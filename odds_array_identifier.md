# Odds Array Identifier Roadmap

## Overview
This document provides unique identifiers for each odds market type array to enable precise modifications and conversions. Each array is assigned a clear ID for easy reference during development.

---

## 🏷️ **ODDS ARRAY IDENTIFIERS**

### **ARRAY_ID: A25** - Asian Handicap (Spread)
- **Field**: 25
- **Market Name**: "spread" 
- **Array Structure**: `[timestamp, period, home_odds, handicap, away_odds, status1, status2, score]`
- **Example**: `[1751024391, "10", 0.97, 0.25, 0.82, 2, 0, "0-0"]`
- **Value Meanings**:
  - `[2]` home_odds = 0.97 (odds for home team)
  - `[3]` handicap = 0.25 (goal handicap: +0.25 for home)
  - `[4]` away_odds = 0.82 (odds for away team)

### **ARRAY_ID: A26** - European 1X2 (MoneyLine)
- **Field**: 26
- **Market Name**: "MoneyLine"
- **Array Structure**: `[timestamp, period, home_odds, draw_odds, away_odds, status1, status2, score]`
- **Example**: `[1751024134, "6", 2.3, 2.87, 3.2, 2, 0, "0-0"]`
- **Value Meanings**:
  - `[2]` home_odds = 2.3 (odds for home win)
  - `[3]` draw_odds = 2.87 (odds for draw)
  - `[4]` away_odds = 3.2 (odds for away win)

### **ARRAY_ID: A27** - Total Goals (Over/Under)
- **Field**: 27
- **Market Name**: "Over/Under"
- **Array Structure**: `[timestamp, period, over_odds, total_line, under_odds, status1, status2, score]`
- **Example**: `[1751024265, "8", 0.85, 1.75, 0.95, 2, 0, "0-0"]`
- **Value Meanings**:
  - `[2]` over_odds = 0.85 (odds for over total goals)
  - `[3]` total_line = 1.75 (goals line threshold)
  - `[4]` under_odds = 0.95 (odds for under total goals)

### **ARRAY_ID: A28** - Corner Kicks (Corners)
- **Field**: 28
- **Market Name**: "Corners"
- **Array Structure**: `[timestamp, period, over_odds, corners_line, under_odds, status1, status2, score]`
- **Example**: `[1751024391, "10", 1.1, 8.5, 0.66, 2, 0, "0-1"]`
- **Value Meanings**:
  - `[2]` over_odds = 1.1 (odds for over total corners)
  - `[3]` corners_line = 8.5 (corners line threshold)
  - `[4]` under_odds = 0.66 (odds for under total corners)

---

## 🎯 **QUICK REFERENCE TABLE**

| Array ID | Field | Market Name | Position [2] | Position [3] | Position [4] |
|----------|-------|-------------|--------------|--------------|--------------|
| **A25** | 25 | spread | home_odds | handicap | away_odds |
| **A26** | 26 | MoneyLine | home_odds | draw_odds | away_odds |
| **A27** | 27 | Over/Under | over_odds | total_line | under_odds |
| **A28** | 28 | Corners | over_odds | corners_line | under_odds |

---

## 🔧 **COMMON ARRAY POSITIONS** 
*(Same across all arrays)*

| Position | Field Name | Data Type | Description |
|----------|------------|-----------|-------------|
| `[0]` | timestamp | integer | Change time (Unix timestamp) |
| `[1]` | period | string | Match time ("" = pre-match, "1"-"90+" = live) |
| `[5]` | status1 | integer | Match status (1=Not Started, 2=Live, 3=Finished) |
| `[6]` | status2 | integer | Sealed disk (0=No, 1=Yes) |
| `[7]` | score | string | Current score ("home-away" format) |

---

## 📝 **USAGE INSTRUCTIONS**

### **To Request Array Modifications:**
1. **Reference by Array ID**: "Modify A25" (instead of "modify asian handicap")
2. **Specify Position**: "Change A25[3] handicap values" 
3. **Target Specific Elements**: "Convert A26[2] home_odds to percentage"

### **Example Requests:**
- ✅ **Good**: "Convert A27[3] total_line to display as 'Over/Under X.X goals'"
- ✅ **Good**: "Transform A25[3] handicap to show '+' or '-' prefix"
- ✅ **Good**: "Format A26 odds as percentages instead of decimals"

### **Modification Patterns:**
- **Value Conversion**: Transform numeric values (odds → percentages)
- **Label Addition**: Add descriptive labels to array values
- **Format Changes**: Modify display format while preserving data
- **Conditional Logic**: Apply different formatting based on array values

---

## 🎯 **ROADMAP FOR FUTURE MODIFICATIONS**

This identifier system enables:
- ✅ **Precise targeting** of specific array types and positions
- ✅ **Clear communication** between developer and user
- ✅ **Systematic modifications** without affecting other arrays
- ✅ **Version control** of array transformation logic
- ✅ **Easy rollback** of specific array changes

---

## 🔒 **IMPORTANT NOTES**

1. **Array Positions [0], [1], [5], [6], [7]** are standard across all markets
2. **Positions [2], [3], [4]** contain market-specific betting values
3. **Source data preservation** - modifications only affect output formatting
4. **Independent processing** - each Array ID can be modified independently

---

*Use this roadmap to specify exactly which odds arrays and positions you want to modify for conversions and formatting changes.*