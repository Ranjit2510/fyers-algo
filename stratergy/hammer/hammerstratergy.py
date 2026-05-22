# ============================================================
# LIVE BANKNIFTY HAMMER STRATEGY WITH AUTO ORDER PLACEMENT
# ============================================================
#
# STRATEGY:
#
# 1. Previous 1 hour fall >= 200 points
# 2. Hammer candle forms on 5-min chart
# 3. Entry ABOVE hammer high
# 4. SL = hammer low
# 5. Target = 1 : 1.5 RR
# 6. ATM Option BUYING
#
# ============================================================

import ssl
import certifi
import pandas as pd
from fyers_apiv3.FyersWebsocket import data_ws
from fyers_apiv3 import fyersModel
from datetime import datetime
import math
import time

# ============================================================
# SSL FIX
# ============================================================

ssl._create_default_https_context = ssl.create_default_context(
    cafile=certifi.where()
)

# ============================================================
# FYERS CREDENTIALS
# ============================================================

client_id = "SJCOD6UFV4-100"

access_token = "SJCOD6UFV4-100:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcURfcmdtV1RCWC1JMUljbHo1cHJ4NUZoak51MzNLU2g1UjJrUXQtRmNreXVoZlRDS0o3VGxEdnlPaEo5ZkNqaUJjczljVFRwbUxOa0Nodld4YzFCMVR3b1AySk9HekhhQTVpUno5cXhIV3F6QTRRWT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2ZmYwMGFmM2Y3ODlkNWNlODQxOGM1NjllMWE1NDhmN2NmZGU2MmRkNjE1NTgzNWY4ODAyZjM3NSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIwNDEyMSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc5NDk2MjAwLCJpYXQiOjE3Nzk0MzIxNjAsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3OTQzMjE2MCwic3ViIjoiYWNjZXNzX3Rva2VuIn0.X8oUJ_bcTsw6p9gP80j1fdCXHcA3G8DrOreLA1W46V8"

# ============================================================
# FYERS API OBJECT
# ============================================================

fyers = fyersModel.FyersModel(
    client_id=client_id,
    token=access_token,
    is_async=False,
    log_path=""
)

# ============================================================
# GLOBAL VARIABLES
# ============================================================

candles_df = pd.DataFrame(columns=[
    'Timestamp',
    'Open',
    'High',
    'Low',
    'Close'
])

current_candle = None
current_interval = None

hammer_detected = False

hammer_high = None
hammer_low = None

entry_price = None
target_price = None
stoploss_price = None

trade_taken = False

# ============================================================
# SETTINGS
# ============================================================

LOT_QTY = 15

RR_RATIO = 1.5

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
# GET ATM OPTION SYMBOL
# ============================================================

def get_atm_option_symbol(spot_price):

    strike = round(spot_price / 100) * 100

    # Example:
    # BANKNIFTY26MAY52500CE

    expiry = "26MAY"

    option_symbol = f"NSE:BANKNIFTY{expiry}{strike}CE"

    return option_symbol

# ============================================================
# PLACE ORDER
# ============================================================

def place_order(symbol):

    data = {
        "symbol": symbol,
        "qty": LOT_QTY,
        "type": 2,                # MARKET ORDER
        "side": 1,                # BUY
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False
    }

    response = fyers.place_order(data=data)

    print("\nORDER RESPONSE:\n")

    print(response)

# ============================================================
# STRATEGY CHECK
# ============================================================

