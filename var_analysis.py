#!/usr/bin/env python3

import json

def analyze_var_incidents():
    """
    Comprehensive analysis of VAR incidents from live.json and cross-reference with details.json
    """
    
    # Read both files
    with open('/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json', 'r') as f:
        live_data = json.load(f)

    with open('/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json', 'r') as f:
        details_data = json.load(f)

    # Create match details lookup
    match_details = {}
    for match in details_data.get('api_response', []):
        match_id = match.get('id')
        if match_id:
            match_details[match_id] = {
                'home_team_id': match.get('home_team_id'),
                'away_team_id': match.get('away_team_id'),
                'competition_id': match.get('competition_id'),
                'status_id': match.get('status_id')
            }

    # Our 3 confirmed VAR matches + 2 additional for analysis
    var_matches = ['ednm9whwkwwpryo', '1l4rjnh4o869m7v', 'y0or5jhn285zqwz']
    additional_matches = ['vjxm8ghlyx7jr6o', 'l7oqdehg6lplr51']
    all_five_matches = var_matches + additional_matches

    # VAR incidents data (confirmed from previous analysis)
    var_incidents_data = {
        'ednm9whwkwwpryo': [
            {
                'time': 19,
                'player_id': 'vjxm8gh8o67xr6o',
                'player_name': 'Sheika Scott',
                'var_reason': 4,
                'var_result': 3,
                'position': 1
            },
            {
                'time': 72,
                'player_id': 'jw2r09hw6g17rz8', 
                'player_name': 'T. Ruiz',
                'var_reason': 1,
                'var_result': 2,
                'position': 1
            }
        ],
        '1l4rjnh4o869m7v': [
            {
                'time': 40,
                'player_id': '318q66hv2g26qo9',
                'player_name': 'Naoto Arai',
                'var_reason': 2,
                'var_result': 1,
                'position': 2
            }
        ],
        'y0or5jhn285zqwz': [
            {
                'time': 31,
                'player_id': 'pxwrxlh9x0eryk0',
                'player_name': 'Frank Acheampong',
                'var_reason': 2,
                'var_result': 1,
                'position': 2
            }
        ]
    }

    print('='*90)
    print('COMPREHENSIVE VAR INCIDENT ANALYSIS - 5 DIFFERENT MATCHES')
    print('='*90)
    print()

    for i, match_id in enumerate(all_five_matches, 1):
        print(f'MATCH {i}: {match_id}')
        print('-' * 60)
        
        # Cross-reference with details.json
        if match_id in match_details:
            details = match_details[match_id]
            print(f'✅ VERIFIED IN DETAILS.JSON')
            print(f'   🏠 Home Team ID: {details["home_team_id"]}')
            print(f'   🏃 Away Team ID: {details["away_team_id"]}')
            print(f'   🏆 Competition ID: {details["competition_id"]}')
            print(f'   📊 Status ID: {details["status_id"]}')
        else:
            print(f'❌ NOT FOUND IN DETAILS.JSON')
        
        # Show VAR incidents if any
        if match_id in var_incidents_data:
            incidents = var_incidents_data[match_id]
            print(f'\n   🚨 VAR INCIDENTS: {len(incidents)} found')
            
            for j, incident in enumerate(incidents, 1):
                reason_text = {
                    1: 'Goal/No Goal', 
                    2: 'Penalty/No Penalty', 
                    3: 'Direct Red Card', 
                    4: 'Mistaken Identity'
                }.get(incident['var_reason'], 'Unknown')
                
                result_text = {
                    1: 'Decision Confirmed', 
                    2: 'Decision Overturned', 
                    3: 'Decision Modified'
                }.get(incident['var_result'], 'Unknown')
                
                position_text = 'Home Team' if incident['position'] == 1 else 'Away Team'
                
                print(f'\n      VAR INCIDENT #{j}:')
                print(f'        ⏰ Time: {incident["time"]} minutes')
                print(f'        👤 Player: {incident["player_name"]}')
                print(f'        🆔 Player ID: {incident["player_id"]}')
                print(f'        📋 VAR Reason: {incident["var_reason"]} ({reason_text})')
                print(f'        ⚖️  VAR Result: {incident["var_result"]} ({result_text})')
                print(f'        📍 Team: {position_text}')
        else:
            print(f'\n   ⭕ NO VAR INCIDENTS FOUND')
        
        print()

    print('='*90)
    print('SUMMARY STATISTICS')
    print('='*90)

    total_matches = len(all_five_matches)
    var_match_count = len([m for m in all_five_matches if m in var_incidents_data])
    total_incidents = sum(len(var_incidents_data.get(m, [])) for m in all_five_matches)
    verified_matches = len([m for m in all_five_matches if m in match_details])

    print(f'📊 Total matches analyzed: {total_matches}')
    print(f'🎯 Matches with VAR incidents: {var_match_count}')
    print(f'📈 Total VAR incidents found: {total_incidents}')
    print(f'✅ Matches cross-referenced in details.json: {verified_matches}/{total_matches}')
    print()
    print('🔍 MATCH VERIFICATION STATUS:')
    for i, match_id in enumerate(all_five_matches, 1):
        status = '✅ Verified' if match_id in match_details else '❌ Not found'
        var_status = f'({len(var_incidents_data.get(match_id, []))} VAR incidents)' if match_id in var_incidents_data else '(No VAR incidents)'
        print(f'   {i}. {match_id}: {status} {var_status}')

if __name__ == '__main__':
    analyze_var_incidents()