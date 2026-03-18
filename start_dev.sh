#!/bin/bash
# start_dev.sh — Launch backend + frontend in a tmux session

SESSION="stock-forecast"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill any existing session with the same name
tmux kill-session -t "$SESSION" 2>/dev/null

# Create a new detached session with the first window named "backend"
tmux new-session -d -s "$SESSION" -n "backend" -x 220 -y 50

# Pane 0 (left): Backend — FastAPI via uvicorn
tmux send-keys -t "$SESSION:backend" \
  "cd '$ROOT_DIR' && source .venv/bin/activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" Enter

# Split the window vertically to create a second pane for the frontend
tmux split-window -h -t "$SESSION:backend"

# Pane 1 (right): Frontend — Vite dev server
tmux send-keys -t "$SESSION:backend.1" \
  "cd '$ROOT_DIR/frontend' && npm run dev" Enter

# Equalise pane widths
tmux select-layout -t "$SESSION:backend" even-horizontal

# Attach to the session
tmux attach-session -t "$SESSION"
