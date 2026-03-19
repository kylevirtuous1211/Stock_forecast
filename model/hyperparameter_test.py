#!/usr/bin/env python
"""
Hyperparameter sweep for Timer sector forecasting.
Scans one variable at a time and generates plots.
"""
import os
import sys
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

def run_experiment(seq_len, lr, layers, accum, folder_name):
    # Construct command
    cmd = [
        "python", "model/finetune_timer.py",
        "--seq_len", str(seq_len),
        "--learning_rate", str(lr),
        "--train_layers_last", str(layers),
        "--accum_iter", str(accum),
        "--train_epochs", "20", # Run for a few more epochs to see convergence
        "--batch_size", "16",
        "--augment",
        "--checkpoints", f"./model/checkpoints/{folder_name}"
    ]
    print(f"\n>>> Running: {' '.join(cmd)}")
    subprocess.run(cmd)

def get_best_val_loss(folder_name):
    # Expected path: ./model/checkpoints/folder_name/Timer_Finetune_Sector_96/metrics.csv
    # The finetune_timer.py adds a subfolder for the setting. 
    # Actually, finetune_timer.py: path = os.path.join(self.args.checkpoints, setting)
    # where setting = 'Timer_Finetune_Sector_{}'.format(args.pred_len)
    base_path = f"./model/checkpoints/{folder_name}"
    # Find the metrics.csv in any subfolder
    for root, dirs, files in os.walk(base_path):
        if "metrics.csv" in files:
            csv_path = os.path.join(root, "metrics.csv")
            df = pd.read_csv(csv_path)
            if not df.empty:
                return df['vali_loss'].min()
    return None

def main():
    defaults = {
        'seq_len': 192,
        'learning_rate': 1e-4,
        'train_layers_last': 2,
        'accum_iter': 1
    }

    scans = {
        'seq_len': [96, 192, 384],
        'learning_rate': [1e-4, 5e-5, 1e-5],
        'train_layers_last': [1, 2, 4],
        'accum_iter': [1, 2, 4]
    }

    results = {}

    for param, values in scans.items():
        print(f"\n=== Sweeping {param} ===")
        param_results = []
        for val in values:
            # Prepare args
            configs = defaults.copy()
            configs[param] = val
            
            # Generate unique folder
            folder_name = f"sweep_{param}_{val}"
            
            run_experiment(
                configs['seq_len'], 
                configs['learning_rate'], 
                configs['train_layers_last'], 
                configs['accum_iter'],
                folder_name
            )
            
            best_loss = get_best_val_loss(folder_name)
            if best_loss is not None:
                param_results.append((val, best_loss))
        
        results[param] = param_results

    # Plotting
    plot_dir = "./model/sweep_plots"
    os.makedirs(plot_dir, exist_ok=True)

    for param, data in results.items():
        if not data: continue
        
        vals, losses = zip(*data)
        plt.figure(figsize=(8, 5))
        plt.plot(vals, losses, marker='o', linestyle='-')
        plt.title(f"Impact of {param} on Validation Loss")
        plt.xlabel(param)
        plt.ylabel("Min Validation Loss")
        plt.grid(True)
        
        # Format X-axis for learning rate (log scale usually helps)
        if param == 'learning_rate':
            plt.xscale('log')
            
        plt.savefig(os.path.join(plot_dir, f"{param}_plot.png"))
        print(f"Saved plot for {param} to {plot_dir}")

if __name__ == "__main__":
    main()
