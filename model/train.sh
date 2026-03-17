#!/bin/bash
# Start a tmux session named 'stock' and run the training
SESSION_NAME="stock"

tmux new-session -d -s $SESSION_NAME

# Send the command to the tmux session
tmux send-keys -t $SESSION_NAME "source .venv/bin/activate" C-m
tmux send-keys -t $SESSION_NAME "export PYTHONPATH=$PYTHONPATH:$(pwd)" C-m
tmux send-keys -t $SESSION_NAME "python model/finetune_timer.py --train_epochs 10 --batch_size 8" C-m

echo "Started training in tmux session '$SESSION_NAME'."
echo "Attach using: tmux attach -t $SESSION_NAME"
