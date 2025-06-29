# Monitoring.json Field Roadmap & Reference Key

## Complete JSON Structure Map

This document provides a field-by-field roadmap for **monitoring.json** to enable precise editing and parsing. Every field, array, and nested structure is catalogued for exact reference.

---

## 🏗️ **Root Level Structure**

```json
{
  "pretty_print_metadata": { },
  "matches": [ ],
  "footer_completion": ""
}
```

---

## 📊 **pretty_print_metadata** Object

```json
"pretty_print_metadata": {
  "generated_at": "",                    // ISO timestamp string
  "generated_at_readable": "",           // Human readable timestamp
  "total_matches": 0,                    // Integer count
  "source_file": "",                     // Source filename string
  "version": ""                          // Version string
}
```

**Field References**:
- `pretty_print_metadata.generated_at`
- `pretty_print_metadata.generated_at_readable` 
- `pretty_print_metadata.total_matches`
- `pretty_print_metadata.source_file`
- `pretty_print_metadata.version`

---

## ⚽ **matches[]** Array Structure

Each match object in the `matches[]` array contains:

### **Core Match Fields**
```json
{
  "match_id": "",                        // Unique match identifier string
  "timestamp": "",                       // Processing timestamp string  
  "scheduled_time_readable": "",         // Match start time string
  "details_status_id": 0                 // Match status integer (2=live, 3=finished, etc.)
}
```

**Field References**:
- `matches[].match_id`
- `matches[].timestamp`
- `matches[].scheduled_time_readable`
- `matches[].details_status_id`

### **competition** Object
```json
"competition": {
  "name": ""                            // Competition/league name string
}
```

**Field References**:
- `matches[].competition`
- `matches[].competition.name`

### **teams** Object
```json
"teams": {
  "home": {
    "name": ""                          // Home team name string
  },
  "away": {
    "name": ""                          // Away team name string  
  }
}
```

**Field References**:
- `matches[].teams`
- `matches[].teams.home`
- `matches[].teams.home.name`
- `matches[].teams.away`
- `matches[].teams.away.name`

### **Score Arrays** (7-Element Arrays)

```json
"home_scores": [                        // Array[7] of integers
  0,  // [0] Goals (regular time)
  0,  // [1] Halftime score
  0,  // [2] Red cards
  0,  // [3] Yellow cards  
  0,  // [4] Corners (-1 = no data)
  0,  // [5] Overtime score (120min total)
  0   // [6] Penalty shootout score
],
"away_scores": [                        // Array[7] of integers - same structure
  0,  // [0] Goals (regular time)
  0,  // [1] Halftime score
  0,  // [2] Red cards
  0,  // [3] Yellow cards
  0,  // [4] Corners (-1 = no data)  
  0,  // [5] Overtime score (120min total)
  0   // [6] Penalty shootout score
]
```

**Field References**:
- `matches[].home_scores` (full array)
- `matches[].home_scores[0]` (goals)
- `matches[].home_scores[1]` (halftime)
- `matches[].home_scores[2]` (red cards) ⚠️
- `matches[].home_scores[3]` (yellow cards)
- `matches[].home_scores[4]` (corners)
- `matches[].home_scores[5]` (overtime)
- `matches[].home_scores[6]` (penalties)
- `matches[].away_scores` (full array)
- `matches[].away_scores[0]` (goals)
- `matches[].away_scores[1]` (halftime)
- `matches[].away_scores[2]` (red cards) ⚠️
- `matches[].away_scores[3]` (yellow cards)
- `matches[].away_scores[4]` (corners)
- `matches[].away_scores[5]` (overtime)
- `matches[].away_scores[6]` (penalties)

### **var_incidents[]** Array (Optional Field)

```json
"var_incidents": [                      // Array of VAR incident objects
  {
    "type": 0,                          // Integer - incident type (28 = VAR)
    "position": 0,                      // Integer - field position
    "time": 0,                          // Integer - minute of incident
    "player_id": "",                    // String - player identifier
    "player_name": "",                  // String - player name
    "var_reason": 0,                    // Integer - why VAR triggered (1-7, 0=other)
    "var_result": 0                     // Integer - VAR decision (1-10, 0=unknown)
  }
]
```

**Field References**:
- `matches[].var_incidents` (full array)
- `matches[].var_incidents[].type`
- `matches[].var_incidents[].position`
- `matches[].var_incidents[].time`
- `matches[].var_incidents[].player_id`
- `matches[].var_incidents[].player_name`
- `matches[].var_incidents[].var_reason`
- `matches[].var_incidents[].var_result`

### **odds** Object (Optional Field)

```json
"odds": {
  "2": {                                // Company ID (string key) - "2" = Bet365
    "spread": [ ],                      // Asian Handicap odds array
    "MoneyLine": [ ],                   // 1X2 odds array
    "Over/Under": [ ],                  // Total goals odds array
    "Corners": [ ]                      // Corner kicks odds array
  }
}
```

