"""
Optimized workflow: Skip EasyOCR entirely for images.
For images → send directly to Gemini Vision (faster, more accurate).
For PDFs → extract text with PyMuPDF first (fast, no OCR needed for text PDFs),
           fall back to Gemini Vision only if the PDF has no selectable text.
Also: categorization is now done inside the single Gemini call (no second API request).
"""

def process_upload(uploaded_file, user_id: int):
    """
    Optimized pipeline:
    1. For images  → send directly to Gemini Vision (skip EasyOCR entirely).
    2. For PDFs    → try fast text extraction with PyMuPDF first.
                     If no text found, render first page and send to Gemini Vision.
    3. Gemini returns both extracted data AND category in ONE call.
    4. Save to database.
    """
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name
    file_extension = filename.split('.')[-1].lower()

    from ai_extractor import extract_structured_data
    from database import save_document

    if file_extension in ('jpg', 'jpeg', 'png', 'webp'):
        # ── FAST PATH: send image bytes directly to Gemini Vision ──────────
        mime_type = f"image/{'jpeg' if file_extension in ('jpg', 'jpeg') else file_extension}"
        structured_data = extract_structured_data(
            ocr_text="",          # Gemini Vision will read the image directly
            image_bytes=file_bytes,
            mime_type=mime_type,
        )

    elif file_extension == 'pdf':
        # ── PDF PATH: try native text extraction first (instant) ────────────
        import pymupdf
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        raw_text = ""
        for page in doc:
            raw_text += page.get_text()

        if raw_text.strip():
            # Text-based PDF — no OCR needed, just send text to Gemini
            structured_data = extract_structured_data(ocr_text=raw_text)
        else:
            # Scanned / image-only PDF — render first page and send to Gemini Vision
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=120)   # 120 dpi is sufficient for Gemini
            img_bytes = pix.tobytes("jpeg")
            structured_data = extract_structured_data(
                ocr_text="",
                image_bytes=img_bytes,
                mime_type="image/jpeg",
            )
    else:
        raise ValueError("Unsupported file format. Please upload JPG, PNG, WEBP, or PDF.")

    # ── Resolve category from the single Gemini response ──────────────────
    valid_categories = {"Bills", "Medical", "Insurance", "Banking",
                        "Education", "Legal", "Receipts", "Others"}

    category = str(structured_data.get("category", "Others")).strip()
    if category not in valid_categories:
        category = "Others"
    structured_data["category"] = category

    # ── Persist to DB ──────────────────────────────────────────────────────
    save_document(
        user_id=user_id,
        file_name=filename,
        file_type=file_extension,
        document_category=category,
        extracted_data=structured_data,
    )

    return structured_data
