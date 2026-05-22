from fyers_apiv3 import fyersModel

client_id = "SJCOD6UFV4-100"
secret_key = "HQ9AYWSHGQ"
redirect_uri = "http://127.0.0.1"
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJTSkNPRDZVRlY0IiwidXVpZCI6ImZiYjM5YjMzNjM0NDQzY2E5MjZjNTAyZWUzMGUyMjZiIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhSMDQxMjEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2ZmYwMGFmM2Y3ODlkNWNlODQxOGM1NjllMWE1NDhmN2NmZGU2MmRkNjE1NTgzNWY4ODAyZjM3NSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzc5NDYxNjkyLCJpYXQiOjE3Nzk0MzE2OTIsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc3OTQzMTY5Miwic3ViIjoiYXV0aF9jb2RlIn0.jluZIs4LkC019fn6_eJj42bkQDNFNzZHuNLvsa_c5Cs"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type="code",
    grant_type="authorization_code"
)

session.set_token(auth_code)

response = session.generate_token()

print(response)