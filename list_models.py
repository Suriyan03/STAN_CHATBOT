# File: list_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("--- Available Models for Your API Key ---")
    for m in genai.list_models():
      # We only care about models that support the 'generateContent' method
      if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")
    print("-----------------------------------------")

except Exception as e:
    print(f"\nAn error occurred: {e}\n")