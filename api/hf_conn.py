import os
import requests

##### If we wanted to test this file seperately. #####
# from dotenv import load_dotenv
# load_dotenv()


def get_vector(query: str) -> list:
    hf_token = os.environ.get("HF_TOKEN")
    hf_api_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/pipeline/feature-extraction"

    if not hf_token:
        print("===ERROR===")
        print("HF_TOKEN is missing...")
        return None

    try:
        print("Sending request to Hugging Face API for query:", query)
        response = requests.post(
            hf_api_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": query, "options": {"wait_for_model": True}},
            timeout=15,
        )

        if response.status_code == 200:
            print("Successfully connected to Hugging Face API...")
            data = response.json()
            vector = (
                data[0]
                if isinstance(data, list) and isinstance(data[0], list)
                else data
            )
            return vector

        else:
            print("===ERROR===")
            print("API error: ", response.status_code)
            print("Error response: ", response.text)
            return None

    except Exception as e:
        print("===ERROR===")
        print("Error type: ", type(e).__name__)
        print("Error details: ", str(e))
        return None


##### For testing purpose #####
# test_query = "Why RAG is so importand to us?"
# vector_result = get_vector(test_query)

# if vector_result:
#     print("\n===SUCCESS===")
#     print(f"Vector retrieved! Length of vector: {len(vector_result)}")
