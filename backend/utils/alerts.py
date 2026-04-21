import pandas as pd
import json
from datetime import datetime
from database import get_user_documents

def get_user_alerts(user_id: int):
    """
    Parses user documents to identify alerts like expiring policies or overdue bills.
    Returns a list of alert dictionaries.
    """
    df = get_user_documents(user_id)
    alerts = []
    
    if df.empty:
        return alerts
        
    for _, row in df.iterrows():
        try:
            data = json.loads(row['extracted_data'])
        except Exception:
            data = {}
            
        doc_name = row['file_name']
        
        # Check Expiry Dates (Insurance, Passport, etc)
        expiry = data.get('expiry_date')
        if expiry:
            try:
                # Basic parsing, Gemini usually returns YYYY-MM-DD
                exp_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                days_left = (exp_date - datetime.now().date()).days
                if 0 <= days_left <= 30:
                    alerts.append({
                        "type": "warning",
                        "message": f"⏳ {doc_name} is expiring soon (in {days_left} days)."
                    })
                elif days_left < 0:
                    alerts.append({
                        "type": "error",
                        "message": f"🚨 {doc_name} has expired!"
                    })
            except Exception:
                pass
                
        # Check Due Dates (Bills, EMI, etc)
        due = data.get('due_date')
        if due:
            try:
                due_date = datetime.strptime(due, "%Y-%m-%d").date()
                days_left = (due_date - datetime.now().date()).days
                if 0 <= days_left <= 15:
                    alerts.append({
                        "type": "warning",
                        "message": f"💸 Bill for {doc_name} is due in {days_left} days."
                    })
                elif days_left < 0:
                    alerts.append({
                        "type": "error",
                        "message": f"⚠️ Bill for {doc_name} is OVERDUE!"
                    })
            except Exception:
                pass
                
    return alerts
