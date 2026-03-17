import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Set style
sns.set(style="whitegrid")

def analyze_sector_data(csv_path="model/sector_data.csv", output_dir="analysis_plot"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path, index_col='timestamp', parse_dates=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Data shape: {df.shape}")
    print(df.head())

    # 1. Price History Plot
    plt.figure(figsize=(14, 7))
    for col in df.columns:
        # Normalize to start at 1 for comparison
        normalized_price = df[col] / df[col].iloc[0]
        plt.plot(normalized_price, label=col)
    
    plt.title('Normalized Price History (Base=1)')
    plt.xlabel('Date')
    plt.ylabel('Normalized Price')
    plt.legend()
    plt.savefig(os.path.join(output_dir, "price_history_normalized.png"))
    plt.close()
    print("Saved price_history_normalized.png")

    # 2. Correlation Matrix
    # Calculate daily returns for correlation (more stationary)
    # Resample to daily close to reduce noise from 1-min data
    daily_df = df.resample('1D').last().dropna()
    daily_returns = daily_df.pct_change().dropna()

    plt.figure(figsize=(12, 10))
    corr = daily_returns.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Daily Returns')
    plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
    plt.close()
    print("Saved correlation_matrix.png")

    # 3. Distribution of Returns (Histograms)
    plt.figure(figsize=(14, 10))
    # Pick top 4 symbols + XLK to plot
    symbols_to_plot = ['XLK'] + list(df.columns[:3]) 
    if len(symbols_to_plot) > 4:
        symbols_to_plot = symbols_to_plot[:4]
    
    for i, symbol in enumerate(symbols_to_plot):
        plt.subplot(2, 2, i+1)
        sns.histplot(daily_returns[symbol], kde=True, bins=50)
        plt.title(f'Distribution of Daily Returns: {symbol}')
        plt.xlabel('Return')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "returns_distribution.png"))
    plt.close()
    print("Saved returns_distribution.png")

    # 4. Rolling Volatility (30-day window)
    plt.figure(figsize=(14, 7))
    rolling_vol = daily_returns.rolling(window=30).std() * np.sqrt(252) # Annualized
    
    for col in rolling_vol.columns:
        plt.plot(rolling_vol[col], label=col)
        
    plt.title('30-Day Rolling Volatility (Annualized)')
    plt.xlabel('Date')
    plt.ylabel('Volatility')
    plt.legend()
    plt.savefig(os.path.join(output_dir, "rolling_volatility.png"))
    plt.close()
    print("Saved rolling_volatility.png")

    # 5. Z-Score Normalization and Distribution Analysis
    print("\n--- Z-Score Analysis ---")
    from scipy.stats import zscore, skew, kurtosis
    
    # Apply Z-score normalization to the original price data (or returns? usually returns for distribution)
    # User said "normalize all data", implying prices, but prices are non-stationary.
    # However, Timer often works on Z-scored values of the lookback window.
    # Let's normalize the *Prices* as requested, but also note the properties.
    # actually, usually we analyze returns for distribution normality.
    # But let's do PRICE Z-scores as requested to see the distribution of values.
    
    df_zscore = df.apply(zscore)
    
    plt.figure(figsize=(14, 10))
    for i, symbol in enumerate(symbols_to_plot):
        plt.subplot(2, 2, i+1)
        sns.histplot(df_zscore[symbol], kde=True, bins=50)
        plt.title(f'Z-Score Distribution (Prices): {symbol}')
        plt.xlabel('Z-Score')
        
        # Calculate stats
        s = skew(df_zscore[symbol])
        k = kurtosis(df_zscore[symbol])
        print(f"{symbol} - Skew: {s:.2f}, Kurtosis: {k:.2f}")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "zscore_price_distribution.png"))
    plt.close()
    print("Saved zscore_price_distribution.png")
    
    # Also do Z-scores of Returns (more standard for financial analysis)
    daily_returns_z = daily_returns.apply(zscore)
    
    plt.figure(figsize=(14, 10))
    for i, symbol in enumerate(symbols_to_plot):
        plt.subplot(2, 2, i+1)
        sns.histplot(daily_returns_z[symbol], kde=True, bins=50)
        plt.title(f'Z-Score Distribution (Daily Returns): {symbol}')
        plt.xlabel('Z-Score')
        
        s = skew(daily_returns_z[symbol])
        k = kurtosis(daily_returns_z[symbol])
        print(f"{symbol} Returns - Skew: {s:.2f}, Kurtosis: {k:.2f}")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "zscore_returns_distribution.png"))
    plt.close()
    print("Saved zscore_returns_distribution.png")

    # 6. Transformation Comparison (Log, Diff, Power)
    print("\n--- Transformation Comparison ---")
    from sklearn.preprocessing import PowerTransformer, StandardScaler
    
    # We will test transformations on a single representative symbol (e.g. XLK) 
    # and maybe one stock (e.g. AAPL) to see the effect.
    test_symbols = ['XLK', 'AAPL']
    
    for symbol in test_symbols:
        print(f"\nAnalyzing transformations for {symbol}...")
        raw_data = df[symbol].values.reshape(-1, 1)
        
        # 1. Log Prices
        log_data = np.log(raw_data)
        
        # 2. Key: Returns (Differencing)
        # We need to handle NaN from diff
        diff_data = df[symbol].diff().dropna().values.reshape(-1, 1)
        
        # 3. Log Returns
        log_ret_data = np.log(df[symbol] / df[symbol].shift(1)).dropna().values.reshape(-1, 1)
        
        # 4. Power Transformer (Yeo-Johnson)
        pt = PowerTransformer(method='yeo-johnson')
        # Power transform usually works best on stationary-ish data or to fix skew. 
        # Let's try it on Returns (since prices are trending).
        # But maybe user wants to forecast Prices directly? 
        # Timer usually takes raw series (normalized by RevIN or similar).
        # Let's try PT on Raw Prices and Log Returns.
        pt_price = pt.fit_transform(raw_data)
        pt_ret = pt.fit_transform(log_ret_data)
        
        # Plotting
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f'Distribution Transformations for {symbol}', fontsize=16)
        
        # Helper to plot
        def plot_dist(data, ax, title):
            sns.histplot(data, kde=True, bins=50, ax=ax, edgecolor=None)
            ax.set_title(title)
            s = skew(data)
            k = kurtosis(data)
            # Handle array inside skew result if needed
            if isinstance(s, (list, np.ndarray)): s = s[0]
            if isinstance(k, (list, np.ndarray)): k = k[0]
            ax.set_xlabel(f"Skew: {s:.2f}, Kurt: {k:.2f}")

        plot_dist(raw_data, axes[0, 0], "Raw Prices")
        plot_dist(log_data, axes[0, 1], "Log Prices")
        plot_dist(pt_price, axes[0, 2], "Power Transform (Prices)")
        
        plot_dist(diff_data, axes[1, 0], "Differenced (Price Chg)")
        plot_dist(log_ret_data, axes[1, 1], "Log Returns")
        plot_dist(pt_ret, axes[1, 2], "Power Transform (Returns)")
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"transform_comparison_{symbol}.png"))
        plt.close()
        print(f"Saved transform_comparison_{symbol}.png")

if __name__ == "__main__":
    analyze_sector_data()
