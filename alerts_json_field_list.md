# Alerts.json Field Reference List

**Based on API Schema Documentation + Current Implementation Analysis**  
*Reference: alerts_json_schema.json + live data structure*

## **FIELD REFERENCE LIST**

### **📋 METADATA STRUCTURE**
1. `log_metadata` (object)
2. `log_metadata.total_fetches` (integer)
3. `log_metadata.first_fetch` (ISO timestamp string)
4. `log_metadata.last_fetch` (ISO timestamp string)  
5. `log_metadata.log_format` (string)
6. `fetch_history` (array)
7. `fetch_history[].fetch_timestamp` (ISO timestamp string)
8. `fetch_history[].fetch_number` (integer)
9. `fetch_history[].processed_data` (object)
10. `fetch_history[].processed_data.total_matches` (integer)
11. `fetch_history[].processed_data.matches` (array) ← **MAIN DATA ARRAY**
12. `fetch_history[].processing_metadata` (object)
13. `fetch_history[].processing_metadata.source_file` (string)
14. `fetch_history[].processing_metadata.processing_time` (string)
15. `fetch_history[].processing_metadata.status` (string)

### **🏆 MATCH IDENTIFIERS**
16. `match_id` (string) - Unique match identifier
17. `timestamp` (string) - Processing timestamp (readable format)
18. `scheduled_time_readable` (string) - Match scheduled time

### **🏟️ COMPETITION & TEAMS**
19. `competition` (object)
20. `competition.name` (string) - Competition name
21. `teams` (object)
22. `teams.home` (object)
23. `teams.home.name` (string) - Home team name
24. `teams.away` (object)
25. `teams.away.name` (string) - Away team name

### **⚽ SCORING DATA - CURRENT SCORES**
26. `home_score_current` (integer) - Current home score
27. `home_score_half` (integer) - Home halftime score
28. `home_corners` (integer) - Home team corner kicks
29. `away_score_current` (integer) - Current away score
30. `away_score_half` (integer) - Away halftime score
31. `away_corners` (integer) - Away team corner kicks

### **📊 SCORING DATA - SCORE ARRAYS** ⭐ **ARRAY FIELDS**
32. `home_scores` (array[7]) - Home score breakdown by period
33. `home_scores[0]` (integer) - Period 1 home score
34. `home_scores[1]` (integer) - Period 2 home score
35. `home_scores[2]` (integer) - Period 3 home score (usually 0)
36. `home_scores[3]` (integer) - Period 4 home score (usually 0)
37. `home_scores[4]` (integer) - Period 5 home score (special periods)
38. `home_scores[5]` (integer) - Period 6 home score (usually 0)
39. `home_scores[6]` (integer) - Period 7 home score (usually 0)
40. `away_scores` (array[7]) - Away score breakdown by period
41. `away_scores[0]` (integer) - Period 1 away score
42. `away_scores[1]` (integer) - Period 2 away score  
43. `away_scores[2]` (integer) - Period 3 away score (usually 0)
44. `away_scores[3]` (integer) - Period 4 away score (usually 0)
45. `away_scores[4]` (integer) - Period 5 away score (special periods)
46. `away_scores[5]` (integer) - Period 6 away score (usually 0)
47. `away_scores[6]` (integer) - Period 7 away score (usually 0)

### **📋 MATCH STATUS**
48. `details_status_id` (integer) - Match status ID (see status_id_key.md)

### **💰 BETTING ODDS** ⭐ **NESTED ARRAY STRUCTURE**
49. `odds` (object) - Main betting odds container
50. `odds."X"` (object) - Bookmaker odds (X = bookmaker ID like "2", "3")
51. `odds."X".spread` (array) - Point spread betting odds ⭐ **ARRAY**
52. `odds."X".MoneyLine` (array) - Moneyline betting odds ⭐ **ARRAY**
53. `odds."X"."Over/Under"` (array) - Over/Under betting odds ⭐ **ARRAY**
54. `odds."X".Corners` (array) - Corner kick betting odds ⭐ **ARRAY**

