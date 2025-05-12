import pandas as pd
from notifier import send_telegram_message

def identify_levels(data, window=10):
    """Identify support and resistance levels"""
    data['Support'] = data['Low'].rolling(window=window).min()
    data['Resistance'] = data['High'].rolling(window=window).max()
    return data

def is_consolidating(data, window=10, threshold=0.02):
    """Check if the data is consolidating within a defined threshold"""
    recent = data.tail(window)
    max_close = recent['Close'].max()
    min_close = recent['Close'].min()
    return (max_close - min_close) / min_close < threshold

def calculate_trade_parameters(current, previous):
    """Calculate trade entry, stop loss, and take profit"""
    entry = current['Close']
    stop_loss = entry - (previous['Resistance'] - previous['Support']) * 0.5
    take_profit = entry + (entry - stop_loss) * 1.5
    return entry, stop_loss, take_profit

def analyze_breakout(data, selected_indices):
    """Analyze breakout opportunities and prepare trades"""
    trades = []

    for i in range(20, len(data)):
        if is_consolidating(data.iloc[i - 10:i]):
            current = data.iloc[i]
            previous = data.iloc[i - 1]

            breakout_up = current['Close'] > previous['Resistance']
            breakout_down = current['Close'] < previous['Support']

            if breakout_up:
                entry, stop_loss, take_profit = calculate_trade_parameters(current, previous)
                trades.append({
                    'Time': current.name,
                    'Direction': 'BUY',
                    'Entry': round(entry, 2),
                    'StopLoss': round(stop_loss, 2),
                    'TakeProfit': round(take_profit, 2)
                })

            elif breakout_down:
                entry, stop_loss, take_profit = calculate_trade_parameters(current, previous)
                trades.append({
                    'Time': current.name,
                    'Direction': 'SELL',
                    'Entry': round(entry, 2),
                    'StopLoss': round(stop_loss, 2),
                    'TakeProfit': round(take_profit, 2)
                })

    return trades

def send_trade_alerts(selected_indices, trades):
    """Send alerts for detected trades"""
    for index in selected_indices:
        for trade in trades:
            msg = (f"🚨 *Breakout Detected* for *{index}* @ {trade['Time']}\n"
                   f"Direction: *{trade['Direction']}*\n"
                   f"Entry Price: `{trade['Entry']}`\n"
                   f"Stop Loss: `{trade['StopLoss']}`\n"
                   f"Take Profit: `{trade['TakeProfit']}`")
            send_telegram_message(msg)

def analyze_selected_indices(selected_indices, data):
    """Main function to run all analyses and send alerts"""
    data = identify_levels(data)
    trades = analyze_breakout(data, selected_indices)
    send_trade_alerts(selected_indices, trades)