def check_strategy():

    global hammer_detected
    global hammer_high
    global hammer_low
    global entry_price
    global stoploss_price
    global target_price

    if len(candles_df) < 12:
        return

    current = candles_df.iloc[-1]

    previous_1hr = candles_df.iloc[-12:]

    highest_price = previous_1hr['High'].max()

    lowest_price = previous_1hr['Low'].min()

    total_fall = highest_price - lowest_price

    bearish_trend = total_fall >= 200

    hammer_found = is_hammer(
        current['Open'],
        current['High'],
        current['Low'],
        current['Close']
    )

    # ========================================================
    # VALID HAMMER
    # ========================================================

    if bearish_trend and hammer_found:

        hammer_detected = True

        hammer_high = current['High']

        hammer_low = current['Low']

        risk = hammer_high - hammer_low

        entry_price = hammer_high

        stoploss_price = hammer_low

        target_price = hammer_high + (risk * RR_RATIO)

        print("\n")
        print("===================================")
        print("HAMMER DETECTED")
        print("===================================")

        print("Time:", current['Timestamp'])

        print("Hammer High:", hammer_high)

        print("Hammer Low:", hammer_low)

        print("Entry Above:", entry_price)

        print("SL:", stoploss_price)

        print("Target:", target_price)

        print("===================================")

# ============================================================
# CHECK ENTRY
# ============================================================

def check_entry(ltp):

    global hammer_detected
    global trade_taken

    if hammer_detected and not trade_taken:

        # ENTRY ABOVE HAMMER HIGH
        if ltp > entry_price:

            print("\n")
            print("===================================")
            print("ENTRY TRIGGERED")
            print("===================================")

            print("Spot Price:", ltp)

            # ATM OPTION
            option_symbol = get_atm_option_symbol(ltp)

            print("BUYING ATM OPTION:")

            print(option_symbol)

            # PLACE ORDER
            place_order(option_symbol)

            trade_taken = True

# ============================================================
# BUILD 5-MIN CANDLE
# ============================================================

def process_tick(ltp):

    global current_candle
    global current_interval
    global candles_df

    now = datetime.now()

    candle_minute = (now.minute // 5) * 5

    interval = now.replace(
        minute=candle_minute,
        second=0,
        microsecond=0
    )

    # ========================================================
    # FIRST CANDLE
    # ========================================================

    if current_interval is None:

        current_interval = interval

        current_candle = {
            'Timestamp': interval,
            'Open': ltp,
            'High': ltp,
            'Low': ltp,
            'Close': ltp
        }

        return

    # ========================================================
    # UPDATE CANDLE
    # ========================================================

    if interval == current_interval:

        current_candle['High'] = max(
            current_candle['High'],
            ltp
        )

        current_candle['Low'] = min(
            current_candle['Low'],
            ltp
        )

        current_candle['Close'] = ltp

    # ========================================================
    # NEW CANDLE
    # ========================================================

    else:

        candles_df.loc[len(candles_df)] = current_candle

        print("\nNEW 5-MIN CANDLE\n")

        print(current_candle)

        # CHECK STRATEGY
        check_strategy()

        # RESET NEW CANDLE
        current_interval = interval

        current_candle = {
            'Timestamp': interval,
            'Open': ltp,
            'High': ltp,
            'Low': ltp,
            'Close': ltp
        }

# ============================================================
# WEBSOCKET MESSAGE
# ============================================================

def onmessage(message):

    try:

        if 'ltp' in message:

            ltp = float(message['ltp'])

            print("LIVE:", ltp)

            process_tick(ltp)

            check_entry(ltp)

    except Exception as e:

        print("ERROR:", e)

# ============================================================
# CALLBACKS
# ============================================================

def onopen():

    print("WEBSOCKET CONNECTED")

    fyers_socket.subscribe(
        symbols=["NSE:NIFTYBANK-INDEX"],
        data_type="SymbolUpdate"
    )

    fyers_socket.keep_running()

def onerror(message):

    print("ERROR:", message)

def onclose(message):

    print("CLOSED:", message)

# ============================================================
# WEBSOCKET
# ============================================================

fyers_socket = data_ws.FyersDataSocket(

    access_token=access_token,

    log_path="",

    litemode=False,

    write_to_file=False,

    reconnect=True,

    on_connect=onopen,

    on_close=onclose,

    on_error=onerror,

    on_message=onmessage
)

# ============================================================
# START
# ============================================================

fyers_socket.connect()