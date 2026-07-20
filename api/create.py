import os
import time
import requests
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from tqdm import tqdm

load_dotenv()

ZILLIZ_URI = os.environ.get("ZILLIZ_URI")
ZILLIZ_TOKEN = os.environ.get("ZILLIZ_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not ZILLIZ_URI or not ZILLIZ_TOKEN:
    raise ValueError("Missing 'ZILLIZ_URI' or 'ZILLIZ_TOKEN' in environment variables.")

if not HF_TOKEN:
    raise ValueError("Missing 'HF_TOKEN' in environment variables.")

HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/pipeline/feature-extraction"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def get_hf_embeddings(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": texts, "options": {"wait_for_model": True}},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API Error ({response.status_code}): {response.text}")
    return response.json()

print("Connecting to Zilliz Database...")
client = MilvusClient(uri=ZILLIZ_URI, token=ZILLIZ_TOKEN)

COLLECTION_NAME = "az_law"

if client.has_collection(collection_name=COLLECTION_NAME):
    print(f"Dropping existing collection '{COLLECTION_NAME}'...")
    client.drop_collection(collection_name=COLLECTION_NAME)

print(f"Creating collection '{COLLECTION_NAME}'...")
client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=1024,
    metric_type="COSINE",
    auto_id=True,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
base_dir = os.environ.get("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))

if not os.path.exists(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    print(f"Created folder: '{base_dir}'. Place your PDF files here.")

print(f"Loading legal PDFs from '{base_dir}'...")

pdf_docs = DirectoryLoader(
    base_dir,
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True,
    use_multithreading=True,
).load()

if not pdf_docs:
    print("No PDF files found in the directory.")
    exit(0)

for doc in pdf_docs:
    doc.metadata = {k: v for k, v in doc.metadata.items() if k in {"source", "page"}}
    if "page" in doc.metadata:
        doc.metadata["page"] += 1
    if "source" in doc.metadata:
        doc.metadata["source"] = os.path.basename(doc.metadata["source"])

chunks = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(pdf_docs)

print(f"\nProcessing {len(chunks)} text chunks...")

BATCH_SIZE = 16

for i in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Uploading to Zilliz"):
    batch = chunks[i : i + BATCH_SIZE]
    texts = [d.page_content for d in batch]

    embeddings = None
    for attempt in range(3):
        try:
            embeddings = get_hf_embeddings(texts)
            break
        except Exception as err:
            if attempt == 2:
                raise err
            time.sleep(2)

    data = [
        {
            "text": d.page_content,
            "vector": embedding,
            **d.metadata,
        }
        for d, embedding in zip(batch, embeddings)
    ]
    client.insert(collection_name=COLLECTION_NAME, data=data)

print("Successfully embedded and uploaded all PDFs to Zilliz!")