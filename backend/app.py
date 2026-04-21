import streamlit as st

st.set_page_config(page_title="SmartDMS", layout="wide", page_icon="📑")

# Initialize session state if not exists
if "user" not in st.session_state:
    st.session_state.user = None

def main():
    if st.session_state.user is None:
        # Show login / signup if user represents 'not logged in'
        page_login = st.Page("pages/login.py", title="Login", icon="🔑", default=True)
        page_signup = st.Page("pages/signup.py", title="Sign Up", icon="📝")
        pg = st.navigation([page_login, page_signup])
        pg.run()
    else:
        # Show main app once logged in
        page_dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True)
        page_upload = st.Page("pages/upload.py", title="Upload Document", icon="📤")
        page_timeline = st.Page("pages/timeline.py", title="Life Timeline", icon="⏳")
        page_logout = st.Page("pages/login.py", title="Logout", icon="⬅️")
        
        pg = st.navigation([page_dashboard, page_upload, page_timeline, page_logout])
        pg.run()

if __name__ == "__main__":
    main()
