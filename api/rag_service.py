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

def answer_legal_query(query: str) -> str:
    try:
        # 1. Sualı vektorlara çevirmək (Hugging Face Cloud API vasitəsilə)
        hf_token = os.environ.get("HF_TOKEN")
        hf_api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-m3"
        
        response = requests.post(
            hf_api_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": query, "options": {"wait_for_model": True}}
        )
        response.raise_for_status()
        
        vector_data = response.json()
        # Bəzən API iç-içə siyahı qaytarır, onu düzəldirik
        query_vector = vector_data[0] if isinstance(vector_data[0], list) else vector_data

        # 2. Vektorla Zilliz (Milvus) bazasında axtarış etmək
        client = MilvusClient(
            uri=os.environ.get("ZILLIZ_URI"),
            token=os.environ.get("ZILLIZ_TOKEN")
        )
        
        # DİQQƏT: Öz Zilliz kolleksiya adınızı bura yazın (məsələn: "legal_docs")
        COLLECTION_NAME = "az_law" 
        
        search_results = client.search(
            collection_name=COLLECTION_NAME,
            data=[query_vector],
            limit=3, # Ən uyğun 3 sənədi tap
            output_fields=["text"] # Langchain adətən mətni "text" adlı sahədə saxlayır
        )

        # Tapılan mətnləri bir araya yığmaq
        contexts = []
        for hits in search_results:
            for hit in hits:
                # Əgər mətniniz başqa addadırsa (məsələn "page_content"), buranı dəyişin
                contexts.append(hit["entity"]["text"]) 
                
        context_text = "\n\n---\n\n".join(contexts)

        # 3. Tapılan məlumatı Cerebras (və ya Groq) süni intellektinə göndərib cavab almaq
        llm_client = OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=os.environ.get("CEREBRAS_API_KEY")
        )
        
        prompt = f"""Sən köməkçi bir hüquq məsləhətçisisən. İstifadəçinin sualına YALNIZ aşağıdakı kontekstdəki məlumatlara əsasən cavab ver.
        
        Kontekst (Bazada tapılan sənədlər):
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

        return llm_response.choices[0].message.content

    except Exception as e:
        return f"Xəta baş verdi: {str(e)}"