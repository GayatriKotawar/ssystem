import cv2
import numpy as np
import easyocr
import pymupdf  # For PDF processing

# Vercel serverless runs on CPU, so keep OCR initialization CPU-safe.
reader = easyocr.Reader(['en'], gpu=False)

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Applies preprocessing to improve OCR accuracy."""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 1. Grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # 2. Resize maintaining aspect ratio (make it larger to improve text quality)
    height, width = gray.shape
    new_width = 1200
    new_height = int(height * (new_width / width))
    resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    # 3. Increase Contrast / Noise Removal
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    
    # 4. Adaptive Thresholding
    processed = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return processed

def extract_text_from_image(image_bytes: bytes) -> str:
    """Extracts raw text from an image byte array."""
    processed_img = preprocess_image(image_bytes)
    result = reader.readtext(processed_img, detail=0)
    return "\n".join(result)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from all pages in a PDF file via OCR."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    all_text = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render page to a pixmap (image)
        pix = page.get_pixmap(dpi=150)
        # Convert pixmap to bytes (png)
        img_bytes = pix.tobytes("png")
        # Extract text via OCR
        text = extract_text_from_image(img_bytes)
        all_text.append(text)
        
    return "\n".join(all_text)
