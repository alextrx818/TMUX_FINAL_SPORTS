# Alerts.json Field Reference Map

**Single Match Example with Field IDs**

```json
{
  "match_id": "1l4rjnh4vvonm7v",                           // F01
  "timestamp": "06/29/2025 02:26 AM",                      // F02
  "scheduled_time_readable": "06/29/2025 05:00 AM",        // F03
  "competition": {                                          // F04
    "name": "Australia National Premier Leagues"           // F04a
  },
  "teams": {                                                // F05
    "home": {                                               // F05a
      "name": "Canberra FC"                                 // F05a1
    },
    "away": {                                               // F05b
      "name": "Gungahlin United"                            // F05b1
    }
  },
  "home_score_current": 2,                                  // F06
  "home_score_half": 2,                                     // F07
  "home_corners": 3,                                        // F08
  "": "",                                                   // F09 (anomaly)
  "away_score_current": 3,                                  // F10
  "away_score_half": 0,                                     // F11
  "away_corners": 1,                                        // F12
  "home_scores": [4,2,1,1,5,0,0],                          // F13 (array)
  "away_scores": [5,0,0,4,2,0,0],                          // F14 (array)
  "details_status_id": 4,                                   // F15
  "odds": {                                                 // F16
    "2": {                                                  // F16a (bookmaker)
      "spread": [                                           // F16a1 (array)
        [1751173404,"4","-105",3.25,"-117",2,0,"0-0"]       // F16a1_elements
      ],
      "MoneyLine": [                                        // F16a2 (array)
        [1751173750,"9","-999",900.0,"+1400",2,1,"0-0"]     // F16a2_elements
      ],
      "Over/Under": [                                       // F16a3 (array)
        [1751173351,"3","-105",5.0,"-117",2,0,"0-0"]        // F16a3_elements
      ],
      "Corners": [                                          // F16a4 (array)
        [1751173431,"4","-125",9.5,"-111",2,0,"0-0"]        // F16a4_elements
      ]
    }
  },
  "var_incidents": [                                        // F17 (array)
    {
      "type": 28,                                           // F17a
      "position": 1,                                        // F17b
      "time": 19,                                           // F17c
      "player_id": "vjxm8gh8o67xr6o",                       // F17d
      "player_name": "Player Name",                         // F17e
      "var_reason": 4,                                      // F17f
      "var_result": 3                                       // F17g
    }
  ],
  "environment": {                                          // F18
    "weather": "Fair",                                      // F18a
    "pressure": "769mmHg",                                  // F18b
    "temperature": "52°F",                                  // F18c
    "wind": "11mph (Gentle Breeze)",                        // F18d
    "humidity": "58%"                                       // F18e
  }
}
```

## Usage Examples
- "Modify F06 (home_score_current)"
- "Remove F16 (all odds data)"
- "Transform F13 (home_scores array)"
- "Update F15 (details_status_id)"
- "Add field after F03"

*Created: 2025-06-29*