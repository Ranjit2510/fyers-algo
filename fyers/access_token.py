from fyers_apiv3 import fyersModel

client_id = "SJCOD6UFV4-100"
secret_key = "HQ9AYWSHGQ"
redirect_uri = "http://127.0.0.1"
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJTSkNPRDZVRlY0IiwidXVpZCI6IjIxODAwOWVkYTYxNDRhZTY5NzY2OTY0NGQ2NTQ3NTU5IiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhSMDQxMjEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI2ZmYwMGFmM2Y3ODlkNWNlODQxOGM1NjllMWE1NDhmN2NmZGU2MmRkNjE1NTgzNWY4ODAyZjM3NSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzg1NzE2NjkxLCJpYXQiOjE3ODU2ODY2OTEsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc4NTY4NjY5MSwic3ViIjoiYXV0aF9jb2RlIn0.Of0y2Pz-QhFEw3ElYLUwhL3LbckZaCiwhyRONXQlwbo"

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