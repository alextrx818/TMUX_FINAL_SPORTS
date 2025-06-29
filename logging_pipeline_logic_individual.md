# TMUX_FINAL_SPORTS Pipeline - Individual File Data Source & Output Logic

## Overview

This document details the **data source**, **reading mechanism**, and **output logic** for each file in the TMUX_FINAL_SPORTS pipeline. Each stage has a specific input source and output purpose in the data transformation pipeline.

---

## 📊 **PIPELINE FLOW DIAGRAM**

```
API Entry → Data Enrichment → Reference Caching → Data Consolidation → Data Refinement
    ↓              ↓                  ↓                  ↓               ↓
  live.py    details.py+odds.py   teams/competitions   merge.py    pretty_print.py
                                   /countries.py                        ↓
                                                                 pretty_conversion.py
                                                                        ↓
                                                                  monitoring.py
```

---

## 🔍 **INDIVIDUAL FILE ANALYSIS**

### **1. live.py** - Pipeline Entry Point
**📥 Data Source:**
- **API Call**: `https://api.thesports.com/v1/football/match/detail_live`
- **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
- **Authentication**: Environment variables `THESPORTS_USER` and `THESPORTS_SECRET`
- **Parameters**: user, secret
- **Response Processing**: `await response.json()`

**📤 Output Logic:**
- **Format**: Accumulating log with history preservation
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json`
- **Unique Feature**: Maintains history of up to 100 fetches with rotation
- **Structure**: Complex nested JSON with metadata wrapper and fetch history
- **Dependencies Created**: Creates `/tmp/live_matches.json` for downstream processes

**🔄 Pipeline Role**: Entry point that initiates entire pipeline

---

### **2. details.py** - Match Details Fetcher
**📥 Data Source:**
- **File Input**: `/tmp/live_matches.json` (created by live.py)
  - **Method**: `json.load(f)`
  - **Purpose**: Extracts match IDs from live data
- **API Call**: `https://api.thesports.com/v1/football/match/recent/list`
  - **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
  - **Parameters**: user, secret, uuid (match_id from live data)
  - **Response Processing**: `await response.json()`

**📤 Output Logic:**
- **Format**: Single-fetch overwrite system
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json`
- **Structure**: Simple JSON wrapper with timestamp footer
- **Dependencies Created**: Extracts team/competition IDs for caching stages

**🔄 Pipeline Role**: Enriches live match data with detailed information

---

### **3. odds.py** - Betting Odds Fetcher
**📥 Data Source:**
- **File Input**: `/tmp/live_matches.json` (created by live.py)
  - **Method**: `json.load(f)`
  - **Purpose**: Extracts match IDs from live data
- **API Call**: `https://api.thesports.com/v1/football/odds/history`
  - **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
  - **Parameters**: user, secret, uuid (match_id from live data)
  - **Response Processing**: `await response.json()`

**📤 Output Logic:**
- **Format**: Single-fetch overwrite with structured metadata
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json`
- **Structure**: Metadata wrapper with dual timestamp formats
- **Data Filtering**: Only keeps odds from pregame through minute 10

**🔄 Pipeline Role**: Provides early betting odds data for analysis

---

### **4. teams.py** - Team Information Fetcher
**📥 Data Source:**
- **File Input**: `/tmp/team_ids.json` (created by details.py)
  - **Method**: `json.load(f)`
  - **Purpose**: Gets list of team IDs to fetch
- **Cache Input**: `/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Smart caching to avoid redundant API calls
- **API Call**: `https://api.thesports.com/v1/football/team/additional/list` (only for uncached teams)
  - **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
  - **Parameters**: user, secret, uuid (team_id)

**📤 Output Logic:**
- **Format**: Smart caching system with 24-hour TTL
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json`
- **Structure**: Cache metadata with individual item staleness tracking
- **Optimization**: Only fetches stale/missing data, not full replacement

**🔄 Pipeline Role**: Provides team name/information lookups

---

### **5. competitions.py** - Competition Information Fetcher
**📥 Data Source:**
- **File Input**: `/tmp/competition_ids.json` (created by details.py)
  - **Method**: `json.load(f)`
  - **Purpose**: Gets list of competition IDs to fetch
- **Cache Input**: `/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Smart caching to avoid redundant API calls
- **API Call**: `https://api.thesports.com/v1/football/competition/additional/list` (only for uncached competitions)
  - **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
  - **Parameters**: user, secret, uuid (competition_id)

**📤 Output Logic:**
- **Format**: Smart caching system with 24-hour TTL (identical to teams.py)
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json`
- **Structure**: Cache metadata with individual item staleness tracking
- **Optimization**: Only fetches stale/missing data, not full replacement

**🔄 Pipeline Role**: Provides league/competition name lookups

---

### **6. countries.py** - Countries Information Fetcher
**📥 Data Source:**
- **Cache Input**: `/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Smart caching to avoid redundant API calls
- **API Call**: `https://api.thesports.com/v1/football/country/list` (only if cache is stale)
  - **Method**: `aiohttp.ClientSession().get()` (async HTTP request)
  - **Parameters**: user, secret (no UUID needed - global endpoint)

