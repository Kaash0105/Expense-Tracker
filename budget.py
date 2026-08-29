import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# File name for local persistent storage
DATA_FILE = "data.json"

# Helper function: Load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Default values if file doesn't exist yet
    return {
        "acc1_balance": 1000.00,
        "acc2_balance": 1000.00,
        "acc3_balance": 1000.00,
        "transactions": []
    }

# Helper function: Save current state to JSON file
def save_data():
    data = {
        "acc1_balance": st.session_state.acc1_balance,
        "acc2_balance": st.session_state.acc2_balance,
        "acc3_balance": st.session_state.acc3_balance,
        "transactions": st.session_state.transactions
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Expense Tracker", layout="wide")

# Initialize Session State Variables from persistent storage on first load
if "data_loaded" not in st.session_state:
    persistent_data = load_data()
    st.session_state.acc1_balance = persistent_data["acc1_balance"]
    st.session_state.acc2_balance = persistent_data["acc2_balance"]
    st.session_state.acc3_balance = persistent_data["acc3_balance"]
    st.session_state.transactions = persistent_data["transactions"]
    st.session_state.data_loaded = True

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard & Analytics", "Add Expense", "Export Data"])

# Page 1: Dashboard & Analytics
if page == "Dashboard & Analytics":
    st.title("📊 Financial Dashboard")
    
    # Initial Profile Balance Setup
    with st.expander("⚙️ Account Profiles & Initial Balances", expanded=False):
        c1, c2, c3 = st.columns(3)
        init_acc1 = c1.number_input("Account 1 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc1_balance, step=50.0)
        init_acc2 = c2.number_input("Account 2 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc2_balance, step=50.0)
        init_acc3 = c3.number_input("Account 3 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc3_balance, step=50.0)
        
        if st.button("Update Balances"):
            st.session_state.acc1_balance = init_acc1
            st.session_state.acc2_balance = init_acc2
            st.session_state.acc3_balance = init_acc3
            save_data()  # Save changes permanently
            st.success("Account balances updated and saved!")

    # Real-Time Balance Metrics across 3 accounts
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account 1 Balance", f"RM {st.session_state.acc1_balance:,.2f}")
    col2.metric("Account 2 Balance", f"RM {st.session_state.acc2_balance:,.2f}")
    col3.metric("Account 3 Balance", f"RM {st.session_state.acc3_balance:,.2f}")
    
    total_funds = st.session_state.acc1_balance + st.session_state.acc2_balance + st.session_state.acc3_balance
    col4.metric("Total Liquid Funds", f"RM {total_funds:,.2f}")

    st.divider()

    df = pd.DataFrame(st.session_state.transactions)
    if not df.empty:
        st.subheader("Category Breakdown (%)")
        spending_by_cat = df.groupby("Category")["Amount (RM)"].sum().reset_index()
        
        # Doughnut Chart Visualization
        fig = px.pie(
            spending_by_cat,
            values="Amount (RM)",
            names="Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: $%{value:,.2f} (%{percent})")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data recorded yet. Use the 'Add Expense' page to log spending.")

# Page 2: Add Expense
elif page == "Add Expense":
    st.title("➕ Expense Details")

    with st.form("add_expense_form", clear_on_submit=True):
        account = st.selectbox("Select Bank Account Profile", ["Account 1", "Account 2", "Account 3"])
        category = st.selectbox(
            "Spending Category",
            ["Food & Dining", "Housing & Bills", "Entertainment", "Shopping", "Transportation", "Healthcare", "Other"]
        )
        amount = st.number_input("Expense Amount (RM)", min_value=0.01, step=1.0)
        note = st.text_input("Description / Note")
        submit = st.form_submit_button("Record Spending")

        if submit:
            # Map selected account to session balance
            if account == "Account 1":
                current_bal = st.session_state.acc1_balance
            elif account == "Account 2":
                current_bal = st.session_state.acc2_balance
            else:
                current_bal = st.session_state.acc3_balance

            if amount > current_bal:
                st.error(f"Insufficient funds in {account}! Available balance: RM {current_bal:,.2f}")
            else:
                # Deduct from target account
                if account == "Account 1":
                    st.session_state.acc1_balance -= amount
                elif account == "Account 2":
                    st.session_state.acc2_balance -= amount
                else:
                    st.session_state.acc3_balance -= amount

                # Store Transaction
                st.session_state.transactions.append({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Account": account,
                    "Category": category,
                    "Amount (RM)": amount,
                    "Description": note
                })
                
                save_data()  # Save updated balance and transactions permanently
                st.success(f"Deducted RM {amount:,.2f} from {account} and saved to database!")

    st.divider()
    st.subheader("Recent Spendings")
    df = pd.DataFrame(st.session_state.transactions)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No transactions logged in this session yet.")

# Page 3: Export CSV File
elif page == "Export Data":
    st.title("📥 Export Tracking Data")
    df = pd.DataFrame(st.session_state.transactions)

    if not df.empty:
        st.write("Review logged transactions before downloading:")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Transactions as CSV",
            data=csv_data,
            file_name=f"expense_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.warning("No tracking data available to export. Log some expenses first.")
