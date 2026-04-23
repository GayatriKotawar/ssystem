import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import Optional, Any

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found. Document processing will be disabled.")
    client = None
else:
    client = genai.Client(api_key=api_key)

# Use Flash-Lite: faster response times, lower latency, sufficient for extraction
MODEL_ID = "gemini-2.0-flash-lite"

VALID_CATEGORIES = ["Bills", "Medical", "Insurance", "Banking",
                    "Education", "Legal", "Receipts", "Others"]

def extract_structured_data(
    ocr_text: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Single Gemini call that extracts structured data AND classifies the document.
    - If image_bytes provided → Gemini Vision reads image directly (no OCR needed).
    - If only ocr_text provided → text-only extraction (fast for text PDFs).
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")

    valid_cats = ", ".join(VALID_CATEGORIES)

    prompt = f"""You are a smart document analysis assistant. Today's date is {current_date}.

Analyze the document {'image' if image_bytes else 'text'} below and return a SINGLE JSON object.

REQUIRED fields (include even if empty string):
- "category": one of [{valid_cats}]
- "name": person's full name
- "date": primary date in YYYY-MM-DD format
- "amount": numeric amount (e.g. "1500.00"), empty string if none
- "due_date": due/expiry date in YYYY-MM-DD format, empty if none
- "vendor": company/hospital/institution name
- "summary": one plain-English sentence summarizing the document

OPTIONAL fields (only include if found in document):
- "invoice_number", "policy_number", "doctor_name", "medicine",
  "diagnosis", "test_results", "tax_amount", "discount", "patient_id",
  "account_number", "bank_name", "course_name", "grade", "alert"

{"Document text:" + chr(10) + ocr_text if ocr_text.strip() else ""}

Return ONLY raw JSON. No markdown, no code blocks, no explanation."""

    if not client:
        return {"error": "API key not configured", "category": "Others",
                "summary": "Document processing is disabled — no Gemini API key set."}

    try:
        contents: list[Any] = [prompt]
        if image_bytes and mime_type:
            contents.append(
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            )

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,     # Low temperature = deterministic, structured output
                max_output_tokens=1024,
            ),
        )

        text = response.text.strip()

        # Strip potential markdown fences just in case
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        result = json.loads(text.strip())

        # Normalize category
        raw_cat = str(result.get("category", "")).strip()
        if raw_cat not in VALID_CATEGORIES:
            raw_cat = "Others"
        result["category"] = raw_cat

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e} | Raw: {locals().get('text', '')}")
        return {"category": "Others", "summary": "Could not parse AI response.", "error": str(e)}
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        if "429" in str(e):
            return {"category": "Others", "summary": "API rate limit hit. Please wait 60 seconds and try again.", "error": "quota_exceeded"}
        return {"category": "Others", "summary": f"Processing error: {str(e)}", "error": str(e)}
