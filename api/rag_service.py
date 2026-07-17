# import os

# # os.environ["HF_HUB_OFFLINE"] = "1"
# # os.environ["TRANSFORMERS_OFFLINE"] = "1"

# from pymilvus import MilvusClient
# from langchain_core.documents import Document
# from langchain_huggingface import HuggingFaceEndpointEmbeddings

# # from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import (
#     RunnablePassthrough,
#     RunnableParallel,
#     RunnableLambda,
# )
# from langchain_core.output_parsers import StrOutputParser

# # _GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# print("Initializing AI Models and Database Connections...")
# client = MilvusClient(
#     uri=os.environ.get("ZILLIZ_URI"),
#     token=os.environ.get("ZILLIZ_TOKEN"),
# )

# embeddings = HuggingFaceEndpointEmbeddings(
#     model="BAAI/bge-m3",
#     huggingfacehub_api_token=os.environ.get("HF_TOKEN")
# )

# # llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=_GROQ_API_KEY)
# llm = ChatOpenAI(
#     model="gpt-oss-120b",
#     base_url="https://api.cerebras.ai/v1",
#     api_key=os.environ.get("CEREBRAS_API_KEY"),
# )

# def native_milvus_retriever(search_query: str) -> None:
#     query_vector = embeddings.embed_query(search_query)
#     results = client.search(
#         collection_name="az_law",
#         data=[query_vector],
#         limit=6,
#         output_fields=["text", "source", "page"],
#     )

#     docs = []

#     for hit in results[0]:
#         entity = hit["entity"]
#         docs.append(
#             Document(
#                 page_content=entity.get("text", ""),
#                 metadata={
#                     "source": entity.get("source", "Unknown"),
#                     "page": entity.get("page", "N/A"),
#                 },
#             )
#         )

#     return docs


# retiever = RunnableLambda(native_milvus_retriever)

# system_prompt = (
#     "Sən Azərbaycan qanunvericiliyi üzrə ixtisaslaşmış peşəkar hüquq məsləhətçisisən. "
#     "İstifadəçinin sualını cavablandırmaq üçün yalnız aşağıda təqdim olunan sənədlərdən (Kontekst) istifadə et. "
#     "Əgər verilən kontekstdə sualın cavabı yoxdursa, bunu uydurma və sadəcə 'Təqdim olunan sənədlərdə bu barədə məlumat yoxdur' de.\n\n"
#     "Kontekst:\n{context}"
# )

# prompt_template = ChatPromptTemplate.from_messages(
#     [("system", system_prompt), ("human", "{input}")]
# )


# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)


# rag_chain_from_docs = (
#     RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
#     | prompt_template
#     | llm
#     | StrOutputParser()
# )

# rag_chain = RunnableParallel(
#     {"context": retiever, "input": RunnablePassthrough()}
# ).assign(answer=rag_chain_from_docs)


# def answer_legal_query(query: str) -> dict:
#     response = rag_chain.invoke(query)

#     sources = [
#         {
#             "source": doc.metadata.get("source", "Unknown"),
#             "page": doc.metadata.get("page", "N/A"),
#         }
#         for doc in response["context"]
#     ]

#     if "məlumat yoxdur" in response["answer"].lower():
#         sources = []

#     return {"answer": response["answer"], "sources": sources}




import os
import requests
from pymilvus import MilvusClient
from openai import OpenAI
import traceback

def answer_legal_query(query: str) -> dict:
    try:
        # 1. Sualı vektorlara çevirmək (Hugging Face Cloud API vasitəsilə)
        hf_token = os.environ.get("HF_TOKEN")
        hf_api_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/pipeline/feature-extraction"
        
        response = requests.post(
            hf_api_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": query, "options": {"wait_for_model": True}}
        )
        response.raise_for_status()
        
        vector_data = response.json()
        query_vector = vector_data[0] if isinstance(vector_data[0], list) else vector_data
        uri = os.environ.get("ZILLIZ_URI")
        token = os.environ.get("ZILLIZ_TOKEN")
    
    # Əgər dəyişənlər boşdursa, bunu loglarda göstərək
        if not uri or not token:
            print(f"XƏTA: ZILLIZ_URI və ya ZILLIZ_TOKEN tapılmadı! URI: {uri}, Token: {bool(token)}")
            return {"answer": f"Texniki xəta: Konfiqurasiya tapılmadı. XƏTA: ZILLIZ_URI və ya ZILLIZ_TOKEN tapılmadı! URI: {uri}, Token: {bool(token)}", "sources": []}
        # 2. Vektorla Zilliz (Milvus) bazasında axtarış etmək
        client = MilvusClient(
            uri=os.environ.get("ZILLIZ_URI"),
            token=os.environ.get("ZILLIZ_TOKEN")
        )
        
        COLLECTION_NAME = "az_law" 
        
        search_results = client.search(
            collection_name=COLLECTION_NAME,
            data=[query_vector],
            limit=6, # Ən uyğun 6 sənədi tapır (Köhnə tənzimləməyə uyğun)
            output_fields=["text", "source", "page"] # Mənbə və səhifəni də bazadan çəkirik
        )

        contexts = []
        sources = []
        
        for hits in search_results:
            for hit in hits:
                entity = hit["entity"]
                contexts.append(entity.get("text", ""))
                sources.append({
                    "source": entity.get("source", "Unknown"),
                    "page": entity.get("page", "N/A")
                })
                
        context_text = "\n\n---\n\n".join(contexts)

        # 3. Tapılan məlumatı Cerebras AI-a göndərib cavab almaq
        llm_client = OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.environ.get("CEREBRAS_API_KEY")
        )
        
        prompt = f"""Sən Azərbaycan qanunvericiliyi üzrə ixtisaslaşmış peşəkar hüquq məsləhətçisisən. 
İstifadəçinin sualını cavablandırmaq üçün yalnız aşağıda təqdim olunan sənədlərdən (Kontekst) istifadə et. 
Əgər verilən kontekstdə sualın cavabı yoxdursa, bunu uydurma və sadəcə 'Təqdim olunan sənədlərdə bu barədə məlumat yoxdur' de.

Kontekst:
{context_text}

Sual:
{query}
"""

        llm_response = llm_client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {"role": "system", "content": "Sən peşəkar və köməkçi bir süni intellektsən."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = llm_response.choices[0].message.content
        
        # Əgər bazada məlumat tapılmayıbsa mənbələri gizlət
        if "məlumat yoxdur" in answer.lower():
            sources = []

        # Frontend-in tam olaraq gözlədiyi data strukturu
        return {"answer": answer, "sources": sources}

    except Exception as e:
        # Xətanın bütün detallarını Render loglarına yazdırır
        print("XƏTANIN DETALLI TƏHLİLİ:")
        print(traceback.format_exc())
        
        # Ekrandakı mətnə isə xətanın boş qalmayan qəti tipini (repr) qaytarır
        return {"answer": f"Texniki xəta: {repr(e)}", "sources": []}