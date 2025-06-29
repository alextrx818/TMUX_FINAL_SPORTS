#!/bin/bash

# Simplify tmux to just 1 window

# Remove current auto-tmux from bashrc
sed -i '/# Auto-attach to tmux session/,/^fi$/d' ~/.bashrc

# Add simple single-window tmux
cat >> ~/.bashrc << 'EOF'

# Auto-attach to simple tmux session (1 window only)
if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
    if tmux has-session -t main 2>/dev/null; then
        exec tmux attach-session -t main
    else
        exec tmux new-session -s main -c /workspaces/TMUX_FINAL_SPORTS
    fi
fi
EOF

# Kill the complex session
tmux kill-session -t sports-dev 2>/dev/null

# Create simple session
tmux new-session -d -s main -c /workspaces/TMUX_FINAL_SPORTS

echo "✅ Simplified! Now you have:"
echo "• Just 1 tmux window"
echo "• Session name: 'main'"
echo "• No extra windows or complexity"
echo ""
echo "To use: tmux attach -t main"