from fyers_apiv3 import fyersModel
import pandas as pd
import csv
from datetime import datetime, timedelta

# ==============================
# FYERS CONFIG
# ==============================

client_id = "SJCOD6UFV4-100"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCcUR4eVVvZ1l0d0xrSTgxUkRvaGF4LXdKU0N2bjEyUUZBcjdHRGJfckhZc1JvcWJZTnBsNVZFYWpGZlBXdXBvWElpNng2cFQyMWpPaEhOeTR5T0h3SWRvQzJCaGtnS2RVdW9pNGV5Y2RKQVFtOXFHMD0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI4NzRmNzIxYTMyMGUyMmNkZDVlMWNmYTdiNTAyNGE5YTFhMzYwNTU5NzQyMjIyY2EwOGM4MWVkZiIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWFIwNDEyMSIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzc5NDA5ODAwLCJpYXQiOjE3NzkzNzUyNTIsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc3OTM3NTI1Miwic3ViIjoiYWNjZXNzX3Rva2VuIn0.IjYg9XPp7l_Py8EwoI94TN8N_wc_6AXqVnU1B5NFTEA"

# Create FYERS object
fyers = fyersModel.FyersModel(
    client_id=client_id,
    token=access_token,
    is_async=False,
    log_path=""
)

# ==============================
# SETTINGS
# ==============================

symbol = "BSE:SENSEX-INDEX"   # BankNifty
time_frame = "5"                 # 5 minute candles

from_date = datetime(2017, 1, 1)
to_date = datetime(2020,1,1)

# FYERS allows limited candles per request
max_days_per_call = 100

# Output CSV
file_path = "sensex_5min_data_2017-20.csv"

# ==============================
# CALCULATE API CALLS
# ==============================

total_days = (to_date - from_date).days
num_api_calls = (total_days // max_days_per_call) + 1

print(f"Total API Calls Needed: {num_api_calls}")

# ==============================
# WRITE CSV HEADER
# ==============================

with open(file_path, 'w', newline='') as csvfile:

    writer = csv.writer(csvfile)

    # CSV Header
    writer.writerow([
        'Timestamp',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume'
    ])

    # ==============================
    # LOOP API CALLS
    # ==============================

    for api_call in range(num_api_calls):

        # Calculate date ranges
        start_date = from_date + timedelta(days=api_call * max_days_per_call)

        end_date = min(
            to_date,
            start_date + timedelta(days=max_days_per_call - 1)
        )

        print(f"\nFetching Data:")
        print(f"FROM: {start_date.date()} TO: {end_date.date()}")

        # ==============================
        # API REQUEST DATA
        # ==============================

        data = {
            "symbol": symbol,
            "resolution": time_frame,
            "date_format": "1",
            "range_from": start_date.strftime('%Y-%m-%d'),
            "range_to": end_date.strftime('%Y-%m-%d'),
            "cont_flag": "1"
        }

        # ==============================
        # FETCH DATA
        # ==============================

        try:

            historical_response = fyers.history(data=data)

            # Check API response
            if 'candles' not in historical_response:
                print("No candles found")
                print(historical_response)
                continue

            candles = historical_response['candles']

            print(f"Received {len(candles)} candles")

            # ==============================
            # PROCESS EACH CANDLE
            # ==============================

            for candle in candles:

                # Candle format:
                # [timestamp, open, high, low, close, volume]

                epoch_time = candle[0]

                # Convert epoch to readable datetime
                timestamp = datetime.fromtimestamp(
                    epoch_time
                ).strftime('%Y-%m-%d %H:%M:%S')

                # Replace epoch with readable timestamp
                candle[0] = timestamp

                # Write to CSV
                writer.writerow(candle)

        except Exception as e:
            print("ERROR:", e)

print("\nData Download Complete!")
print(f"Saved File: {file_path}")