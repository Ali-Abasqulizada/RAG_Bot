import os

# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"

from pymilvus import MilvusClient
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEndpointEmbeddings

# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.output_parsers import StrOutputParser

# _GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

print("Initializing AI Models and Database Connections...")
client = MilvusClient(
    uri=os.environ.get("ZILLIZ_URI"),
    token=os.environ.get("ZILLIZ_TOKEN"),
)

embeddings = HuggingFaceEndpointEmbeddings(
    model="BAAI/bge-m3",
    huggingfacehub_api_token=os.environ.get("HF_TOKEN")
)

# llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=_GROQ_API_KEY)
llm = ChatOpenAI(
    model="gpt-oss-120b",
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)

def native_milvus_retriever(search_query: str) -> None:
    query_vector = embeddings.embed_query(search_query)
    results = client.search(
        collection_name="az_law",
        data=[query_vector],
        limit=6,
        output_fields=["text", "source", "page"],
    )

    docs = []

    for hit in results[0]:
        entity = hit["entity"]
        docs.append(
            Document(
                page_content=entity.get("text", ""),
                metadata={
                    "source": entity.get("source", "Unknown"),
                    "page": entity.get("page", "N/A"),
                },
            )
        )

    return docs


retiever = RunnableLambda(native_milvus_retriever)

system_prompt = (
    "Sən Azərbaycan qanunvericiliyi üzrə ixtisaslaşmış peşəkar hüquq məsləhətçisisən. "
    "İstifadəçinin sualını cavablandırmaq üçün yalnız aşağıda təqdim olunan sənədlərdən (Kontekst) istifadə et. "
    "Əgər verilən kontekstdə sualın cavabı yoxdursa, bunu uydurma və sadəcə 'Təqdim olunan sənədlərdə bu barədə məlumat yoxdur' de.\n\n"
    "Kontekst:\n{context}"
)

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("human", "{input}")]
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain_from_docs = (
    RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
    | prompt_template
    | llm
    | StrOutputParser()
)

rag_chain = RunnableParallel(
    {"context": retiever, "input": RunnablePassthrough()}
).assign(answer=rag_chain_from_docs)


def answer_legal_query(query: str) -> dict:
    response = rag_chain.invoke(query)

    sources = [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "N/A"),
        }
        for doc in response["context"]
    ]

    if "məlumat yoxdur" in response["answer"].lower():
        sources = []

    return {"answer": response["answer"], "sources": sources}
