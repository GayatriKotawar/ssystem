import os
import json
import re
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

# gemini-2.0-flash supports JSON mode; flash-lite does NOT — use flash
MODEL_ID = "gemini-2.0-flash"

VALID_CATEGORIES = ["Bills", "Medical", "Insurance", "Banking",
                    "Education", "Legal", "Receipts", "Others"]

# ── Keyword fallback categorizer (no API needed) ───────────────────────────
KEYWORD_MAP = {
    "Medical":   ["hospital", "clinic", "doctor", "medicine", "prescription", "diagnosis",
                  "patient", "blood", "test", "report", "health", "pharmacy", "mg", "tablet",
                  "capsule", "injection", "lab", "pathology", "radiology", "x-ray", "scan",
                  "discharge", "admitted", "ward", "opd", "ipd", "pulse", "bp", "sugar",
                  "diabetes", "fever", "treatment", "therapy", "dosage", "symptoms"],
    "Bills":     ["electricity", "water", "gas", "internet", "broadband", "telephone",
                  "utility", "bill", "due date", "meter", "units", "kwh", "consumer no",
                  "connection", "recharge", "mobile", "postpaid", "prepaid"],
    "Insurance": ["insurance", "policy", "premium", "insured", "nominee", "coverage",
                  "claim", "sum assured", "maturity", "lic", "irda", "agent", "beneficiary"],
    "Banking":   ["bank", "account", "transaction", "balance", "debit", "credit", "ifsc",
                  "cheque", "neft", "rtgs", "upi", "statement", "passbook", "loan", "emi",
                  "interest", "savings", "current", "fixed deposit", "fd", "atm"],
    "Education": ["school", "college", "university", "student", "marks", "grade", "result",
                  "certificate", "degree", "diploma", "course", "semester", "examination",
                  "roll number", "admit card", "hall ticket", "scholarship", "fees"],
    "Legal":     ["agreement", "contract", "deed", "affidavit", "court", "legal", "advocate",
                  "lawyer", "notary", "stamp duty", "registration", "power of attorney",
                  "terms and conditions", "clause", "jurisdiction", "plaintiff", "defendant"],
    "Receipts":  ["receipt", "invoice", "order", "purchase", "payment", "paid", "total",
                  "subtotal", "gst", "vat", "tax", "cgst", "sgst", "igst", "hsn",
                  "item", "qty", "quantity", "rate", "discount", "cash", "upi", "card"],
}

def keyword_categorize(text: str) -> str:
    """Fast keyword-based fallback. Returns best matching category or 'Others'."""
    lower = text.lower()
    scores = {cat: 0 for cat in KEYWORD_MAP}
    for cat, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in lower:
                scores[cat] += 1
    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "Others"


def extract_structured_data(
    ocr_text: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> dict:
    """
    Single Gemini call — extracts structured data AND classifies the document.
    Falls back to keyword-based categorization if Gemini fails or misclassifies.
    """
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    valid_cats = ", ".join(VALID_CATEGORIES)

    prompt = f"""You are a smart document analysis assistant. Today's date is {current_date}.

Analyze this document carefully and return a single JSON object.

CATEGORY RULES — pick exactly one:
- "Medical"   → Any hospital bill, prescription, lab report, health record, discharge summary
- "Bills"     → Electricity, water, gas, internet, telephone, utility bills
- "Insurance" → Insurance policy, premium notice, LIC document, claim form
- "Banking"   → Bank statement, passbook, cheque, loan document, FD certificate
- "Education" → School/college fee receipt, mark sheet, certificate, admit card
- "Legal"     → Agreement, contract, affidavit, deed, legal notice
- "Receipts"  → Shopping receipt, invoice, purchase order, GST bill, payment receipt
- "Others"    → Only if the document truly doesn't fit any above category

REQUIRED JSON fields (always include, use empty string if not found):
{{
  "category": "<one of: {valid_cats}>",
  "name": "<person's full name found in document>",
  "date": "<primary date in YYYY-MM-DD format>",
  "amount": "<total amount as number string, e.g. '1500.00', empty if none>",
  "due_date": "<due or expiry date in YYYY-MM-DD, empty if none>",
  "vendor": "<company, hospital, school, shop name>",
  "summary": "<one sentence describing what this document is>"
}}

OPTIONAL fields — add only if found:
"invoice_number", "policy_number", "doctor_name", "medicine", "diagnosis",
"test_results", "tax_amount", "account_number", "bank_name", "course_name", "grade"

{("Document text:" + chr(10) + ocr_text.strip()) if ocr_text.strip() else ""}

IMPORTANT: Return ONLY the raw JSON object. No markdown, no code fences, no extra text."""

    # ── No API key: keyword fallback only ─────────────────────────────────
    if not client:
        cat = keyword_categorize(ocr_text) if ocr_text else "Others"
        return {
            "category": cat,
            "summary": "Document processed using keyword matching (no API key configured).",
            "name": "", "date": "", "amount": "", "due_date": "", "vendor": "",
        }

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
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )

        text = response.text.strip()
        print(f"[Gemini raw] {text[:200]}")

        # Strip markdown fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*```$', '', text)

        # Extract first JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in response: {text[:200]}")

        result = json.loads(match.group(0))

        # Validate + normalise category
        raw_cat = str(result.get("category", "")).strip()
        # Case-insensitive match
        matched = next((c for c in VALID_CATEGORIES if c.lower() == raw_cat.lower()), None)
        if not matched:
            # Keyword fallback on the OCR text / summary
            fallback_text = ocr_text or str(result.get("summary", ""))
            matched = keyword_categorize(fallback_text)
        result["category"] = matched

        # Ensure required fields exist
        for field in ("name", "date", "amount", "due_date", "vendor", "summary"):
            result.setdefault(field, "")

        return result

    except json.JSONDecodeError as e:
        print(f"[ai_extractor] JSON parse error: {e}")
        # Keyword fallback
        cat = keyword_categorize(ocr_text) if ocr_text else "Others"
        return {
            "category": cat,
            "summary": "AI extraction partially failed — categorized by keywords.",
            "name": "", "date": "", "amount": "", "due_date": "", "vendor": "",
            "error": str(e),
        }
    except Exception as e:
        print(f"[ai_extractor] Gemini error: {e}")
        if "429" in str(e):
            cat = keyword_categorize(ocr_text) if ocr_text else "Others"
            return {
                "category": cat,
                "summary": "API rate limit hit — categorized by keywords.",
                "name": "", "date": "", "amount": "", "due_date": "", "vendor": "",
                "error": "quota_exceeded",
            }
        cat = keyword_categorize(ocr_text) if ocr_text else "Others"
        return {
            "category": cat,
            "summary": f"Processing error: {str(e)}",
            "name": "", "date": "", "amount": "", "due_date": "", "vendor": "",
            "error": str(e),
        }
