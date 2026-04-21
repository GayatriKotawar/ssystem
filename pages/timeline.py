import streamlit as st
import pandas as pd
import json
from datetime import datetime
from database import get_user_documents
from utils.alerts import get_user_alerts

st.title("📈 Life Timeline & Expenses")
st.markdown("Track your document history, upcoming expirations, and categorized expenses.")

user_id = st.session_state.user['id']

# 1. Show alerts prominently
alerts = get_user_alerts(user_id)
if alerts:
    st.subheader("📌 Critical Alerts")
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
    # 2. Timeline View
    st.subheader("🕒 Document Timeline")
    
    # We create a structured timeline based on the database
    timeline_data = []
    
    # Also prepare receipt insight engine metrics
    receipt_data = []
    
    for _, row in df.iterrows():
        try:
            data = json.loads(row['extracted_data'])
        except:
            data = {}
            
        doc_name = row['file_name']
        cat = row['document_category']
        upload_date = row['upload_date'][:10]
        
        # Timeline items (combining upload date, due dates, expirations)
        desc = ""
        exp = data.get('expiry_date')
        if exp:
            desc += f" Expires: {exp}"
            
        due = data.get('due_date')
        if due:
            desc += f" Due: {due}"
            
        timeline_data.append({
            "Date": upload_date,
            "Document": doc_name,
            "Category": cat,
            "Details": desc if desc else "Processed"
        })
        
        # Expense insights items
        amt_str = str(data.get('amount', '0')).replace(',', '').replace('₹', '').replace('$', '').strip()
        if amt_str:
            try:
                amt = float(amt_str)
                receipt_data.append({
                    "Date": upload_date,
                    "Category": cat,
                    "Amount": amt
                })
            except:
                pass

    tl_df = pd.DataFrame(timeline_data)
    st.dataframe(tl_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 3. Receipt Insight Engine
    st.subheader("💸 Expense Summaries")
    
    if receipt_data:
        r_df = pd.DataFrame(receipt_data)
        
        # Aggregate by category
        summary_df = r_df.groupby("Category")["Amount"].sum().reset_index()
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("### Total by Category")
            for _, row in summary_df.iterrows():
                st.write(f"**{row['Category']}**: ₹ {row['Amount']:,.2f}")
                
        with c2:
            st.bar_chart(summary_df.set_index("Category"))
            
    else:
        st.info("No expense data extracted yet.")
