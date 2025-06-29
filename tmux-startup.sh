#!/bin/bash

# TMUX startup script for TMUX_FINAL_SPORTS project

SESSION="sports-dev"

# Check if session already exists
tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then
  # Create new session with first window
  tmux new-session -d -s $SESSION -c /workspaces/TMUX_FINAL_SPORTS

  # Window 0: Main development
  tmux rename-window -t $SESSION:0 'main'
  
  # Window 1: Data pipeline monitoring
  tmux new-window -t $SESSION:1 -n 'pipeline' -c /workspaces/TMUX_FINAL_SPORTS
  tmux send-keys -t $SESSION:1 'tail -f pipeline_background.log' C-m
  
  # Window 2: Log monitoring
  tmux new-window -t $SESSION:2 -n 'logs' -c /workspaces/TMUX_FINAL_SPORTS
  tmux send-keys -t $SESSION:2 'python view_logs.py' C-m
  
  # Window 3: Testing
  tmux new-window -t $SESSION:3 -n 'test' -c /workspaces/TMUX_FINAL_SPORTS
  
  # Window 4: File editing/development
  tmux new-window -t $SESSION:4 -n 'dev' -c /workspaces/TMUX_FINAL_SPORTS
  
  # Split the main window into panes
  tmux select-window -t $SESSION:0
  tmux split-window -h -c /workspaces/TMUX_FINAL_SPORTS
  tmux split-window -v -c /workspaces/TMUX_FINAL_SPORTS
  tmux select-pane -t 0
  
  # Set up the panes
  tmux send-keys -t $SESSION:0.0 'ls -la' C-m
  tmux send-keys -t $SESSION:0.1 'python -c "import sys; print(f\"Python {sys.version}\")"' C-m
  tmux send-keys -t $SESSION:0.2 'echo "Ready for sports data analysis!"' C-m
  
  # Select the main window
  tmux select-window -t $SESSION:0
  tmux select-pane -t 0
fi

# Attach to the session
tmux attach-session -t $SESSION