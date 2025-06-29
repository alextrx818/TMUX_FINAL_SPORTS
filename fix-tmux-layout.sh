#!/bin/bash

# Fix tmux to use single panes (no splits)

# Remove the auto-tmux from bashrc and replace with cleaner version
sed -i '/# Auto-attach to tmux session/,/^fi$/d' ~/.bashrc

# Add cleaner auto-tmux code
cat >> ~/.bashrc << 'EOF'

# Auto-attach to tmux session (single pane per window)
if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
    if tmux has-session -t sports-dev 2>/dev/null; then
        exec tmux attach-session -t sports-dev
    else
        # Create session with single panes only
        tmux new-session -d -s sports-dev -c /workspaces/TMUX_FINAL_SPORTS
        tmux rename-window -t sports-dev:0 'main'
        tmux new-window -t sports-dev -n 'pipeline' -c /workspaces/TMUX_FINAL_SPORTS
        tmux new-window -t sports-dev -n 'logs' -c /workspaces/TMUX_FINAL_SPORTS
        tmux new-window -t sports-dev -n 'test' -c /workspaces/TMUX_FINAL_SPORTS
        tmux new-window -t sports-dev -n 'dev' -c /workspaces/TMUX_FINAL_SPORTS
        tmux select-window -t sports-dev:0
        exec tmux attach-session -t sports-dev
    fi
fi
EOF

echo "✅ Fixed! Now each window will have a single terminal pane."
echo "The split panes have been removed from your current session."