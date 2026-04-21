import os
import json
import re
from google import genai
from dotenv import load_dotenv

# Load key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class DocumentProcessor:
    def __init__(self):
        # Initialize the 2026 Unified Client
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        # Using 2.0 Flash-Lite for higher quota and multimodal vision support
        self.model_id = "gemini-2.0-flash-lite"

    def analyze_with_ai(self, image_bytes):
        """
        Processes the raw image bytes directly using Gemini Vision.
        This is far more accurate for tables and medical records than text-only OCR.
        """
        
        prompt = """
        Analyze this document image and extract detailed information into a JSON format.
        
        CRITICAL INSTRUCTIONS:
        1. Identify the 'category' (Medical, Education, Bills, Legal, or Receipt).
        2. Find the 'participant_name' (e.g., Patient Name, Student Name).
        3. Identify the 'organization' (Hospital name, College name, or Shop name).
        4. If Medical: Extract symptoms, findings, and prescriptions into 'medical_safety'.
        5. If Education: Extract event names and signatories.
        
        RETURN ONLY RAW JSON in this structure:
        {
            "category": "Category Name",
            "plain_language": "One-sentence simple summary",
            "extracted_data": {
                "participant_name": "Full Name",
                "event_name": "Specific event/Consultation reason",
                "organization": "Institute Name",
                "signatories": ["Names of doctors/officials"],
                "dates": ["All dates found"],
                "amounts": [0.0]
            },
            "panic_alert": "Urgency/Warning message",
            "emotion_support": "A supportive or congratulatory message",
            "medical_safety": "Detailed clinical notes or findings",
            "legal_risk": "Any contract risks identified"
        }
        """

        try:
            # Sending both the image and the prompt to Gemini
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    # New: Send the image bytes directly as a 'part'
                    {"mime_type": "image/jpeg", "data": image_bytes}
                ],
                config={'response_mime_type': 'application/json'}
            )
            
            # Use regex to ensure we only get the JSON block
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("AI did not return valid JSON")
                
        except Exception as e:
            if "429" in str(e):
                return {"category": "Quota Error", "plain_language": "API limit reached. Wait 60 seconds."}
            print(f"DEBUG ERROR: {e}")
            return {"category": "Error", "plain_language": f"Processing failed: {str(e)}"}