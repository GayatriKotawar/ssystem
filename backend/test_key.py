import os

import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
test_key = os.getenv("GEMINI_API_KEY")

if not test_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

try:
    genai.configure(api_key=test_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say 'Key is Working'")
    print(response.text)
except Exception as e:
    print(f"Connection failed: {e}")
