from fyers_apiv3.FyersWebsocket import data_ws
import json

# =====================================================
# FYERS ACCESS TOKEN
# =====================================================
import ssl
import certifi

ssl._create_default_https_context = ssl.create_default_context(
    cafile=certifi.where()
)
client_id = "SJCOD6UFV4-100"

access_token = "SJCOD6UFV4-100:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcURfcmdtV1RCWC1JMUljbHo1cHJ4NUZoak51MzNLU2g1UjJrUXQtRmNreXVoZlRDS0o3VGxEdnlPaEo5ZkNqaUJjczljVFRwbUxOa0Nodld4YzFCMVR3b1AySk9HekhhQTVpUno5cXhIV3F6QTRRWT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2ZmYwMGFmM2Y3ODlkNWNlODQxOGM1NjllMWE1NDhmN2NmZGU2MmRkNjE1NTgzNWY4ODAyZjM3NSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIwNDEyMSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc5NDk2MjAwLCJpYXQiOjE3Nzk0MzIxNjAsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3OTQzMjE2MCwic3ViIjoiYWNjZXNzX3Rva2VuIn0.X8oUJ_bcTsw6p9gP80j1fdCXHcA3G8DrOreLA1W46V8"

# =====================================================
# SYMBOLS
# =====================================================

symbols = [
    "NSE:NIFTYBANK-INDEX"
]

# =====================================================
# CALLBACK FUNCTION
# =====================================================

def onmessage(message):

    print("\nLIVE TICK RECEIVED:\n")

    print(json.dumps(message, indent=4))

# =====================================================
# ERROR CALLBACK
# =====================================================

def onerror(message):

    print("ERROR:", message)

# =====================================================
# CLOSE CALLBACK
# =====================================================

def onclose(message):

    print("Connection Closed:", message)

# =====================================================
# OPEN CALLBACK
# =====================================================

def onopen():

    print("WebSocket Connected")

    # Subscribe symbols
    fyers.subscribe(
        symbols=symbols,
        data_type="SymbolUpdate"
    )

    fyers.keep_running()

# =====================================================
# CREATE WEBSOCKET
# =====================================================

fyers = data_ws.FyersDataSocket(

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

# =====================================================
# CONNECT
# =====================================================

fyers.connect()
import ssl
print(ssl.OPENSSL_VERSION)