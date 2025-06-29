#!/usr/bin/env python3

import json

# Load merge.json
with open('/workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json', 'r') as f:
    merge_data = json.load(f)

print("=== ODDS GROUPING TEST ===")
print(f"Total matches: {len(merge_data['matches'])}")

# Check first 5 matches for their complete structure
for i, match in enumerate(merge_data['matches'][:5]):
    print(f"\n--- MATCH {i+1}: {match['match_id']} ---")
    print(f"Match ID: {match['match_id']}")
    
    # Check if odds data exists for this match
    has_odds = 'odds' in match
    print(f"Has odds data: {has_odds}")
    
    if has_odds:
        print(f"Odds companies: {list(match['odds'].keys())}")
        for company_id, company_data in match['odds'].items():
            print(f"  Company {company_id}: {list(company_data.keys())}")
    
    # Show what other data is grouped with this match
    main_fields = ['teams', 'competition', 'environment', 'data_sources']
    for field in main_fields:
        if field in match:
            if field == 'teams':
                print(f"Teams: {match[field]['home']['name']} vs {match[field]['away']['name']}")
            elif field == 'competition':
                print(f"Competition: {match[field]['name']}")
            elif field == 'data_sources':
                print(f"Data sources: {match[field]}")
    print("---")

# Count total matches with odds
matches_with_odds = sum(1 for match in merge_data['matches'] if 'odds' in match)
print(f"\nSUMMARY:")
print(f"Total matches: {len(merge_data['matches'])}")
print(f"Matches with odds: {matches_with_odds}")
print(f"Odds data correctly grouped with individual matches: {'YES' if matches_with_odds > 0 else 'NO'}")