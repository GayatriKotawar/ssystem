import streamlit as st
from database import get_user_documents
from utils.alerts import get_user_alerts
import pandas as pd
import json
import ast

st.title("📊 Smart Dashboard")

user_id = st.session_state.user['id']
name = st.session_state.user['name']

st.markdown(f"Welcome back, **{name}**!")

# Fetch Alerts
alerts = get_user_alerts(user_id)
if alerts:
    st.subheader("🔔 Smart Alerts")
    for alert in alerts:
        if alert['type'] == 'error':
            st.error(alert['message'])
        else:
            st.warning(alert['message'])

st.divider()

# Fetch Documents
df = get_user_documents(user_id)

if df.empty:
    st.info("No documents found. Start by uploading a document in the 'Upload Document' page.")
else:
    # Key Metrics
    total_docs = len(df)
    
    # Process amounts for total expenses
    total_expenses = 0.0
    for _, row in df.iterrows():
        try:
            data = json.loads(row['extracted_data'])
            amt_str = str(data.get('amount', '0')).replace(',', '').replace('₹', '').replace('$', '').strip()
            if amt_str:
                total_expenses += float(amt_str)
        except:
            pass
            
    # Count expiring soon
    expiring_count = len([a for a in alerts if "expiring" in a['message'].lower()])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Documents", total_docs)
    col2.metric("Total Expenses", f"₹ {total_expenses:,.2f}")
    col3.metric("Upcoming Expiries", expiring_count)
    
    st.divider()
    
    st.subheader("📈 Insights")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Documents by Category**")
        cat_counts = df['document_category'].value_counts()
        st.bar_chart(cat_counts)
        
    with c2:
        st.markdown("**Recent Uploads**")
        recent = df[['file_name', 'document_category', 'upload_date']].head(5)
        st.dataframe(recent, use_container_width=True, hide_index=True)
