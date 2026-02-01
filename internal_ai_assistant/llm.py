# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# MODEL_NAME = "llama-3.1-8b-instant"

# # Read key securely from environment
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# def call_llm(prompt: str) -> str:
#     """
#     Calls Groq Cloud LLaMA API securely using environment variables.
#     """

#     if not GROQ_API_KEY:
#         return "Error: GROQ_API_KEY not found. Please set it in your .env file."

#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": MODEL_NAME,
#         "messages": [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an Internal AI Assistant inside a company. "
#                     "Answer professionally, clearly, and avoid hallucinations."
#                 )
#             },
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.2
#     }

#     try:
#         response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)

#         if response.status_code != 200:
#             return f"LLM Error: {response.text}"

#         return response.json()["choices"][0]["message"]["content"]

#     except Exception as e:
#         return f"LLM Exception: {str(e)}"


import streamlit as st
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

def call_llm(prompt: str) -> str:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not configured."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an Internal AI Assistant inside a company. "
                    "Answer professionally, clearly, and avoid hallucinations."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Exception: {str(e)}"
