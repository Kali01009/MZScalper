import logging
import pandas as pd
import numpy as np
import time
from notifier import send_telegram_message

# Utility to calculate volatility (std dev of % changes)
def detect_squeeze(df, window=20, threshold=0.2):
    returns = df['Close'].pct_change()
    rolling_std = returns.rolling(window=window).std()
    return rolling_std.iloc[-1] < threshold * rolling_std.max()

# Detect triangle patterns
def detect_triangle(df):
    recent = df[-50:]
    highs = recent['High']
    lows = recent['Low']

    # Approximate triangle by trendline convergence
    upper_slope = np.polyfit(range(len(highs)), highs, 1)[0]
    lower_slope = np.polyfit(range(len(lows)), lows, 1)[0]

    if upper_slope < 0 and lower_slope > 0:
        return "Symmetrical Triangle"
    elif upper_slope == 0 and lower_slope > 0:
        return "Ascending Triangle"
    elif lower_slope == 0 and upper_slope < 0:
        return "Descending Triangle"
    return None

# Detect double top/bottom patterns
def detect_double_top_bottom(df):
    close = df['Close'][-60:]
    peaks = close[(close.shift(1) < close) & (close.shift(-1) < close)]
    troughs = close[(close.shift(1) > close) & (close.shift(-1) > close)]
    
    if len(peaks) >= 2 and abs(peaks.iloc[-1] - peaks.iloc[-2]) < 0.005 * close.mean():
        return "Double Top"
    if len(troughs) >= 2 and abs(troughs.iloc[-1] - troughs.iloc[-2]) < 0.005 * close.mean():
        return "Double Bottom"
    return None

# Head and shoulders detection (very simple version)
def detect_head_and_shoulders(df):
    close = df['Close'][-60:].reset_index(drop=True)
    if len(close) < 60:
        return None
    # naive pattern check
    l_shoulder = close[10:20].max()
    head = close[25:35].max()
    r_shoulder = close[40:50].max()
    if head > l_shoulder and head > r_shoulder and abs(l_shoulder - r_shoulder) < 0.01 * head:
        return "Head and Shoulders"
    if head < l_shoulder and head < r_shoulder and abs(l_shoulder - r_shoulder) < 0.01 * head:
        return "Inverse Head and Shoulders"
    return None

# Flag / Pennant detection
def detect_flag_pennant(df):
    last = df[-20:]
    trend = df['Close'][-40:-20]
    recent = df['Close'][-20:]

    trend_change = trend.iloc[-1] - trend.iloc[0]
    recent_range = recent.max() - recent.min()

    if abs(trend_change) > 0.005 * df['Close'].mean() and recent_range < 0.004 * df['Close'].mean():
        return "Flag or Pennant"
    return None

# Main function to analyze index data
def analyze_selected_indices(selected_indices, data):
    for index in selected_indices:
        logging.info(f"Analyzing {index}...")

        # Make sure data has enough candles
        if len(data) < 300:
            logging.warning(f"Not enough data for {index} (needs 300, has {len(data)})")
            continue

        df = data.copy().tail(300)
        breakout_signals = []

        # Pre-breakout condition: Squeeze detection
        if detect_squeeze(df):
            breakout_signals.append("⚠️ Low volatility (squeeze) detected")

        # Pattern detections
        triangle = detect_triangle(df)
        if triangle:
            breakout_signals.append(f"🔺 Possible {triangle}")

        flag_pennant = detect_flag_pennant(df)
        if flag_pennant:
            breakout_signals.append(f"📍 {flag_pennant} detected")

        double_pattern = detect_double_top_bottom(df)
        if double_pattern:
            breakout_signals.append(f"🔄 {double_pattern} pattern")

        hs = detect_head_and_shoulders(df)
        if hs:
            breakout_signals.append(f"👤 {hs} pattern forming")

        # Send to Telegram if signals found
        if breakout_signals:
            message = f"📊 *Breakout Alert for {index}*\n\n"
            message += "\n".join(breakout_signals)
            message += f"\n\n_Analyzed on 1-minute timeframe using last 300 candles._"
            send_telegram_message(message)
            logging.info(f"Signal sent for {index}")
        else:
            logging.info(f"No breakout signal detected for {index}")

# Function to run the analysis in a loop indefinitely
def run_analysis():
    selected_indices = ["R_10", "R_25", "R_50"]  # You can modify this to include your indices
    while True:
        # Fetch live data from the trading API (replace with your method to get live data)
        data = fetch_live_data()  # Placeholder for the function to fetch live data

        # Perform analysis
        analyze_selected_indices(selected_indices, data)

        # Sleep for 60 seconds before the next analysis cycle (to stay within 1-minute timeframe)
        time.sleep(60)

def fetch_live_data():
    # Placeholder: This function should fetch the latest live candle data from your data source
    # Simulating with random data for now (replace with actual API fetch)
    now = pd.to_datetime("now")
    timestamps = pd.date_range(end=now, periods=300, freq='T')
    data = pd.DataFrame(index=timestamps)
    data['Open'] = np.random.uniform(100, 110, size=len(data))
    data['High'] = data['Open'] + np.random.uniform(0, 2, size=len(data))
    data['Low'] = data['Open'] - np.random.uniform(0, 2, size=len(data))
    data['Close'] = np.random.uniform(data['Low'], data['High'], size=len(data))
    return data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_analysis()
