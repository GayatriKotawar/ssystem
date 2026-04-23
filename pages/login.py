import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from auth import authenticate_user

st.title("Login to SmartDMS")
st.markdown("Welcome back! Please login to access your smart document vault.")

if 'user' in st.session_state and st.session_state.user:
    st.success(f"You are already logged in as {st.session_state.user['name']}.")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
else:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                user = authenticate_user(email, password)
                if user:
                    # Remove password hash from session state
                    del user['password_hash']
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