**Field References**:
- `matches[].odds`
- `matches[].odds["2"]` (Bet365 company)
- `matches[].odds["2"].spread`
- `matches[].odds["2"].MoneyLine`
- `matches[].odds["2"]["Over/Under"]`
- `matches[].odds["2"].Corners`

### **Odds Arrays Structure** (8-Element Arrays)

Each odds type contains arrays with this structure:
```json
[
  1751157838,  // [0] Timestamp (integer)
  "4",         // [1] Match minute (string)
  "-129",      // [2] Primary odds (American format string)
  0.75,        // [3] Handicap/Total line (float)
  "+102",      // [4] Secondary odds (American format string)
  2,           // [5] Match status (integer)
  0,           // [6] Sealed disk flag (integer)
  "0-0"        // [7] Current score (string)
]
```

**Field References**:
- `matches[].odds["2"].spread[0][0]` (timestamp)
- `matches[].odds["2"].spread[0][1]` (minute)
- `matches[].odds["2"].spread[0][2]` (primary odds)
- `matches[].odds["2"].spread[0][3]` (handicap line)
- `matches[].odds["2"].spread[0][4]` (secondary odds)
- `matches[].odds["2"].spread[0][5]` (status)
- `matches[].odds["2"].spread[0][6]` (sealed flag)
- `matches[].odds["2"].spread[0][7]` (score)

### **environment** Object (Optional Field)

```json
"environment": {
  "weather": "",                        // Weather description string
  "pressure": "",                       // Air pressure string (e.g., "763mmHg")
  "temperature": "",                    // Temperature string (e.g., "86°F")
  "wind": "",                          // Wind description string (e.g., "4mph (Light Breeze)")
  "humidity": ""                       // Humidity percentage string (e.g., "66%")
}
```

**Field References**:
- `matches[].environment`
- `matches[].environment.weather`
- `matches[].environment.pressure`
- `matches[].environment.temperature`
- `matches[].environment.wind`
- `matches[].environment.humidity`

---

## 🎯 **Quick Reference Examples**

### **Removing Red Cards from Score Arrays**:
- **Target Fields**: `matches[].home_scores[2]` and `matches[].away_scores[2]`
- **Action**: Remove index [2] from both score arrays
- **Result**: Arrays become 6-element instead of 7-element

### **Removing All Betting Odds**:
- **Target Field**: `matches[].odds`
- **Action**: Remove entire odds object
- **Result**: Match has no betting data

### **Keeping Only Goals and Halftime Scores**:
- **Target Fields**: `matches[].home_scores[0,1]` and `matches[].away_scores[0,1]`
- **Action**: Create new 2-element arrays with only positions [0] and [1]
- **Result**: `[goals, halftime]` arrays only

### **Removing VAR Incidents**:
- **Target Field**: `matches[].var_incidents`
- **Action**: Remove entire var_incidents array
- **Result**: No VAR data in output

### **Removing Environment Data**:
- **Target Field**: `matches[].environment`
- **Action**: Remove entire environment object
- **Result**: No weather/temperature data

---

## 📋 **Field Categories for Easy Reference**

### **🔧 Core Fields** (Always Present)
- `match_id`, `timestamp`, `scheduled_time_readable`, `details_status_id`
- `competition.name`
- `teams.home.name`, `teams.away.name` 
- `home_scores[]`, `away_scores[]`

### **🎰 Optional Fields** (May Be Present)
- `var_incidents[]`
- `odds{}`
- `environment{}`

### **📊 Array Fields**
- `matches[]` (root level)
- `home_scores[]` (7 elements)
- `away_scores[]` (7 elements)
- `var_incidents[]` (variable length)
- `odds["2"].spread[]` (8-element sub-arrays)
- `odds["2"].MoneyLine[]` (8-element sub-arrays)
- `odds["2"]["Over/Under"][]` (8-element sub-arrays)
- `odds["2"].Corners[]` (8-element sub-arrays)

### **🏢 Object Fields**
- `pretty_print_metadata{}`
- `competition{}`
- `teams{}`
- `teams.home{}`
- `teams.away{}`
- `odds{}`
- `odds["2"]{}`
- `environment{}`

---

## ⚡ **Common Editing Patterns**

### **Array Element Removal**:
```
Original: [goals, halftime, red, yellow, corners, overtime, penalties]
Remove red cards (index 2): [goals, halftime, yellow, corners, overtime, penalties]
```

### **Object Field Removal**:
```
Original: {..., "odds": {...}, "environment": {...}}
Remove odds: {..., "environment": {...}}
```

### **Nested Array Access**:
```
Path: matches[0].odds["2"].spread[0][3]
Meaning: First match → Bet365 odds → Spread betting → First odds entry → Handicap line
```

---

**Generated**: 06/29/2025 01:00 AM EST  
**Version**: 1.0  
**Purpose**: Field-level editing reference for monitoring.json structure