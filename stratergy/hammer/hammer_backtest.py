import pandas as pd
import numpy as np

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("../../data/banknifty_5min_data.csv")

df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# =========================================================
# BASIC CANDLE CALCULATIONS
# =========================================================

df['Body'] = abs(df['Close'] - df['Open'])

df['UpperWick'] = (
    df['High'] - df[['Open', 'Close']].max(axis=1)
)

df['LowerWick'] = (
    df[['Open', 'Close']].min(axis=1) - df['Low']
)

df['CandleRange'] = df['High'] - df['Low']

df['Body'] = df['Body'].replace(0, 0.01)

# =========================================================
# INSTITUTIONAL HAMMER CONDITIONS
# =========================================================

# 1. Long lower rejection
df['LongLowerRejection'] = (
    df['LowerWick'] >= (2.5 * df['Body'])
)

# 2. Close near high
df['CloseNearHigh'] = (
    (df['High'] - df['Close']) <=
    (0.25 * df['CandleRange'])
)

# 3. Small upper wick
df['SmallUpperWick'] = (
    df['UpperWick'] <= df['Body']
)

# 4. Previous bearish trend
df['BearishTrend'] = (
    (df['Close'].shift(1) < df['Close'].shift(2)) &
    (df['Close'].shift(2) < df['Close'].shift(3))
)

# 5. High volume confirmation
df['AvgVolume20'] = df['Volume'].rolling(20).mean()

df['HighVolume'] = (
    df['Volume'] > (1.5 * df['AvgVolume20'])
)

# 6. Demand zone
df['Recent20Low'] = df['Low'].rolling(20).min()

df['AtDemandZone'] = (
    abs(df['Low'] - df['Recent20Low'])
    <= (0.002 * df['Low'])
)

# =========================================================
# FINAL HAMMER SIGNAL
# =========================================================

df['InstitutionalHammer'] = (

    df['LongLowerRejection'] &

    df['CloseNearHigh'] &

    df['SmallUpperWick'] &

    df['BearishTrend'] &

    df['HighVolume'] &

    df['AtDemandZone']
)

# =========================================================
# ANALYZE NEXT 30 MIN MOVE
# =========================================================

results = []

for i in range(len(df)):

    if df.loc[i, 'InstitutionalHammer']:

        hammer_time = df.loc[i, 'Timestamp']

        hammer_high = df.loc[i, 'High']

        hammer_low = df.loc[i, 'Low']

        hammer_close = df.loc[i, 'Close']

        # =================================================
        # CHECK NEXT 6 CANDLES (30 mins on 5-min chart)
        # =================================================

        future_data = df.iloc[i + 1:i + 7]

        if len(future_data) == 0:
            continue

        # =================================================
        # STOPLOSS LOGIC
        # =================================================
        # If any candle closes below hammer low
        # SL HIT
        # =================================================

        sl_hit = False

        sl_hit_time = None

        for _, row in future_data.iterrows():

            if row['Close'] < hammer_low:

                sl_hit = True

                sl_hit_time = row['Timestamp']

                break

        # =================================================
        # MAX MOVE CALCULATION
        # =================================================

        max_high = future_data['High'].max()

        points_moved = max_high - hammer_close

        # =================================================
        # SAVE RESULT
        # =================================================

        results.append({

            'HammerTime': hammer_time,

            'HammerClose': hammer_close,

            'HammerHigh': hammer_high,

            'HammerLow': hammer_low,

            'MaxMoveNext30Min': round(points_moved, 2),

            'SL_Hit': sl_hit,

            'SL_Hit_Time': sl_hit_time

        })

# =========================================================
# CREATE RESULTS DATAFRAME
# =========================================================

results_df = pd.DataFrame(results)

# =========================================================
# PRINT RESULTS
# =========================================================

print("\nHAMMER ANALYSIS RESULTS:\n")

print(results_df.head(50))

# =========================================================
# SAVE CSV
# =========================================================

results_df.to_csv(
    "hammer_30min_analysis.csv",
    index=False
)

print("\nSaved to hammer_30min_analysis.csv")