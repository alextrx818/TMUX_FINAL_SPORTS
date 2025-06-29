#!/bin/bash

# Fix System Error Script
# This script addresses the "system error" issues in tmux

echo "🔧 Fixing System Issues..."
echo "=========================="

# 1. Kill any hanging processes
echo "1. Cleaning up processes..."
pkill -f continuous_fetch 2>/dev/null || true
pkill -f background_runner 2>/dev/null || true

# 2. Kill all tmux sessions
echo "2. Cleaning up tmux sessions..."
tmux kill-server 2>/dev/null || true
sleep 2

# 3. Clean up temp files
echo "3. Cleaning temp files..."
rm -f pipeline.pid
rm -f /tmp/live_matches.json
rm -f /tmp/match_details.json
rm -f /tmp/match_odds.json
rm -f /tmp/team_ids.json
rm -f /tmp/competition_ids.json
rm -f /tmp/team_data.json
rm -f /tmp/competition_data.json
rm -f /tmp/country_data.json

# 4. Start fresh tmux session
echo "4. Starting fresh tmux session..."
SESSION="sports-clean"

# Create new session
tmux new-session -d -s $SESSION -c /workspaces/TMUX_FINAL_SPORTS

# Setup basic windows
tmux rename-window -t $SESSION:0 'main'
tmux send-keys -t $SESSION:0 'clear && echo "✅ System Fixed - Ready to work!"' C-m

# Pipeline monitoring window
tmux new-window -t $SESSION:1 -n 'monitor' -c /workspaces/TMUX_FINAL_SPORTS
tmux send-keys -t $SESSION:1 'clear && echo "📊 Pipeline Monitor - Ready"' C-m

# Testing window
tmux new-window -t $SESSION:2 -n 'test' -c /workspaces/TMUX_FINAL_SPORTS
tmux send-keys -t $SESSION:2 'clear && echo "🧪 Testing Environment - Ready"' C-m

# Back to main window
tmux select-window -t $SESSION:0

echo "✅ System fixed!"
echo "📋 To connect: tmux attach -t $SESSION"
echo "🚀 To start pipeline: ./background_runner.sh start"
echo "🛑 To stop pipeline: ./background_runner.sh stop"

# Attach to session
tmux attach-session -t $SESSION
