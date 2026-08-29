import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Tracker", layout="wide")

# Initialize Session State Variables (3 Accounts)
if "acc1_balance" not in st.session_state:
    st.session_state.acc1_balance = 1000.00
if "acc2_balance" not in st.session_state:
    st.session_state.acc2_balance = 1000.00
if "acc3_balance" not in st.session_state:
    st.session_state.acc3_balance = 1000.00
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard & Analytics", "Add Expense", "Export Data"])

# Page 1: Dashboard & Analytics
if page == "Dashboard & Analytics":
    st.title("📊 Expense Tracker")

    # Initial Profile Balance Setup
    with st.expander("⚙️ Account Profiles & Initial Balances", expanded=False):
        c1, c2, c3 = st.columns(3)
        init_acc1 = c1.number_input("Account 1 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc1_balance,
                                    step=50.0)
        init_acc2 = c2.number_input("Account 2 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc2_balance,
                                    step=50.0)
        init_acc3 = c3.number_input("Account 3 Initial Amount (RM)", min_value=0.0, value=st.session_state.acc3_balance,
                                    step=50.0)

        if st.button("Update Balances"):
            st.session_state.acc1_balance = init_acc1
            st.session_state.acc2_balance = init_acc2
            st.session_state.acc3_balance = init_acc3
            st.success("Account balances updated!")

    # Real-Time Balance Metrics across 3 accounts
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account 1 Balance", f"RM{st.session_state.acc1_balance:,.2f}")
    col2.metric("Account 2 Balance", f"RM{st.session_state.acc2_balance:,.2f}")
    col3.metric("Account 3 Balance", f"RM{st.session_state.acc3_balance:,.2f}")

    total_funds = st.session_state.acc1_balance + st.session_state.acc2_balance + st.session_state.acc3_balance
    col4.metric("Total Liquid Funds", f"RM{total_funds:,.2f}")

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
        fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: RM%{value:,.2f} (%{percent})")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data recorded yet. Use the 'Add Expense' page to log spending.")

# Page 2: Add Expense
elif page == "Add Expense":
    st.title("➕ Add Expense Detail")

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
                st.error(f"Insufficient funds in {account}! Available balance: RM{current_bal:,.2f}")
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
                st.success(f"Deducted RM{amount:,.2f} from {account}!")

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
