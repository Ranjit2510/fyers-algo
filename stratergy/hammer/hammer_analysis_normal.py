import pandas as pd

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("../../data/banknifty_5min_data.csv")

# Convert timestamp to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Reset index
df = df.reset_index(drop=True)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_CANDLES = 12      # 12 candles = 1 hour on 5min chart
MIN_FALL_POINTS = 200      # Bearish trend condition
NEXT_CANDLES = 6           # Next 30 mins (6 x 5min candles)

# =========================================================
# RESULT STORAGE
# =========================================================

results = []

# =========================================================
# HAMMER DETECTION FUNCTION
# =========================================================

def is_hammer(open_price, high_price, low_price, close_price):

    body = abs(close_price - open_price)

    upper_wick = high_price - max(open_price, close_price)

    lower_wick = min(open_price, close_price) - low_price

    # Avoid division issue
    if body == 0:
        body = 0.01

    hammer = (
        lower_wick >= 2 * body and
        upper_wick <= body
    )

    return hammer

# =========================================================
# MAIN LOOP
# =========================================================

for i in range(LOOKBACK_CANDLES, len(df) - NEXT_CANDLES):

    current = df.iloc[i]

    # =====================================================
    # PREVIOUS 1 HOUR BEARISH TREND
    # =====================================================

    previous_window = df.iloc[i - LOOKBACK_CANDLES:i]

    highest_price = previous_window['High'].max()

    lowest_price = previous_window['Low'].min()

    total_fall = highest_price - lowest_price

    bearish_trend = total_fall >= MIN_FALL_POINTS

    # =====================================================
    # CHECK HAMMER
    # =====================================================

    hammer_found = is_hammer(
        current['Open'],
        current['High'],
        current['Low'],
        current['Close']
    )

    # =====================================================
    # IF HAMMER AFTER BEARISH TREND
    # =====================================================

    if bearish_trend and hammer_found:

        hammer_high = current['High']
        hammer_low = current['Low']

        entry_price = current['Close']

        # =================================================
        # NEXT 30 MINUTES DATA
        # =================================================

        next_candles = df.iloc[i + 1:i + 1 + NEXT_CANDLES]

        max_move = 0

        sl_hit = False

        sl_hit_time = None

        # =================================================
        # CHECK NEXT CANDLES
        # =================================================

        for _, candle in next_candles.iterrows():

            # SL HIT CONDITION
            if candle['Close'] < hammer_low:

                sl_hit = True
                sl_hit_time = candle['Timestamp']

                break

            # Calculate move after hammer
            move_points = candle['High'] - entry_price

            if move_points > max_move:
                max_move = move_points

        # =================================================
        # STORE RESULT
        # =================================================

        results.append({

            'Hammer Time': current['Timestamp'],

            'Open': current['Open'],
            'High': current['High'],
            'Low': current['Low'],
            'Close': current['Close'],

            'Previous Fall Points': round(total_fall, 2),

            'Max Move Next 30 Min': round(max_move, 2),

            'SL Hit': sl_hit,

            'SL Hit Time': sl_hit_time

        })

# =========================================================
# RESULT DATAFRAME
# =========================================================

result_df = pd.DataFrame(results)

# =========================================================
# PRINT RESULTS
# =========================================================

print("\nHAMMER ANALYSIS RESULTS:\n")

print(result_df.head(20))

# =========================================================
# SAVE CSV
# =========================================================

result_df.to_csv("hammer_strategy_results.csv", index=False)

print("\nResults saved to hammer_strategy_results.csv")