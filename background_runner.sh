#!/bin/bash

# Background Pipeline Runner with Process Management
# Starts the continuous pipeline in the background with proper logging

SCRIPT_DIR="/workspaces/TMUX_FINAL_SPORTS"
PID_FILE="$SCRIPT_DIR/pipeline.pid"
LOG_FILE="$SCRIPT_DIR/pipeline_background.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 `cat "$PID_FILE"` 2>/dev/null; then
            echo "❌ Pipeline is already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        
        echo "🚀 Starting background pipeline..."
        echo "📄 Logs: $LOG_FILE"
        echo "🆔 PID will be stored in: $PID_FILE"
        
        # Set environment variables and start in background
        export THESPORTS_USER=thenecpt
        export THESPORTS_SECRET=0c55322e8e196d6ef9066fa4252cf386
        nohup $SCRIPT_DIR/continuous_fetch.sh > "$LOG_FILE" 2>&1 &
        PID=$!
        echo $PID > "$PID_FILE"
        
        echo "✅ Pipeline started successfully!"
        echo "🆔 Process ID: $PID"
        echo "📊 To view logs: tail -f $LOG_FILE"
        echo "🛑 To stop: ./background_runner.sh stop"
        ;;
        
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "❌ No PID file found. Pipeline may not be running."
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🛑 Stopping pipeline (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            echo "✅ Pipeline stopped successfully!"
        else
            echo "❌ Process $PID not found. Cleaning up PID file."
            rm -f "$PID_FILE"
        fi
        ;;
        
    status)
        if [ -f "$PID_FILE" ] && kill -0 `cat "$PID_FILE"` 2>/dev/null; then
            PID=$(cat "$PID_FILE")
            echo "✅ Pipeline is running (PID: $PID)"
            echo "📊 Runtime: $(ps -o etime= -p $PID | tr -d ' ')"
        else
            echo "❌ Pipeline is not running"
            [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        fi
        ;;
        
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "📄 Showing last 20 lines of pipeline logs:"
            echo "==========================================="
            tail -20 "$LOG_FILE"
            echo ""
            echo "📊 To follow logs live: tail -f $LOG_FILE"
        else
            echo "❌ No log file found at $LOG_FILE"
        fi
        ;;
        
    restart)
        echo "🔄 Restarting pipeline..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    *)
        echo "🤖 Sports API Pipeline Background Runner"
        echo "========================================"
        echo "Usage: $0 {start|stop|status|logs|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start pipeline in background"
        echo "  stop    - Stop background pipeline"
        echo "  status  - Check if pipeline is running"
        echo "  logs    - Show recent log output"
        echo "  restart - Stop and start pipeline"
        echo ""
        echo "Example:"
        echo "  ./background_runner.sh start"
        echo "  ./background_runner.sh status"
        echo "  ./background_runner.sh logs"
        echo "  ./background_runner.sh stop"
        exit 1
        ;;
esac