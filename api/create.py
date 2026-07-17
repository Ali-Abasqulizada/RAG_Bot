import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from pymilvus import MilvusClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from tqdm import tqdm

client = MilvusClient(
    uri="https://in03-7cfe653a6914015.serverless.aws-eu-central-1.cloud.zilliz.com",
    token="c3ca6b3a38b4ff1cf97a379aec971766e6f31f1cd532f0275e0c079db5bef2dcf4e5f1ce3417677190842fab698299bfab93d8e5"
)

if client.has_collection(collection_name="az_law"):
    client.drop_collection(collection_name="az_law")

client.create_collection(
    collection_name="az_law", dimension=1024, metric_type="COSINE", auto_id=True
)

base_dir = r"C:\Users\user\Desktop\Docx"
print("Loading legal PDFs...")

pdf_docs = DirectoryLoader(
    base_dir,
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True,
    use_multithreading=True,
).load()

for doc in pdf_docs:
    doc.metadata = {k: v for k, v in doc.metadata.items() if k in {"source", "page"}}
    if "page" in doc.metadata:
        doc.metadata["page"] += 1

chunks = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(pdf_docs)

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3", model_kwargs={"device": "cuda"}
)

print("\nStarting upload using MilvusClient...")
for i in tqdm(range(0, len(chunks), 50), desc="Uploading"):
    batch = chunks[i : i + 50]
    data = [
        {
            "text": d.page_content,
            "vector": embeddings.embed_query(d.page_content),
            **d.metadata,
        }
        for d in batch
    ]
    client.insert(collection_name="az_law", data=data)

print("\n✅ Successfully uploaded PDFs!")
