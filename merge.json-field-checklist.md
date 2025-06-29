# merge.json Field Checklist for pretty_print.py

> **Purpose**: This checklist serves as a roadmap for communicating and identifying JSON fields between user and AI for the future `pretty_print.py` implementation. Check/uncheck fields to specify which data should be included in the pretty print output.

---

## 📋 **TOP-LEVEL METADATA FIELDS**

**File-level metadata and summary information:**

- [ ] `merge_metadata` - Pipeline execution metadata
  - [ ] `timestamp` - ISO timestamp of merge execution
  - [ ] `total_matches` - Total number of matches processed
  - [ ] `data_sources` - Source availability counts
    - [ ] `live_matches` - Number of matches with live data
    - [ ] `details_matches` - Number of matches with details data  
    - [ ] `odds_matches` - Number of matches with odds data
    - [ ] `teams_cached` - Number of teams in cache
    - [ ] `competitions_cached` - Number of competitions in cache
    - [ ] `countries_cached` - Number of countries in cache
  - [ ] `merge_version` - Version of merge process
  - [ ] `pipeline_duration_seconds` - Total processing time
  - [ ] `completion_timestamp_nyc` - Human-readable NYC completion time
  - [ ] `in_play_matches` - Number of currently live/in-play matches

- [ ] `footer_completion` - Pipeline completion message
- [ ] `in_play_summary` - In-play matches summary text

---

## 🏈 **INDIVIDUAL MATCH FIELDS**

**Core match identification:**

- [ ] `match_id` - Unique match identifier
- [ ] `timestamp` - Match processing timestamp

**Data source tracking:**

- [ ] `data_sources` - Which data sources contributed to this match
  - [ ] `live` - Has live data (boolean)
  - [ ] `details` - Has details data (boolean)
  - [ ] `odds` - Has odds data (boolean)
  - [ ] `teams_cache` - Teams resolved from cache (boolean)
  - [ ] `competitions_cache` - Competition resolved from cache (boolean)
  - [ ] `countries_cache` - Countries resolved from cache (boolean)

**Match scheduling & venue:**

- [ ] `scheduled_time` - Unix timestamp of scheduled start
- [ ] `scheduled_time_readable` - Human-readable scheduled start time
- [ ] `venue_id` - Venue identifier
- [ ] `referee_id` - Referee identifier
- [ ] `neutral_venue` - Is this a neutral venue match (boolean)
- [ ] `season_id` - Season identifier

**Match context & metadata:**

- [ ] `environment` - Weather and field conditions
  - [ ] `weather` - Weather condition code (integer)
  - [ ] `pressure` - Atmospheric pressure (string with unit)
  - [ ] `temperature` - Temperature (string with unit)
  - [ ] `wind` - Wind speed (string with unit)
  - [ ] `humidity` - Humidity percentage (string with %)

- [ ] `round_info` - Tournament/league round information
  - [ ] `stage_id` - Stage/phase identifier
  - [ ] `round_num` - Round number
  - [ ] `group_num` - Group number (for group stages)

- [ ] `coverage` - Broadcast/coverage availability
  - [ ] `mlive` - Mobile live coverage available (integer 0/1)
  - [ ] `lineup` - Lineup information available (integer 0/1)

**Teams information:**

- [ ] `teams` - Home and away team details
  - [ ] `home` - Home team information
    - [ ] `id` - Team ID
    - [ ] `name` - Full team name
    - [ ] `short_name` - Short/abbreviated team name
    - [ ] `logo` - Team logo URL
    - [ ] `country_id` - Team's country ID
    - [ ] `country` - Team's country details
      - [ ] `id` - Country ID
      - [ ] `name` - Country name
      - [ ] `logo` - Country flag URL
  - [ ] `away` - Away team information (same structure as home)

**Competition information:**

- [ ] `competition` - League/tournament details
  - [ ] `id` - Competition ID
  - [ ] `name` - Full competition name
  - [ ] `short_name` - Short competition name
  - [ ] `logo` - Competition logo URL
  - [ ] `country_id` - Competition's country ID
  - [ ] `country` - Competition's country details
    - [ ] `id` - Country ID  
    - [ ] `name` - Country name
    - [ ] `logo` - Country flag URL

**Live match status** *(only present when live data available)*:

- [ ] `live_status` - Current match status
  - [ ] `status_id` - Status code (integer)
  - [ ] `status_text` - Human-readable status
  - [ ] `last_update` - Last update timestamp
  - [ ] `last_update_readable` - Human-readable last update time

**Live scores** *(only present when live data available)*:

