# Status ID Key

This document will contain the mapping between status IDs and their meanings for sports match data.

## Status ID Reference

| Status ID | Meaning | Description |
|-----------|---------|-------------|
| 0 | Abnormal | Abnormal (suggest hiding) |
| 1 | Not started | Match has not started yet |
| 2 | First half | Match is in first half |
| 3 | Half-time | Match is at half-time break |
| 4 | Second half | Match is in second half |
| 5 | Overtime | Match is in overtime |
| 6 | Overtime (deprecated) | Overtime (deprecated status) |
| 7 | Penalty Shoot-out | Match is in penalty shoot-out |
| 8 | End | Match has ended |
| 9 | Delay | Match is delayed |
| 10 | Interrupt | Match is interrupted |
| 11 | Cut in half | Match was cut in half |
| 12 | Cancel | Match was cancelled |
| 13 | To be determined | Match time/status to be determined |

## Notes

- Status IDs are found in the `details_status_id` field of match data
- Used for understanding match states in the sports data pipeline
- Most common status IDs in current data: 2 (First half), 3 (Half-time), 4 (Second half), 8 (End), 9 (Delay), 13 (TBD)

---

*Created: 2025-06-29*  
*Updated: 2025-06-29*  
*Purpose: Reference for interpreting status_id values in sports match data*

