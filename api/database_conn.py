import os
from pymilvus import MilvusClient

##### If we wanted to test this file separately. #####
# from dotenv import load_dotenv
# load_dotenv()


def search_vector(
    query_vector: list, collection_name: str = "az_law", limit: int = 6
) -> list:

    uri = os.environ.get("ZILLIZ_URI")
    token = os.environ.get("ZILLIZ_TOKEN")

    if not uri or not token:
        print("===ERROR===")
        print("ZILLIZ_URI or ZILLIZ_TOKEN is missing...")
        return None

    try:
        print("Connecting to DB and searching in collection:", collection_name)
        client = MilvusClient(uri=uri, token=token)

        search_results = client.search(
            collection_name=collection_name,
            data=[query_vector],
            limit=limit,
            output_fields=["text", "source"],
        )

        print("===SUCCESS===")
        print(f"Retrieved {len(search_results[0])} results from the database.")

        return search_results[0]
    except Exception as e:
        print("===ERROR===")
        print("Error type: ", type(e).__name__)
        print("Error details: ", str(e))
        return None


##### For testing purposes #####
# dummy_vector = [0.1] * 1024

# results = search_vector(dummy_vector, limit=3)

# if results:
#     print("Top Result ID:", results[0].get("id"))
#     print("Top Result Distance/Score:", results[0].get("distance"))
#     print("Top Result Entity:", results[0].get("entity"))
