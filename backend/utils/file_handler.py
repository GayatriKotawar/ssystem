import tempfile
import os

def save_uploaded_file(uploaded_file) -> str:
    """
    Saves a Streamlit uploaded file temporarily and returns the path.
    (If needed for file-based libraries. Not always necessary 
    if libraries support byte streams natively.)
    """
    try:
        # Create a temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path
    except Exception as e:
        print(f"Error saving uploaded file: {e}")
        return None
