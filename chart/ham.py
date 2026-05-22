import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os

# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "data/banknifty_5min_data.csv"

CHART_FOLDER = "hammer/charts"

RR_RATIO = 1.5

LOOKBACK_CANDLES = 12

MIN_FALL = 200

# Create charts folder
os.makedirs(CHART_FOLDER, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(CSV_FILE)

df['Timestamp'] = pd.to_datetime(df['Timestamp'])

df['Date'] = df['Timestamp'].dt.date

# ============================================================
# HAMMER DETECTION
# ============================================================

def is_hammer(open_price, high_price, low_price, close_price):

    body = abs(close_price - open_price)

    upper_wick = high_price - max(open_price, close_price)

    lower_wick = min(open_price, close_price) - low_price

    if body == 0:
        body = 0.01

    return (
        lower_wick >= 2 * body and
        upper_wick <= body
    )

# ============================================================
# PROCESS DAY-WISE
# ============================================================

grouped = df.groupby('Date')

trade_results = []

# ============================================================
# MAIN LOOP
# ============================================================

for date, day_df in grouped:

    day_df = day_df.reset_index(drop=True)

    # Skip small days
    if len(day_df) < LOOKBACK_CANDLES + 10:
        continue

    trade_taken = False

    # ========================================================
    # CANDLE LOOP
    # ========================================================

    for i in range(LOOKBACK_CANDLES, len(day_df) - 1):

        if trade_taken:
            break

        current = day_df.iloc[i]

        # ====================================================
        # PREVIOUS 1 HOUR FALL
        # ====================================================

        previous_window = day_df.iloc[i - LOOKBACK_CANDLES:i]

        highest_price = previous_window['High'].max()

        lowest_price = previous_window['Low'].min()

        total_fall = highest_price - lowest_price

        bearish_trend = total_fall >= MIN_FALL

        # ====================================================
        # HAMMER CHECK
        # ====================================================

        hammer_found = is_hammer(
            current['Open'],
            current['High'],
            current['Low'],
            current['Close']
        )

        if bearish_trend and hammer_found:

            hammer_high = current['High']

            hammer_low = current['Low']

            risk = hammer_high - hammer_low

            entry_price = hammer_high

            sl_price = hammer_low

            target_price = hammer_high + (risk * RR_RATIO)

            # =================================================
            # WAIT FOR ENTRY
            # =================================================

            for j in range(i + 1, len(day_df)):

                next_candle = day_df.iloc[j]

                # ENTRY TRIGGER
                if next_candle['High'] >= entry_price:

                    entry_time = next_candle['Timestamp']

                    # =========================================
                    # CHECK TARGET / SL
                    # =========================================

                    exit_price = None
                    exit_time = None
                    trade_status = None

                    for k in range(j, len(day_df)):

                        trade_candle = day_df.iloc[k]

                        # TARGET HIT
                        if trade_candle['High'] >= target_price:

                            exit_price = target_price

                            exit_time = trade_candle['Timestamp']

                            trade_status = "TARGET HIT"

                            break

                        # SL HIT
                        if trade_candle['Low'] <= sl_price:

                            exit_price = sl_price

                            exit_time = trade_candle['Timestamp']

                            trade_status = "SL HIT"

                            break

                    # =========================================
                    # EOD EXIT
                    # =========================================

                    if exit_price is None:

                        last_candle = day_df.iloc[-1]

                        exit_price = last_candle['Close']

                        exit_time = last_candle['Timestamp']

                        trade_status = "EOD EXIT"

                    # =========================================
                    # SAVE RESULT
                    # =========================================

                    trade_results.append({

                        'Date': date,

                        'Hammer Time': current['Timestamp'],

                        'Entry Time': entry_time,

                        'Exit Time': exit_time,

                        'Entry Price': entry_price,

                        'Exit Price': exit_price,

                        'SL': sl_price,

                        'Target': target_price,

                        'Status': trade_status

                    })

                    # =========================================
                    # CREATE CHART
                    # =========================================

                    chart_df = day_df.copy()

                    chart_df.set_index('Timestamp', inplace=True)

                    # =====================================================
                    # CREATE FULL-LENGTH MARKERS
                    # =====================================================

                    entry_marker = pd.Series(
                        index=chart_df.index,
                        dtype=float
                    )

                    exit_marker = pd.Series(
                        index=chart_df.index,
                        dtype=float
                    )

                    # =====================================================
                    # ADD ENTRY / EXIT POINTS
                    # =====================================================

                    entry_marker.loc[entry_time] = entry_price

                    exit_marker.loc[exit_time] = exit_price
                    apds = [

                        mpf.make_addplot(
                            entry_marker,
                            type='scatter',
                            markersize=200,
                            marker='^'
                        ),

                        mpf.make_addplot(
                            exit_marker,
                            type='scatter',
                            markersize=200,
                            marker='v'
                        )
                    ]

                    chart_file = f"{CHART_FOLDER}/{date}.png"

                    title = (
                        f"{date} | "
                        f"{trade_status} | "
                        f"Entry: {entry_price} | "
                        f"Exit: {exit_price}"
                    )

                    mpf.plot(
                        chart_df,
                        type='candle',
                        style='charles',
                        title=title,
                        figsize=(14, 7),

                        hlines=dict(
                            hlines=[
                                entry_price,
                                sl_price,
                                target_price
                            ],
                            colors=[
                                'blue',
                                'red',
                                'green'
                            ]
                        ),

                        addplot=apds,

                        savefig=chart_file
                    )

                    print(f"Chart Saved: {chart_file}")

                    trade_taken = True

                    break

# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(trade_results)

results_df.to_csv("hammer_backtest_results.csv", index=False)

print("\nBACKTEST COMPLETE")

print("\nResults saved: hammer_backtest_results.csv")