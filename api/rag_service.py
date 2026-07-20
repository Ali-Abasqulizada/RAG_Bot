import os
import traceback
from openai import OpenAI

from .hf_conn import get_vector
from .database_conn import search_vector


def answer_legal_query(query: str) -> dict:
    try:
        query_vector = get_vector(query)
        if not query_vector:
            return {
                "answer": "Technical Error: Could not retrieve vector from Hugging Face API.",
                "sources": [],
            }

        search_results = search_vector(query_vector)
        if not search_results:
            return {
                "answer": "Technical Error: Could not retrieve results from the database.",
                "sources": [],
            }

        contexts = []
        sources = []

        for hit in search_results:
            entity = hit.get("entity", {})
            contexts.append(entity.get("text", ""))
            sources.append(
                {
                    "source": entity.get("source", "Unknown"),
                    "page": entity.get("page", "N/A"),
                }
            )

        context_text = "\n\n---\n\n".join(contexts)
        
        prompt = f"""Sən Azərbaycan qanunvericiliyi üzrə ixtisaslaşmış peşəkar hüquq məsləhətçisisən. 
İstifadəçinin sualını cavablandırmaq üçün yalnız aşağıda təqdim olunan sənədlərdən (Kontekst) istifadə et. 
Əgər verilən kontekstdə sualın cavabı yoxdursa, bunu uydurma və sadəcə 'Təqdim olunan sənədlərdə bu barədə məlumat yoxdur' de.

Kontekst:
{context_text}

Sual:
{query}
"""
        messages = [
            {
                "role": "system",
                "content": "Sən peşəkar və köməkçi bir süni intellektsən.",
            },
            {"role": "user", "content": prompt},
        ]

        answer = ""
        groq_success = False

        try:
            print("Attempting to generate answer using Groq API...")
            groq_client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.environ.get("GROQ_API_KEY"),
            )

            groq_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile", messages=messages, temperature=0.1, timeout=10
            )

            answer = groq_response.choices[0].message.content
            groq_success = True
            print("===SUCCESS=== Answer generated via Groq.")
        except Exception as groq_err:
            print("Groq API encountered an error/timeout:", groq_err)
            print("Falling back to Cerebras API...")

        if not groq_success:
            try:
                cerebras_client = OpenAI(
                    base_url="https://api.cerebras.ai/v1",
                    api_key=os.environ.get("CEREBRAS_API_KEY"),
                )

                cerebras_response = cerebras_client.chat.completions.create(
                    model="gpt-oss-120b", messages=messages, temperature=0.1, timeout=15
                )

                answer = cerebras_response.choices[0].message.content
                print("===SUCCESS=== Answer generated via Cerebras.")
            except Exception as cerebras_err:
                print("Cerebras API encountered an error/timeout:", cerebras_err)
                print("Models is not working...")
                
                answer = "System Error!?. Please try again later."

        if "məlumat yoxdur" in answer.lower():
            sources = []

        return {"answer": answer, "sources": sources}

    except Exception as e:
        print("DETAILED ERROR TRACEBACK:")
        print(traceback.format_exc())
        return {"answer": f"Technical Error: {repr(e)}", "sources": []}
