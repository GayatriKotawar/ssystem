import streamlit as st
import pandas as pd
from PIL import Image
import os
from workflow import process_upload

st.title("📤 Upload Document")
st.markdown("Upload medical bills, prescriptions, insurance docs, IDs, and more. Gemini AI will handle the rest.")

uploaded_file = st.file_uploader("Upload a file (JPG, PNG, PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    user_id = st.session_state.user['id']
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Preview")
        if file_type in ['jpg', 'jpeg', 'png']:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True, caption=uploaded_file.name)
        else:
            st.info(f"PDF Uploaded: {uploaded_file.name}")
            
    with col2:
        if st.button("🚀 Process Document", use_container_width=True):
            with st.spinner("Extracting text and identifying category with Gemini 2.0..."):
                try:
                    results = process_upload(uploaded_file, user_id)
                    
                    if "error" in results:
                        st.error(results["error"])
                    else:
                        st.success(f"Processing Complete! Category: {results.get('category', 'Others')}")
                        
                        st.subheader("Extracted Information")
                        # Format clearly
                        for k, v in results.items():
                            if v and k != "category":
                                st.write(f"**{k.replace('_', ' ').title()}**: {v}")
                                
                        with st.expander("Show Raw JSON Insights"):
                            st.json(results)
                            
                except Exception as e:
                    st.error(f"Failed to process document. Error: {e}")
