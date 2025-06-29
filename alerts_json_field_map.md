# Alerts.json Field Map

This document provides a comprehensive field reference for alerts.json to enable precise communication about field modifications and conversions.

## File Structure Overview

```
alerts.json
├── log_metadata (object)
│   ├── total_fetches (integer)
│   ├── first_fetch (ISO timestamp string)
│   ├── last_fetch (ISO timestamp string)
│   └── log_format (string)
└── fetch_history (array)
    └── [fetch_entry] (object)
        ├── fetch_timestamp (ISO timestamp string)
        ├── fetch_number (integer)
        ├── processed_data (object)
        │   ├── matches (array)
        │   │   └── [match] (object) ← **MAIN MATCH DATA**
        │   └── total_matches (integer)
        └── processing_metadata (object)
            ├── source_file (string)
            ├── processing_time (string)
            └── status (string)
```

## Match Object Field Reference

### **A. BASIC IDENTIFIERS**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **A1** | `match_id` | string | Unique match identifier | `"1l4rjnh4vvonm7v"` |
| **A2** | `timestamp` | string | Processing timestamp (readable) | `"06/29/2025 02:08 AM"` |
| **A3** | `scheduled_time_readable` | string | Match scheduled time | `"06/29/2025 05:00 AM"` |

### **B. COMPETITION DATA**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **B1** | `competition` | object | Competition container | `{}` |
| **B1.1** | `competition.name` | string | Competition name | `"Australia National Premier Leagues Capital Football 1"` |

### **C. TEAM DATA**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **C1** | `teams` | object | Teams container | `{}` |
| **C1.1** | `teams.home` | object | Home team container | `{}` |
| **C1.1.1** | `teams.home.name` | string | Home team name | `"Canberra FC"` |
| **C1.2** | `teams.away` | object | Away team container | `{}` |
| **C1.2.1** | `teams.away.name` | string | Away team name | `"Gungahlin United"` |

### **D. SCORING DATA**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **D1** | `home_score_current` | integer | Current home team score | `2` |
| **D2** | `home_score_half` | integer | Home team halftime score | `2` |
| **D3** | `home_corners` | integer | Home team corner kicks | `3` |
| **D4** | `away_score_current` | integer | Current away team score | `1` |
| **D5** | `away_score_half` | integer | Away team halftime score | `0` |
| **D6** | `away_corners` | integer | Away team corner kicks | `1` |
| **D7** | `home_scores` | array | Home score breakdown by period | `[4,2,1,1,5,0,0]` |
| **D8** | `away_scores` | array | Away score breakdown by period | `[5,0,0,4,2,0,0]` |

### **E. MATCH STATUS**
| Field Code | Field Name | Type | Description | Example | Status Reference |
|------------|------------|------|-------------|---------|------------------|
| **E1** | `details_status_id` | integer | Match status ID | `4` | See status_id_key.md |

### **F. BETTING ODDS** 
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **F1** | `odds` | object | Betting odds container | `{}` |
| **F1.X** | `odds."X"` | object | Bookmaker odds (X = bookmaker ID) | `odds."2"` |
| **F1.X.1** | `odds."X".spread` | array | Point spread odds | `[[...], [...]]` |
| **F1.X.2** | `odds."X".MoneyLine` | array | Moneyline odds | `[[...], [...]]` |
| **F1.X.3** | `odds."X"."Over/Under"` | array | Over/Under odds | `[[...], [...]]` |
| **F1.X.4** | `odds."X".Corners` | array | Corner kick betting odds | `[[...], [...]]` |

### **G. ENVIRONMENTAL DATA**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **G1** | `environment` | object | Weather/environmental container | `{}` |
| **G1.1** | `environment.weather` | string | Weather conditions | `"Fair"` |
| **G1.2** | `environment.pressure` | string | Atmospheric pressure | `"769mmHg"` |
| **G1.3** | `environment.temperature` | string | Temperature | `"54°F"` |
| **G1.4** | `environment.wind` | string | Wind conditions | `"11mph (Gentle Breeze)"` |
| **G1.5** | `environment.humidity` | string | Humidity percentage | `"55%"` |

### **H. VAR/INCIDENT DATA**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **H1** | `var_incidents` | array | VAR incident reports | `[{...}, {...}]` |
| **H1.1** | `var_incidents[].type` | integer | Incident type code | `28` |
| **H1.2** | `var_incidents[].position` | integer | Field position | `1` |
| **H1.3** | `var_incidents[].time` | integer | Incident time (minutes) | `19` |
| **H1.4** | `var_incidents[].player_id` | string | Player identifier | `"vjxm8gh8o67xr6o"` |
| **H1.5** | `var_incidents[].player_name` | string | Player name | `"Sheika Scott"` |
| **H1.6** | `var_incidents[].var_reason` | integer | VAR review reason code | `4` |
| **H1.7** | `var_incidents[].var_result` | integer | VAR decision result code | `3` |

### **I. SPECIAL/ANOMALY FIELDS**
| Field Code | Field Name | Type | Description | Example |
|------------|------------|------|-------------|---------|
| **I1** | `""` | string | Empty key field (data anomaly) | `""` |

## Usage Instructions

### **How to Reference Fields in Conversations:**

1. **Use Field Codes for precision**: "Please modify field **D1** (home_score_current)"

2. **Use Full Paths for nested fields**: "Update **C1.1.1** (teams.home.name)"

3. **Reference multiple fields**: "Convert fields **D1**, **D2**, **D4**, **D5** from integers to strings"

4. **Specify array operations**: "Transform **D7** (home_scores) array structure"

### **Common Field Groups:**

- **Basic Match Info**: A1, A2, A3, B1.1
- **Team Data**: C1.1.1, C1.2.1  
- **Current Scores**: D1, D4
- **Historical Scores**: D2, D5, D7, D8
- **Match State**: E1
- **Environmental**: G1.1, G1.2, G1.3, G1.4, G1.5
- **Betting**: F1.X.1, F1.X.2, F1.X.3, F1.X.4
- **VAR/Incidents**: H1, H1.1-H1.7
- **Data Anomalies**: I1

### **Field Modification Examples:**

```
"Convert field D1 (home_score_current) from integer to string"
"Add new field D9 for total_goals calculation" 
"Rename field A2 (timestamp) to processing_timestamp"
"Remove all F1.X.4 (Corners) betting data"
"Transform D7 array into object with period names"
```

---

*Created: 2025-06-29*  
*Purpose: Field reference for alerts.json modifications*  
*File: /workspaces/TMUX_FINAL_SPORTS/alerts_json_field_map.md*