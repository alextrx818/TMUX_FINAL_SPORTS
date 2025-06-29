# Filter File System Documentation

## Overview

This document provides a comprehensive breakdown of the **filtering logic** and **file system architecture** used in the TMUX_FINAL_SPORTS sports data pipeline. The system employs sophisticated filtering mechanisms across multiple stages to transform raw API data into clean, user-friendly outputs.

## Pipeline Architecture

```
📡 API Sources → 🔄 Processing Stages → 📊 Filtered Outputs → 💾 Logging System
```

### Complete Data Flow
```
live.py → details.py + odds.py (parallel) → teams.py + competitions.py + countries.py → merge.py → pretty_print.py → pretty_conversion.py → monitoring.py
```

## Data Sources & Input Points

### 1. **live.py** - Entry Point
- **API Source**: `https://api.thesports.com/v1/football/match/detail_live`
- **Input Type**: Live match data (global endpoint)
- **Dependencies**: None
- **Authentication**: Environment variables (`THESPORTS_USER`, `THESPORTS_SECRET`)

### 2. **details.py** - Match Details
- **API Source**: `https://api.thesports.com/v1/football/match/recent/list`
- **Input Type**: Match IDs from live.py
- **Dependencies**: `/tmp/live_matches.json`
- **Purpose**: Detailed match information and ID extraction

### 3. **odds.py** - Betting Data
- **API Source**: `https://api.thesports.com/v1/football/odds/history`
- **Input Type**: Match IDs from live.py
- **Dependencies**: `/tmp/live_matches.json`
- **Purpose**: Historical betting odds with time filtering

### 4. **Reference Data Sources**
- **teams.py**: `https://api.thesports.com/v1/football/team/additional/list`
- **competitions.py**: `https://api.thesports.com/v1/football/competition/additional/list`
- **countries.py**: `https://api.thesports.com/v1/football/country/list`

## Filtering Mechanisms

### 🕐 Time-Based Filtering (odds.py)

**Purpose**: Capture only early match betting data for pre-game analysis

```python
# Filter Logic: Lines 164-173 in odds.py
if minute_str == "" or (minute_str.isdigit() and int(minute_str) <= 10):
    filtered_odds.append(odds_entry)  # ✅ KEEP
else:
    # ❌ DISCARD odds after 10th minute
```

**Criteria**:
- ✅ **KEEP**: Pregame odds (`minute == ""`)
- ✅ **KEEP**: Minutes 1-10 (`int(minute) <= 10`)
- ❌ **REMOVE**: All odds after 10th minute

**Impact**: Reduces odds data volume by ~80-90%

### 🎯 Content-Based Filtering (merge.py)

**Purpose**: Remove non-essential data while preserving critical information

```python
# Major Content Filters: Lines 296-312 in merge.py
```

#### ❌ **Filtered Out**:
- **stats[]** arrays (possession %, shots, passes, tackles, etc.)
- **incidents[]** except VAR decisions (goals, cards, substitutions)
- **tlive[]** live commentary arrays
- Technical metadata and internal processing data

#### ✅ **Preserved**:
- **VAR incidents** (type: 28) - Video Assistant Referee decisions
- **Score arrays** - 7-element arrays: `[goals, halftime, red_cards, yellow_cards, corners, overtime, penalties]`
- **Team information** - Names, logos, countries
- **Competition data** - League names, current seasons
- **Environment data** - Weather, temperature, pressure, wind, humidity
- **Early odds data** - Filtered betting information from odds.py

### 💾 Cache-Based Optimization

**Purpose**: Minimize API calls through intelligent caching

```python
# Cache Logic: 24-hour duration with staleness detection
if cache_is_fresh:
    stale_items = get_stale_items(items, cache)
    # Only fetch stale/missing items
else:
    # Fetch all items (cache expired)
```

**Cache Locations**:
- `/cache/teams/teams_cache.json`
- `/cache/competitions/competitions_cache.json`
- `/cache/countries/countries_cache.json`

**Cache Metadata**:
```json
{
  "cache_metadata": {
    "created_at": "ISO timestamp",
    "last_updated": "ISO timestamp", 
    "cache_version": "1.0",
    "total_items": 777,
    "cache_duration_hours": 24
  }
}
```

## File System Architecture

### 📁 Directory Structure

```
/workspaces/TMUX_FINAL_SPORTS/
├── 📊 logs/                          # Primary logging system
│   ├── live/live.json               # Accumulating live match data (100-fetch rotation)
│   ├── details/details.json         # Match details with timestamps
│   ├── odds/odds.json               # Filtered early betting odds
│   ├── merge/merge.json             # Combined & filtered comprehensive data
│   ├── pretty_print/pretty_print.json    # User-friendly essential fields
│   ├── pretty_conversion/pretty_conversion.json  # American odds format
│   └── monitoring/monitoring.json   # Final validation & monitoring
├── 💾 cache/                         # Smart caching system
│   ├── teams/teams_cache.json       # Team data (24hr TTL)
│   ├── competitions/competitions_cache.json  # Competition data (24hr TTL)
│   └── countries/countries_cache.json     # Country lookup table (24hr TTL)
└── 🔄 /tmp/                          # Inter-stage communication
    ├── live_matches.json            # Match IDs for pipeline propagation
    ├── team_ids.json                # Extracted team identifiers
    ├── competition_ids.json         # Extracted competition identifiers
    └── match_details.json           # Processed match information
```

