#!/bin/bash

# Add tmux auto-attach to shell profile
echo '
# Auto-attach to tmux session
if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
  # Try to attach to existing session, or create new one
  tmux attach-session -t sports-dev || tmux new-session -s sports-dev -c /workspaces/TMUX_FINAL_SPORTS
fi
' >> ~/.bashrc

echo "Tmux auto-attach added to ~/.bashrc"
echo "Restart your terminal or run 'source ~/.bashrc' to activate"