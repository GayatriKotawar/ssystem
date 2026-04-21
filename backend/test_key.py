import google.generativeai as genai

# Paste your key here again
test_key = "AIzaSyDBtY8ZmME_L5-eidHG4aYUlc4EBA9gmMk"


try:
    genai.configure(api_key=test_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Key is Working'")
    print(response.text)
except Exception as e:
    print(f"❌ Connection Failed: {e}")