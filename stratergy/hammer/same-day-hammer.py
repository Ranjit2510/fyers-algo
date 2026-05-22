import pandas as pd
from datetime import time

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("../../data/banknifty_5min_data.csv")

# Convert timestamp to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# =========================================================
# FILTER ONLY MARKET HOURS
# =========================================================

MARKET_START = time(9, 15)
MARKET_END = time(15, 25)

df = df[
    (df['Timestamp'].dt.time >= MARKET_START) &
    (df['Timestamp'].dt.time <= MARKET_END)
]

# =========================================================
# EXTRACT DATE
# =========================================================

df['Date'] = df['Timestamp'].dt.date

# Reset index
df = df.reset_index(drop=True)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_CANDLES = 12      # 1 hour
MIN_FALL_POINTS = 200
NEXT_CANDLES = 6           # Next 30 mins

# =========================================================
# HAMMER DETECTION
# =========================================================

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

# =========================================================
# RESULTS
# =========================================================

results = []

# =========================================================
# GROUP DATA DAY-WISE
# =========================================================

grouped = df.groupby('Date')

# =========================================================
# PROCESS EACH DAY SEPARATELY
# =========================================================

for date, day_df in grouped:

    # Reset day index
    day_df = day_df.reset_index(drop=True)

    # Skip small days
    if len(day_df) < LOOKBACK_CANDLES + NEXT_CANDLES:
        continue

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for i in range(LOOKBACK_CANDLES, len(day_df) - NEXT_CANDLES):

        current = day_df.iloc[i]

        # =================================================
        # PREVIOUS 1 HOUR DATA (ONLY SAME DAY)
        # =================================================

        previous_window = day_df.iloc[i - LOOKBACK_CANDLES:i]

        highest_price = previous_window['High'].max()

        lowest_price = previous_window['Low'].min()

        total_fall = highest_price - lowest_price

        bearish_trend = total_fall >= MIN_FALL_POINTS

        # =================================================
        # HAMMER CHECK
        # =================================================

        hammer_found = is_hammer(
            current['Open'],
            current['High'],
            current['Low'],
            current['Close']
        )

        # =================================================
        # VALID SETUP
        # =================================================

        if bearish_trend and hammer_found:

            hammer_high = current['High']
            hammer_low = current['Low']

            entry_price = current['Close']

            # =============================================
            # NEXT 30 MIN DATA
            # =============================================

            next_candles = day_df.iloc[i + 1:i + 1 + NEXT_CANDLES]

            max_move = 0

            sl_hit = False

            sl_hit_time = None

            # =============================================
            # CHECK NEXT CANDLES
            # =============================================

            for _, candle in next_candles.iterrows():

                # SL HIT
                if candle['Close'] < hammer_low:

                    sl_hit = True
                    sl_hit_time = candle['Timestamp']

                    break

                # Max upward move
                move_points = candle['High'] - entry_price

                if move_points > max_move:
                    max_move = move_points

            # =============================================
            # SAVE RESULT
            # =============================================

            results.append({

                'Date': date,

                'Hammer Time': current['Timestamp'],

                'Open': current['Open'],
                'High': current['High'],
                'Low': current['Low'],
                'Close': current['Close'],

                'Previous 1Hr Fall': round(total_fall, 2),

                'Max Move Next 30 Min': round(max_move, 2),

                'SL Hit': sl_hit,

                'SL Hit Time': sl_hit_time

            })

# =========================================================
# FINAL DATAFRAME
# =========================================================

result_df = pd.DataFrame(results)

# =========================================================
# PRINT RESULTS
# =========================================================

print("\nHAMMER STRATEGY RESULTS:\n")

print(result_df.head(20))

# =========================================================
# SAVE CSV
# =========================================================


result_df.to_csv("result/hammer_strategy_results.csv", index=False)

print("\nResults saved to hammer_strategy_results.csv")