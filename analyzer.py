import pandas as pd
from notifier import send_telegram_message

def identify_levels(data, window=10):
    data['Support'] = data['Low'].rolling(window=window).min()
    data['Resistance'] = data['High'].rolling(window=window).max()
    return data

def is_consolidating(data, window=10, threshold=0.02):
    recent = data.tail(window)
    max_close = recent['close'].max()
    min_close = recent['close'].min()
    return (max_close - min_close) / min_close < threshold

def calculate_trade_parameters(current, previous):
    entry = current['close']
    stop_loss = entry - (previous['resistance'] - previous['support']) * 0.5
    take_profit = entry + (entry - stop_loss) * 1.5
    return entry, stop_loss, take_profit

def analyze_breakout(data, symbol):
    trades = []
    data = identify_levels(data)

    for i in range(20, len(data)):
        if is_consolidating(data.iloc[i - 10:i]):
            current = data.iloc[i]
            previous = data.iloc[i - 1]

            breakout_up = current['close'] > previous['Resistance']
            breakout_down = current['close'] < previous['Support']

            if breakout_up or breakout_down:
                direction = 'BUY' if breakout_up else 'SELL'
                entry, stop_loss, take_profit = calculate_trade_parameters(current, previous)
                trades.append({
                    'Time': current.name,
                    'Direction': direction,
                    'Entry': round(entry, 2),
                    'StopLoss': round(stop_loss, 2),
                    'TakeProfit': round(take_profit, 2)
                })
                # Send the first (or best) trade signal immediately
                msg = (f"🚨 *Breakout Detected* for *{symbol}* @ {current.name}\n"
                       f"Direction: *{direction}*\n"
                       f"Entry Price: `{entry}`\n"
                       f"Stop Loss: `{stop_loss}`\n"
                       f"Take Profit: `{take_profit}`")
                send_telegram_message(msg)
                return trades  # Return after sending the first signal

    return trades

def analyze_selected_indices(selected_indices, data):
    for symbol in selected_indices:
        trades = analyze_breakout(data, symbol)
        # Optionally handle further trades if needed
