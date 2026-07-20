import os
from pymilvus import MilvusClient
from dotenv import load_dotenv

load_dotenv()

uri = os.environ.get("ZILLIZ_URI")
token = os.environ.get("ZILLIZ_TOKEN")

print("uri: ", uri)
print("token: ", token)
print("Is token available: ", bool(token))

if not uri or not token:
    print("===ERROR===")
    print("Token or uri is missing...")
    exit(1)

print("Token and uri is OKAY!!!")

try:
    print("Connection DB...")
    client = MilvusClient(uri=uri, token=token)
    collections = client.list_collections()

    print("Successfully connected DB!!!")
    print("COLLECTIONS: ", collections)
except Exception as e:
    print("===ERROR===")
    print("Error type: ", type(e).__name__)
    print("Error details", str(e))
