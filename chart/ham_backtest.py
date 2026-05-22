import pandas as pd

# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "data/banknifty_5min_data.csv"

OUTPUT_FILE = "chart/hammer_backtest_results.csv"

LOOKBACK_CANDLES = 12

MIN_FALL = 200

RR_RATIO = 1.5

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

    # Avoid divide-by-zero
    if body == 0:
        body = 0.01

    hammer = (
        lower_wick >= 2 * body and
        upper_wick <= body
    )

    return hammer

# ============================================================
# RESULTS STORAGE
# ============================================================

results = []

# ============================================================
# PROCESS DAY-WISE
# ============================================================

grouped = df.groupby('Date')

# ============================================================
# MAIN LOOP
# ============================================================

for date, day_df in grouped:

    day_df = day_df.reset_index(drop=True)

    # Skip small trading days
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

        # ====================================================
        # VALID HAMMER
        # ====================================================

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

                    exit_price = None
                    exit_time = None

                    sl_hit = False

                    target_hit = False

                    trade_status = None

                    # =========================================
                    # CHECK TRADE
                    # =========================================

                    for k in range(j, len(day_df)):

                        trade_candle = day_df.iloc[k]

                        # TARGET HIT
                        if trade_candle['High'] >= target_price:

                            exit_price = target_price

                            exit_time = trade_candle['Timestamp']

                            target_hit = True

                            trade_status = "TARGET HIT"

                            break

                        # SL HIT
                        if trade_candle['Low'] <= sl_price:

                            exit_price = sl_price

                            exit_time = trade_candle['Timestamp']

                            sl_hit = True

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
                    # POINTS CAPTURED
                    # =========================================

                    points = round(
                        exit_price - entry_price,
                        2
                    )

                    # Negative if SL
                    if sl_hit:
                        points = -abs(points)

                    # =========================================
                    # SAVE RESULT
                    # =========================================

                    results.append({

                        'Date': date,

                        'Hammer Time': current['Timestamp'],

                        'Entry Time': entry_time,

                        'Entry Price': round(entry_price, 2),

                        'SL Price': round(sl_price, 2),

                        'Target Price': round(target_price, 2),

                        'Exit Time': exit_time,

                        'Exit Price': round(exit_price, 2),

                        'SL Hit': sl_hit,

                        'Target Hit': target_hit,

                        'Trade Status': trade_status,

                        'Points Captured': round(points, 2)

                    })

                    print("\nTRADE FOUND")

                    print(f"Date: {date}")

                    print(f"Status: {trade_status}")

                    print(f"Points: {points}")

                    trade_taken = True

                    break

# ============================================================
# CREATE FINAL DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)

# ============================================================
# SAVE CSV
# ============================================================

results_df.to_csv(OUTPUT_FILE, index=False)

# ============================================================
# SUMMARY
# ============================================================

total_trades = len(results_df)

wins = len(results_df[
    results_df['Target Hit'] == True
])

losses = len(results_df[
    results_df['SL Hit'] == True
])

total_points = results_df['Points Captured'].sum()

win_rate = 0

if total_trades > 0:

    win_rate = round(
        (wins / total_trades) * 100,
        2
    )

# ============================================================
# PRINT SUMMARY
# ============================================================

print("\n===================================")
print("BACKTEST SUMMARY")
print("===================================")

print(f"Total Trades: {total_trades}")

print(f"Wins: {wins}")

print(f"Losses: {losses}")

print(f"Win Rate: {win_rate}%")

print(f"Total Points: {round(total_points, 2)}")

print("===================================")

print(f"\nResults saved to: {OUTPUT_FILE}")