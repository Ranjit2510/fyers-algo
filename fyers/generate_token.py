from fyers_apiv3 import fyersModel
import webbrowser

client_id = "SJCOD6UFV4-100"
secret_key = "HQ9AYWSHGQ"
redirect_uri = "http://127.0.0.1"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type="code",
    grant_type="authorization_code"
)
# Generate login URL
response = session.generate_authcode()

print("Open this URL in browser:")
print(response)