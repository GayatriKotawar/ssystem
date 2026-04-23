import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from auth import register_user

st.title("Create an Account")
st.markdown("Join SmartDMS to securely manage and analyze your documents.")

with st.form("signup_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submit = st.form_submit_button("Sign Up")
    
    if submit:
        if not name or not email or not password:
            st.error("All fields are required!")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        else:
            success = register_user(name, email, password)
            if success:
                st.success("Account created successfully! You can now log in.")
                # We could redirect, but standard Streamlit allows user to click Login
            else:
                st.error("Email already registered. Please use a different email or log in.")

st.markdown("Already have an account? **[Go to Login](Login)** (Use sidebar)")