### 📝 Logging Formats

#### **Accumulating Logs** (live.json)
```json
{
  "log_metadata": {
    "total_fetches": 100,
    "first_fetch": "06/27/2025 07:59:32 PM EST",
    "last_fetch": "06/27/2025 09:38:33 PM EST",
    "log_format": "accumulating_v1.0"
  },
  "fetch_history": [
    {
      "fetch_id": "20250627_195932",
      "api_response": { /* Full API response */ },
      "fetch_timestamp": "06/27/2025 07:59:32 PM EST",
      "match_count": 83
    }
  ]
}
```

#### **Single-Fetch Logs** (details.json, odds.json)
```json
{
  "api_response": [ /* Processed data */ ],
  "fetch_timestamp": "06/28/2025 08:50:42 PM EST",
  "footer_completion": "--- Details.py fetch completed: 06/28/2025 08:50:42 PM EST ---"
}
```

#### **Cache Structure** (teams_cache.json)
```json
{
  "cache_metadata": { /* Cache info */ },
  "teams": {
    "team_id_123": {
      "data": { /* Team information */ },
      "fetched_at": "2025-06-28T01:22:34.551763",
      "api_updated_at": 1749614205
    }
  }
}
```

## Performance Optimizations

### 🚀 **Concurrent Processing**
- **Semaphore Limits**: 15-30 concurrent API requests
- **Parallel Stages**: details.py + odds.py run simultaneously
- **Cache Optimization**: Only fetch stale/missing data

### 📈 **Data Volume Reduction**

| Stage | Data Volume | Reduction Technique |
|-------|-------------|-------------------|
| **Raw API** | 100% | None (complete data capture) |
| **Odds Filtering** | ~20% | Time-based filter (≤10 minutes) |
| **Content Filtering** | ~40% | Remove stats/incidents/commentary |
| **Pretty Print** | ~15% | Essential fields only |
| **Final Output** | ~10% | Clean, user-friendly format |

### ⏱️ **Timing Controls**
- **Minimum Fetch Interval**: 60 seconds between pipeline runs
- **Cache Duration**: 24 hours for reference data
- **Log Rotation**: 100-fetch history maintained

## Error Handling & Recovery

### 🛡️ **Resilience Mechanisms**
- **Independent Logging**: Each stage maintains separate logs
- **Cache Fallback**: Use cached data if API fails
- **Graceful Degradation**: Missing data doesn't break pipeline
- **Error Isolation**: Failed requests return empty objects

### 📊 **Monitoring & Validation**
- **monitoring.py**: Final data validation stage
- **Cache Hit Metrics**: Track API call efficiency
- **Processing Time**: Pipeline duration monitoring
- **Data Quality**: Field extraction verification

## API Schema References

### 🏈 **Score Array Structure** (7 elements)
```
[0] Score (regular time)              - Integer
[1] Halftime score                    - Integer  
[2] Red cards                         - Integer
[3] Yellow cards                      - Integer
[4] Corners (-1 = no data)           - Integer
[5] Overtime score (120 min total)   - Integer
[6] Penalty shootout score           - Integer
```

### 🎰 **Odds Array Structure** (8 elements)
```
[0] Change timestamp                  - Integer
[1] Match minute                      - String
[2] Primary odds value               - Float
[3] Handicap/Total line              - Float  
[4] Secondary odds value             - Float
[5] Match status                     - Integer
[6] Sealed disk flag                 - Integer
[7] Current score                    - String
```

### 🚨 **VAR Incident Fields**
```
type: 28 (VAR Decision identifier)
position: Field position
time: Incident minute
player_id: Player identifier
player_name: Player name
var_reason: Why VAR was triggered (1-7, 0=other)
var_result: VAR decision outcome (1-10, 0=unknown)
```

## Usage Examples

### 🔍 **Monitor Filtering Status**
```bash
# Check current pipeline status
./background_runner.sh status

# View recent logs to see filtering in action
./background_runner.sh logs

# Monitor specific log files
tail -f /workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json
```

### 📊 **Cache Performance**
```bash
# View cache hit ratios in logs
grep "Cache hits" /workspaces/TMUX_FINAL_SPORTS/pipeline_background.log

# Check cache freshness
cat /workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json | jq '.cache_metadata'
```

### 🎯 **Data Analysis**
```bash
# Count matches in final output
cat /workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json | jq '.pretty_print_metadata.total_matches'

# View VAR incidents
cat /workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json | jq '.matches[] | select(.var_incidents) | .var_incidents'
```

## Future Enhancements

### 🔮 **Planned Features**
- **Advanced Filtering**: Custom time ranges for odds data
- **Data Sorting**: Match importance and status-based prioritization
- **Analytics Pipeline**: Statistical analysis of filtered data
- **Real-time Alerts**: Notification system for VAR decisions
- **API Rate Limiting**: Enhanced throttling mechanisms

---

**Generated**: 06/29/2025 12:55 AM EST  
**Version**: 1.0  
**Maintainer**: TMUX_FINAL_SPORTS Pipeline System