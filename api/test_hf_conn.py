import os
import requests
from dotenv import load_dotenv

load_dotenv()

hf_token = os.environ.get("HF_TOKEN")
hf_api_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/pipeline/feature-extraction"

print('hf_token: ', hf_token)

if not hf_token:
    print("===ERROR===")
    print("Hf_token is missing...")
    exit(1)
    
try:
    print("Sending request to Hugging Face API...")
    response = requests.post(
        hf_api_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": "Test query for connection check", "options": {"wait_for_model": True}},
        timeout=15
    )
    
    print("Response Status Code: ", response.status_code)
    
    if response.status_code == 200:
        print("Successfully connected to Hugging Face Api...")
        data = response.json()
        print("Success: ", len(data) if isinstance(data, list) else "Data received")
    else:
        print("===ERROR===")
        print("API error: ", response.status_code)
        print("Error response: ", response.text)
except Exception as e:
    print("===ERROR===")
    print("Error type: ", type(e).__name__)
    print("Error details", str(e))