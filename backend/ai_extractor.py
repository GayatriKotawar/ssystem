import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# We need a fallback or clear error if API key is missing
api_key = os.getenv("GEMINI_API_KEY") 
if not api_key:
    # For testing purposes, we'll initialize without API key and handle errors gracefully
    print("WARNING: GEMINI_API_KEY not found. Document processing will be disabled.")
    client = None
else:
    client = genai.Client(api_key=api_key)

from typing import Optional, Any

def extract_structured_data(ocr_text: str, image_bytes: Optional[bytes] = None, mime_type: Optional[str] = None) -> dict:
    """Uses Gemini 2.0 Flash Lite to extract structured data from OCR text."""
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Extract structured information from this document.
    Current System Date is: {current_date}. 
    Return JSON only without Markdown formatting blocks (e.g., no ```json).
    
    Extract the following standard fields (only if available, otherwise omit them):
    - name, date (YYYY-MM-DD), amount, due_date, policy_number, expiry_date, vendor, doctor_name, medicine, test_results, category
    
    IMPORTANT: You are highly encouraged to extract ANY AND ALL other relevant data points found in the document using concise, snake_case keys (e.g., patient_id, diagnosis, invoice_number, tax_amount). If the document is a prescription or medical report, vigorously extract symptoms, vitals, prescriptions, etc.

    OCR Text (may contain errors, use the provided original image as the primary source of truth if available):
    {ocr_text}
    
    Return pure JSON format. Example output:
    {{
      "name": "Rahul Sharma",
      "date": "2025-02-12",
      "amount": "2450",
      "due_date": "",
      "policy_number": "",
      "expiry_date": "",
      "vendor": "Apollo Pharmacy",
      "doctor_name": "",
      "medicine": "Paracetamol",
      "test_results": "",
      "category": "Medical"
    }}
    """
    
    if not client:
        print("Document processing disabled - no API key configured")
        return {"error": "API key not configured", "message": "Document processing is disabled"}
    
    try:
        from google.genai import types
        contents: list[Any] = [prompt]
        if image_bytes and mime_type:
            contents.append(
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            )

        # Use gemini-2.5-flash as the latest standard flash logic model
        print("Sending payload to Gemini 2.5 Flash...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
        )
        
        # Clean potential markdown wrapping
        text = response.text.strip()
        print(f"Gemini Raw Response: {text}")
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
        
    except Exception as e:
        print(f"Error during Gemini extraction: {e}")
        try:
            print(f"Failed Response Text: {response.text}")
        except:
            pass
        return {}
