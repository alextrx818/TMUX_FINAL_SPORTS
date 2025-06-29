#!/bin/bash

# Sports API Pipeline Starter
# This script initiates the complete data fetch pipeline

echo "Starting Sports API Pipeline..."
echo "================================"

# Set API credentials (hardcoded for convenience)
export THESPORTS_USER="thenecpt"
export THESPORTS_SECRET="0c55322e8e196d6ef9066fa4252cf386"

echo "✅ API credentials set"
echo "User: $THESPORTS_USER"
echo "Secret: [HIDDEN]"

# Clean up any previous temp files
rm -f /tmp/live_matches.json
rm -f /tmp/match_details.json
rm -f /tmp/match_odds.json
rm -f /tmp/team_ids.json
rm -f /tmp/competition_ids.json
rm -f /tmp/team_data.json
rm -f /tmp/competition_data.json
rm -f /tmp/country_data.json

echo "Starting pipeline with live.py..."

# Start the pipeline - live.py will trigger the chain
python3 live.py

echo "Pipeline completed!"
echo "Data files saved in /tmp/"
echo "- live_matches.json"
echo "- match_details.json" 
echo "- match_odds.json"
echo "- team_data.json"
echo "- competition_data.json"
echo "- country_data.json"