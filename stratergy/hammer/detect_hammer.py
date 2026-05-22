import pandas as pd
import numpy as np

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("../../data/sensex_5min_data_2020-26.csv")

# Convert timestamp
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

# Avoid divide by zero
df['Body'] = df['Body'].replace(0, 0.01)

# =========================================================
# 1. LONG LOWER REJECTION
# =========================================================
# Lower wick should be at least 2.5x body

df['LongLowerRejection'] = (
    df['LowerWick'] >= (2.5 * df['Body'])
)

# =========================================================
# 2. CLOSE NEAR HIGH
# =========================================================
# Close should be in top 25% of candle

df['CloseNearHigh'] = (
    (df['High'] - df['Close']) <=
    (0.25 * df['CandleRange'])
)

# =========================================================
# 3. SMALL UPPER WICK
# =========================================================

df['SmallUpperWick'] = (
    df['UpperWick'] <= df['Body']
)

# =========================================================
# 4. PREVIOUS BEARISH TREND
# =========================================================
# Last 3 candles should show bearish movement

df['BearishTrend'] = (
    (df['Close'].shift(1) < df['Close'].shift(2)) &
    (df['Close'].shift(2) < df['Close'].shift(3))
)

# =========================================================
# 5. HIGH VOLUME CONFIRMATION
# =========================================================
# Volume > 1.5x average volume of last 20 candles

df['AvgVolume20'] = df['Volume'].rolling(20).mean()

df['HighVolume'] = (
    df['Volume'] > (1.5 * df['AvgVolume20'])
)

# =========================================================
# 6. DEMAND ZONE DETECTION
# =========================================================
# Candle low should be near recent 20-candle low

df['Recent20Low'] = df['Low'].rolling(20).min()

df['AtDemandZone'] = (
    abs(df['Low'] - df['Recent20Low'])
    <= (0.002 * df['Low'])   # within 0.2%
)

# =========================================================
# FINAL INSTITUTIONAL HAMMER
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
# FILTER HAMMER CANDLES
# =========================================================

hammer_df = df[df['InstitutionalHammer'] == True]

# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\nINSTITUTIONAL HAMMERS FOUND:\n")

print(
    hammer_df[
        [
            'Timestamp',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume'
        ]
    ].head(50)
)

# =========================================================
# SAVE TO CSV
# =========================================================

hammer_df.to_csv(
    "institutional_hammers.csv",
    index=False
)

print("\nSaved to institutional_hammers.csv")