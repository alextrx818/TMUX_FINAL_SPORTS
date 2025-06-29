# Odds Market Examples - Real Data from Recent Fetch

## Overview
This document contains **real odds arrays** from the most recent pipeline fetch (06/27/2025 09:13 AM). These examples show actual live betting data during match progression, demonstrating the 8-element array structure for each market type.

---

## 🏷️ **A25 - "spread" (Asian Handicap)**

### **Array Structure**: `[timestamp, period, home_odds, handicap, away_odds, status1, status2, score]`

**Example 1 - 10th minute:**
```json
[1751024391, "10", 0.97, 0.25, 0.82, 2, 0, "0-0"]
```
- **[0]** `1751024391` - Timestamp (odds change time)
- **[1]** `"10"` - Match minute (10th minute)
- **[2]** `0.97` - Home team odds
- **[3]** `0.25` - Handicap (+0.25 goals for home team)
- **[4]** `0.82` - Away team odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

**Example 2 - 7th minute:**
```json
[1751024189, "7", 1.0, 0.25, 0.8, 2, 0, "0-0"]
```
- **[0]** `1751024189` - Timestamp (odds change time)
- **[1]** `"7"` - Match minute (7th minute)
- **[2]** `1.0` - Home team odds
- **[3]** `0.25` - Handicap (+0.25 goals for home team)
- **[4]** `0.8` - Away team odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

---

## 🏷️ **A26 - "MoneyLine" (European 1X2)**

### **Array Structure**: `[timestamp, period, home_odds, draw_odds, away_odds, status1, status2, score]`

**Example 1 - 10th minute:**
```json
[1751024387, "10", 2.3, 2.75, 3.4, 2, 0, "0-0"]
```
- **[0]** `1751024387` - Timestamp (odds change time)
- **[1]** `"10"` - Match minute (10th minute)
- **[2]** `2.3` - Home win odds
- **[3]** `2.75` - Draw odds
- **[4]** `3.4` - Away win odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

**Example 2 - 8th minute:**
```json
[1751024265, "8", 2.3, 2.75, 3.25, 2, 0, "0-0"]
```
- **[0]** `1751024265` - Timestamp (odds change time)
- **[1]** `"8"` - Match minute (8th minute)
- **[2]** `2.3` - Home win odds
- **[3]** `2.75` - Draw odds
- **[4]** `3.25` - Away win odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

---

## 🏷️ **A27 - "Over/Under" (Total Goals)**

### **Array Structure**: `[timestamp, period, over_odds, total_line, under_odds, status1, status2, score]`

**Example 1 - 10th minute:**
```json
[1751024387, "10", 0.92, 1.75, 0.87, 2, 0, "0-0"]
```
- **[0]** `1751024387` - Timestamp (odds change time)
- **[1]** `"10"` - Match minute (10th minute)
- **[2]** `0.92` - Over 1.75 goals odds
- **[3]** `1.75` - Total goals line
- **[4]** `0.87` - Under 1.75 goals odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

**Example 2 - 9th minute:**
```json
[1751024332, "9", 0.87, 1.75, 0.92, 2, 0, "0-0"]
```
- **[0]** `1751024332` - Timestamp (odds change time)
- **[1]** `"9"` - Match minute (9th minute)
- **[2]** `0.87` - Over 1.75 goals odds
- **[3]** `1.75` - Total goals line
- **[4]** `0.92` - Under 1.75 goals odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-0"` - Current score

---

## 🏷️ **A28 - "Corners" (Corner Kicks)**

### **Array Structure**: `[timestamp, period, over_odds, corners_line, under_odds, status1, status2, score]`

**Example 1 - 10th minute:**
```json
[1751024391, "10", 1.1, 8.5, 0.66, 2, 0, "0-1"]
```
- **[0]** `1751024391` - Timestamp (odds change time)
- **[1]** `"10"` - Match minute (10th minute)
- **[2]** `1.1` - Over 8.5 corners odds
- **[3]** `8.5` - Total corners line
- **[4]** `0.66` - Under 8.5 corners odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-1"` - Current score

**Example 2 - 9th minute:**
```json
[1751024292, "9", 1.0, 8.5, 0.72, 2, 0, "0-1"]
```
- **[0]** `1751024292` - Timestamp (odds change time)
- **[1]** `"9"` - Match minute (9th minute)
- **[2]** `1.0` - Over 8.5 corners odds
- **[3]** `8.5` - Total corners line
- **[4]** `0.72` - Under 8.5 corners odds
- **[5]** `2` - Match status (Live)
- **[6]** `0` - Sealed disk (No)
- **[7]** `"0-1"` - Current score

---

## 📊 **Data Insights**

### **Match Context**
- **Fetch Time**: June 27, 2025 at 09:13 AM EDT
- **Match Status**: Live match in progress (status code 2)
- **Score Progression**: 0-0 early in match, 0-1 by 9th-10th minute
- **Data Source**: Company ID "2" (likely Bet365)

### **Odds Movement Patterns**
- **Asian Handicap**: Consistent +0.25 handicap for home team
- **MoneyLine**: Home team favored (2.3 odds vs 3.25-3.4 away)
- **Over/Under**: Low-scoring expectations (1.75 goals line)
- **Corners**: Standard line at 8.5 corners total

### **Real-Time Changes**
These examples show **actual odds fluctuations** during live play:
- Odds adjust based on match flow and betting volume
- Timestamps show exact moments of odds changes
- Score updates reflect match progression

### **Array ID Quick Reference**
| Array ID | Market Name | Key Positions | Line Example |
|----------|-------------|---------------|--------------|
| **A25** | spread | [2]=home_odds, [3]=handicap, [4]=away_odds | Home +0.25 goals |
| **A26** | MoneyLine | [2]=home_odds, [3]=draw_odds, [4]=away_odds | 2.3 / 2.75 / 3.4 |
| **A27** | Over/Under | [2]=over_odds, [3]=total_line, [4]=under_odds | 1.75 goals total |
| **A28** | Corners | [2]=over_odds, [3]=corners_line, [4]=under_odds | 8.5 corners total |

---

## 🔧 **Usage for Modifications**

When requesting odds array modifications, reference these examples:
- **"Format A25[3] to show '+0.25' instead of '0.25'"** - Add plus sign to handicap
- **"Convert A26[2,4] to percentages"** - Show implied probabilities
- **"Display A27[3] as 'Over/Under 1.75 goals'"** - Add descriptive text
- **"Transform A28 to show corner range"** - Format as "8-9 corners"

These real examples provide the foundation for understanding current data structure and planning precise modifications to the odds display format.

---

*Reference: /workspaces/TMUX_FINAL_SPORTS/odds_array_identifier.md for complete array documentation*