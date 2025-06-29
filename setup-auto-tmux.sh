#!/bin/bash

# One-time setup script to make tmux automatic
# Run once and tmux will auto-start for all future terminals

echo "Setting up automatic tmux terminal..."

# Create tmux config if not exists
if [ ! -f ~/.tmux.conf ]; then
    cp .tmux.conf ~/.tmux.conf
    echo "✓ Tmux config installed"
else
    echo "✓ Tmux config already exists"
fi

# Remove any existing tmux auto-start code from bashrc
sed -i '/# Auto-attach to tmux session/,/^fi$/d' ~/.bashrc 2>/dev/null

# Add auto-tmux code to bashrc
cat >> ~/.bashrc << 'EOF'

# Auto-attach to tmux session
if command -v tmux &> /dev/null && [ -n "$PS1" ] && [[ ! "$TERM" =~ screen ]] && [[ ! "$TERM" =~ tmux ]] && [ -z "$TMUX" ]; then
    # Check if sports-dev session exists, attach or create
    if tmux has-session -t sports-dev 2>/dev/null; then
        exec tmux attach-session -t sports-dev
    else
        exec tmux new-session -s sports-dev -c /workspaces/TMUX_FINAL_SPORTS
    fi
fi
EOF

echo "✓ Auto-tmux added to ~/.bashrc"

# Kill existing session to start fresh
tmux kill-session -t sports-dev 2>/dev/null

# Create the session with proper setup
tmux new-session -d -s sports-dev -c /workspaces/TMUX_FINAL_SPORTS

# Setup windows
tmux rename-window -t sports-dev:0 'main'
tmux new-window -t sports-dev:1 -n 'pipeline' -c /workspaces/TMUX_FINAL_SPORTS
tmux new-window -t sports-dev:2 -n 'logs' -c /workspaces/TMUX_FINAL_SPORTS  
tmux new-window -t sports-dev:3 -n 'test' -c /workspaces/TMUX_FINAL_SPORTS
tmux new-window -t sports-dev:4 -n 'dev' -c /workspaces/TMUX_FINAL_SPORTS

# Setup main window with splits
tmux select-window -t sports-dev:0
tmux split-window -h -c /workspaces/TMUX_FINAL_SPORTS
tmux split-window -v -c /workspaces/TMUX_FINAL_SPORTS
tmux select-pane -t 0

echo "✓ Tmux session 'sports-dev' created with 5 windows"
echo ""
echo "🎉 SETUP COMPLETE!"
echo ""
echo "From now on:"
echo "• Every new terminal will automatically start in tmux"
echo "• Your session has 5 windows: main, pipeline, logs, test, dev"
echo "• Use Ctrl-a + number to switch windows"
echo "• Use Ctrl-a d to detach (session keeps running)"
echo ""
echo "To start using tmux right now, run:"
echo "tmux attach -t sports-dev"
echo ""
echo "Or open a new terminal - it will auto-attach!"