### **🎯 BETTING ODDS ARRAY ELEMENTS** ⭐ **EACH ARRAY[8] STRUCTURE**
**Handicap/Spread Array[8]:**
55. `odds."X".spread[0]` (integer) - Change time
56. `odds."X".spread[1]` (string) - Time of match (empty before start)
57. `odds."X".spread[2]` (float) - Home win odds
58. `odds."X".spread[3]` (float) - Handicap value
59. `odds."X".spread[4]` (float) - Away win odds
60. `odds."X".spread[5]` (integer) - Match status
61. `odds."X".spread[6]` (integer) - Disk sealed (0=No, 1=Yes)
62. `odds."X".spread[7]` (string) - Score (home-away)

**MoneyLine Array[8]:**
63. `odds."X".MoneyLine[0]` (integer) - Change time
64. `odds."X".MoneyLine[1]` (string) - Time of match
65. `odds."X".MoneyLine[2]` (float) - Home win odds
66. `odds."X".MoneyLine[3]` (float) - Draw odds
67. `odds."X".MoneyLine[4]` (float) - Away win odds
68. `odds."X".MoneyLine[5]` (integer) - Match status
69. `odds."X".MoneyLine[6]` (integer) - Disk sealed
70. `odds."X".MoneyLine[7]` (string) - Score

**Over/Under Array[8]:**
71. `odds."X"."Over/Under"[0]` (integer) - Change time
72. `odds."X"."Over/Under"[1]` (string) - Time of match
73. `odds."X"."Over/Under"[2]` (float) - Over odds
74. `odds."X"."Over/Under"[3]` (float) - Handicap value
75. `odds."X"."Over/Under"[4]` (float) - Under odds
76. `odds."X"."Over/Under"[5]` (integer) - Match status
77. `odds."X"."Over/Under"[6]` (integer) - Disk sealed
78. `odds."X"."Over/Under"[7]` (string) - Score

**Corners Array[8]:**
79. `odds."X".Corners[0]` (integer) - Change time
80. `odds."X".Corners[1]` (string) - Time of match
81. `odds."X".Corners[2]` (float) - Over odds
82. `odds."X".Corners[3]` (float) - Handicap value
83. `odds."X".Corners[4]` (float) - Under odds
84. `odds."X".Corners[5]` (integer) - Match status
85. `odds."X".Corners[6]` (integer) - Disk sealed
86. `odds."X".Corners[7]` (string) - Corner ratio (home-away)

### **🎬 VAR/INCIDENT DATA** ⭐ **ARRAY FIELD**
87. `var_incidents` (array) - VAR incident reports ⭐ **ARRAY**
88. `var_incidents[].type` (integer) - Incident type code
89. `var_incidents[].position` (integer) - Field position
90. `var_incidents[].time` (integer) - Incident time (minutes)
91. `var_incidents[].player_id` (string) - Player identifier
92. `var_incidents[].player_name` (string) - Player name
93. `var_incidents[].var_reason` (integer) - VAR review reason (see schema)
94. `var_incidents[].var_result` (integer) - VAR decision result (see schema)

### **🌤️ ENVIRONMENTAL DATA**
95. `environment` (object) - Weather/environmental container
96. `environment.weather` (string) - Weather conditions
97. `environment.pressure` (string) - Atmospheric pressure
98. `environment.temperature` (string) - Temperature
99. `environment.wind` (string) - Wind conditions  
100. `environment.humidity` (string) - Humidity percentage

### **⚠️ DATA ANOMALIES**
101. `""` (string) - Empty key field (data anomaly)

---

## **🎯 QUICK REFERENCE - ARRAY FIELDS**

**All Array Fields for Quick Reference:**
- **fetch_history** (main log array)
- **matches** (main match data array)
- **home_scores[7]** (score breakdown)
- **away_scores[7]** (score breakdown)
- **odds."X".spread[8]** (betting array)
- **odds."X".MoneyLine[8]** (betting array)
- **odds."X"."Over/Under"[8]** (betting array) 
- **odds."X".Corners[8]** (betting array)
- **var_incidents[]** (incident reports)

## **💬 USAGE EXAMPLES**

```
"Update field #26 (home_score_current) from integer to string"
"Convert array #32 (home_scores) to object with period names"
"Remove all betting arrays #51-54 (odds spread/moneyline/over-under/corners)"
"Transform field #48 (details_status_id) validation using status_id_key.md"
"Add new field after #25 for team logos"
"Modify array #87 (var_incidents) structure"
```

---

*Created: 2025-06-29*  
*Based on: API schema + live alerts.json analysis*  
*Total Fields: 101 mapped fields*  
*Array Fields: 9 identified arrays*