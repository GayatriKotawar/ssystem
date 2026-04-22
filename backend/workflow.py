def process_upload(uploaded_file, user_id: int):
    """
    Main pipeline:
    1. Read bytes based on file type.
    2. Extract raw text with EasyOCR + OpenCV.
    3. Structure data via Gemini.
    4. Categorize via Gemini.
    5. Save to database.
    
    Returns the final structured dict or None if failure.
    """
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name
    file_extension = filename.split('.')[-1].lower()

    from ai_extractor import extract_structured_data
    from categorizer import categorize_document
    from database import save_document
    from ocr_engine import extract_text_from_image, extract_text_from_pdf
    
    # 1. & 2. OCR Extractions
    if file_extension in ['pdf']:
        raw_text = extract_text_from_pdf(file_bytes)
    elif file_extension in ['jpg', 'jpeg', 'png']:
        raw_text = extract_text_from_image(file_bytes)
    else:
        raise ValueError("Unsupported file format. Please upload JPG, PNG, or PDF.")
        
    if not raw_text.strip() and file_extension not in ['jpg', 'jpeg', 'png']:
        # Edge case: No text detected and it's not an image we can pass to Gemini
        return {
            "error": "No text detected in the document."
        }
        
    # 3. Structure data multimodally (if image)
    mime_type = f"image/{file_extension}" if file_extension in ['jpg', 'jpeg', 'png'] else None
    image_bytes = file_bytes if mime_type else None
    
    structured_data = extract_structured_data(raw_text, image_bytes, mime_type)
    
    # 4. Auto-Categorize
    category = categorize_document(raw_text)
    
    # Optional fallback
    if "category" in structured_data and structured_data["category"] and category == "Others":
        category = structured_data["category"]
        
    # Inject final category
    structured_data["category"] = category
    
    # 5. Save to Database
    save_document(
        user_id=user_id,
        file_name=filename,
        file_type=file_extension,
        document_category=category,
        extracted_data=structured_data
    )
    
    return structured_data