- [ ] `scores` - Current match scores
  - [ ] `home` - Home team score array [FT, HT, ?, ?, Total, ?, ?]
  - [ ] `away` - Away team score array [FT, HT, ?, ?, Total, ?, ?]

- [ ] `score_summary` - Parsed score totals
  - [ ] `home_total` - Home team total score
  - [ ] `away_total` - Away team total score  
  - [ ] `home_ft` - Home team full-time score
  - [ ] `away_ft` - Away team full-time score
  - [ ] `home_ht` - Home team half-time score
  - [ ] `away_ht` - Away team half-time score

**VAR incidents** *(only present when VAR decisions occur)*:

- [ ] `var_incidents` - Video Assistant Referee decisions
  - [ ] `type` - Incident type (always 28 for VAR)
  - [ ] `position` - Team position (1=home, 2=away)
  - [ ] `time` - Match minute when VAR decision occurred
  - [ ] `player_id` - ID of player involved
  - [ ] `player_name` - Name of player involved
  - [ ] `var_reason` - Why VAR was triggered (1=Goal awarded, 2=Goal not awarded, etc.)
  - [ ] `var_result` - VAR decision outcome (1=Goal confirmed, 2=Goal cancelled, etc.)

**Odds data** *(only present when odds available)*:

- [ ] `odds` - Betting odds information
  - [ ] `{company_id}` - Odds company (e.g. "2" for Bet365)
    - [ ] `asia` - Asian handicap odds arrays
    - [ ] `eu` - European 1X2 odds arrays  
    - [ ] `bs` - Over/Under (Big/Small) odds arrays
    - [ ] `cr` - Corner kicks odds arrays

---

## 📝 **FIELD NOTES FOR FUTURE REFERENCE**

### **Odds Data Structure:**
Each odds array contains: `[timestamp, minute, odds1, line/handicap, odds2, status, sealed, score]`
- **minute**: `""` = pregame, `"1"-"10"` = match minutes (filtered to early match only)
- **asia**: `[home_odds, handicap, away_odds]`
- **eu**: `[home_odds, draw_odds, away_odds]` 
- **bs/cr**: `[over_odds, total_line, under_odds]`

### **Status Codes:**
- `1` = Not Started
- `2` = Live  
- `3` = Finished
- `4` = Finished
- `8` = Finished
- `13` = Postponed
- `15` = Cancelled

### **Score Arrays:**
Score arrays have 7 positions: `[FT, HT, ?, ?, Total, ?, ?]`
- Position 0: Full-time score
- Position 1: Half-time score  
- Position 4: Total/current score
- Other positions: TBD/unused

### **VAR Decision Codes:**
- **var_reason** (Why VAR was triggered):
  - 1 = Goal awarded, 2 = Goal not awarded, 3 = Penalty awarded, 4 = Penalty not awarded
  - 5 = Red card given, 6 = Card upgrade, 7 = Mistaken identity, 0 = Other
- **var_result** (What VAR decided):
  - 1 = Goal confirmed, 2 = Goal cancelled, 3 = Penalty confirmed, 4 = Penalty cancelled
  - 5 = Red card confirmed, 6 = Red card cancelled, 7 = Card upgrade confirmed
  - 8 = Card upgrade cancelled, 9 = Original decision, 10 = Original decision changed, 0 = Unknown

### **Data Availability:**
- **Live data**: Only present for ongoing matches (status_id 2-7)
- **VAR incidents**: Only present when VAR decisions occur during live matches
- **Odds data**: Only for matches with betting markets (filtered to pregame-10min)
- **Environment**: Weather data availability varies by venue
- **Team countries**: May be empty if team country not cached

### **Pretty Print Implementation Notes:**
- Use `data_sources` boolean flags to determine what data is available for display
- `scheduled_time_readable` is pre-formatted for display
- Team `short_name` may be empty, fallback to `name`
- Logo URLs are direct image links from thesports.com CDN
- Odds company priority: Bet365 (ID "2") preferred, others as fallback

---

## 🎯 **QUICK REFERENCE FOR COMMON USE CASES**

**Minimal match display:**
- `match_id`, `teams.home.name`, `teams.away.name`, `scheduled_time_readable`

**Live scoreboard:**
- Add: `live_status.status_text`, `score_summary.{home|away}_total`

**Full match card:**
- Add: `competition.short_name`, `environment`, `odds` 

**Debug/technical view:**
- Add: `data_sources`, `timestamp`, pipeline metadata

---

*This checklist reflects the exact structure output by merge.py as of 2025-06-26. Update when merge.py structure changes.*