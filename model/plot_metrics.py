import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

def plot_metrics(csv_path, output_path=None):
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Check for expected columns
    expected_cols = ['epoch', 'train_loss', 'vali_loss']
    if not all(col in df.columns for col in expected_cols):
        print(f"Error: CSV missing required columns. Found: {df.columns}")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df['epoch'], df['train_loss'], label='Train Loss', marker='o')
    plt.plot(df['epoch'], df['vali_loss'], label='Validation Loss', marker='o')
    
    if 'mse' in df.columns:
         plt.plot(df['epoch'], df['mse'], label='MSE', linestyle='--')

    plt.title('Training and Validation Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot training metrics from CSV')
    parser.add_argument('csv_path', type=str, help='Path to metrics.csv')
    parser.add_argument('--output', type=str, default=None, help='Path to save the plot (optional)')
    
    args = parser.parse_args()
    
    # Default output path if not provided
    if args.output is None:
        base_dir = os.path.dirname(args.csv_path)
        args.output = os.path.join(base_dir, 'training_plot.png')
        
    plot_metrics(args.csv_path, args.output)
