import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

CATEGORIES = [
    "Bills",
    "Medical",
    "Insurance",
    "Banking",
    "Education",
    "Legal",
    "Receipts",
    "Others"
]

def categorize_document(ocr_text: str, extracted_json: dict = None) -> str:
    """Assigns the document to one of the predefined categories."""
    
    # If the ai_extractor already gave us a category, we could use that,
    # but the instructions specifically separate AI Auto Categorization.
    # We will prompt Gemini specifically for classification.
    
    prompt = f"""
    Classify the following document text into exactly ONE of these categories:
    {", ".join(CATEGORIES)}
    
    Document Text:
    {ocr_text}
    
    Return ONLY the category name. No other text.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        cat = response.text.strip()
        # Verify it's one of the valid categories
        for valid_cat in CATEGORIES:
            if valid_cat.lower() in cat.lower():
                return valid_cat
                
        return "Others"
        
    except Exception as e:
        print(f"Error during Gemini categorization: {e}")
        return "Others"