**📤 Output Logic:**
- **Format**: Smart caching system with 24-hour TTL (identical to teams.py/competitions.py)
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json`
- **Structure**: Cache metadata with global country list
- **Global Endpoint**: No input IDs required, fetches all countries

**🔄 Pipeline Role**: Provides country name lookups

---

### **7. merge.py** - Data Merger & Consolidator
**📥 Data Source (Multiple Files):**
- **Live Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json`
  - **Method**: `json.load(f)`
- **Details Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json`
  - **Method**: `json.load(f)`
- **Odds Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json`
  - **Method**: `json.load(f)`
- **Teams Cache**: `/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json`
  - **Method**: `json.load(f)`
- **Competitions Cache**: `/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json`
  - **Method**: `json.load(f)`
- **Countries Cache**: `/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json`
  - **Method**: `json.load(f)`

**📤 Output Logic:**
- **Format**: Single comprehensive output with extensive metadata
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json`
- **Structure**: Pipeline performance tracking + comprehensive data sources count
- **Features**: Cross-referencing, data enrichment, pipeline timing

**🔄 Pipeline Role**: Combines all previous outputs into unified comprehensive data structure

---

### **8. pretty_print.py** - Data Formatter & Filter
**📥 Data Source:**
- **Merge Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Loads comprehensive merged data for filtering

**📤 Output Logic:**
- **Format**: Single filtered output with minimal metadata
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json`
- **Structure**: Data transformation focus with source file tracking
- **Purpose**: Removes unwanted fields, keeps essentials only

**🔄 Pipeline Role**: Filters comprehensive data into clean, essential-only output

---

### **9. pretty_conversion.py** - Field Converter & Transformer
**📥 Data Source:**
- **Pretty Print Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Independent field extraction and conversion

**📤 Output Logic:**
- **Format**: Independent processing with identical structure preservation
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json`
- **Structure**: Advanced conversions with dual timestamp formats
- **Key Features**: 
  - Hong Kong → American odds conversion
  - European → American odds conversion
  - Celsius → Fahrenheit temperature conversion
  - m/s → mph wind speed conversion with Beaufort scale
  - Weather codes → natural language conversion

**🔄 Pipeline Role**: Converts data to user-friendly American/Imperial formats

---

### **10. monitoring.py** - Terminal Field Processor
**📥 Data Source:**
- **Pretty Conversion Data**: `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json`
  - **Method**: `json.load(f)`
  - **Purpose**: Final independent field extraction

**📤 Output Logic:**
- **Format**: Independent terminal processing with field decomposition
- **File Path**: `/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json`
- **Structure**: Field type conversion and validation
- **Key Features**:
  - Score array decomposition (7-element arrays → individual named fields)
  - Individual field extraction: `home_score_current`, `home_score_half`, `home_corners`
  - Visual spacing between home/away score groups
  - Terminal stage (no next stage calls)

**🔄 Pipeline Role**: Final processing stage with score field decomposition for readability

---

## 📋 **SUMMARY OF READING MECHANISMS**

### **API Endpoints (6 files make API calls):**
1. **live.py** → `/match/detail_live`
2. **details.py** → `/match/recent/list`
3. **odds.py** → `/odds/history`
4. **teams.py** → `/team/additional/list`
5. **competitions.py** → `/competition/additional/list`
6. **countries.py** → `/country/list`

### **File Dependencies Chain:**
```
live.py → /tmp/live_matches.json → details.py + odds.py
       ↓
details.py → /tmp/team_ids.json + /tmp/competition_ids.json → teams.py + competitions.py
       ↓
All sources → merge.py → pretty_print.py → pretty_conversion.py → monitoring.py
```

### **Cache System (Smart 24-hour TTL):**
- **teams_cache.json** - Individual team staleness tracking
- **competitions_cache.json** - Individual competition staleness tracking  
- **countries_cache.json** - Global country list staleness tracking

### **Reading Methods Used:**
- **API Calls**: `aiohttp.ClientSession().get()` (async)
- **JSON Files**: `json.load(f)` (synchronous)
- **Authentication**: Environment variables for all API calls
- **Error Handling**: Try/catch blocks with fallback behavior

---

## 🎯 **KEY INSIGHTS**

1. **Data Entry**: live.py is the sole API entry point that initiates the pipeline
2. **Smart Caching**: teams.py, competitions.py, countries.py use identical smart caching to minimize API calls
3. **Data Enrichment**: details.py + odds.py run in parallel to enrich live data
4. **Data Flow**: Each stage reads from specific previous stage outputs - no arbitrary file access
5. **Terminal Processing**: monitoring.py is the final stage with score field decomposition
6. **Error Resilience**: Each stage has fallback behavior if input files are missing
7. **Pipeline Efficiency**: Smart caching reduces API calls by ~80-90% for reference data

This pipeline demonstrates a well-structured data transformation architecture where each stage has a clear input source, processing purpose, and output format optimized for the next stage's requirements.

---

**Generated**: 06/29/2025 01:48 AM EST  
**Version**: 1.0  
**Purpose**: Individual file data source and output logic documentation