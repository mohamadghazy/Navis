import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_debts, get_expenses, get_income
from utils.exporters import export_to_excel, generate_pdf_report
from core.calculations import (
    calculate_total_debt_balance,
    calculate_total_monthly_expenses,
    calculate_total_monthly_income,
    calculate_monthly_surplus
)
from components.cards import render_empty_state
from config import CURRENCY

st.set_page_config(page_title="Reports", page_icon="📄", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user
settings = st.session_state.user_settings

debts_df = get_debts(username)
expenses_df = get_expenses(username)
income_df = get_income(username)

total_debt = calculate_total_debt_balance(debts_df)
monthly_expenses = calculate_total_monthly_expenses(expenses_df)
now = datetime.now()
monthly_income = calculate_total_monthly_income(income_df, now)
monthly_surplus = calculate_monthly_surplus(income_df, expenses_df, debts_df, now)

st.title("📄 Reports")
st.markdown("Generate and export financial reports")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Financial Summary")
    
    summary_data = {
        'total_debt': total_debt,
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'monthly_surplus': monthly_surplus
    }
    
    st.metric("💰 Total Debt", f"{CURRENCY} {total_debt:,.0f}")
    st.metric("💸 Monthly Expenses", f"{CURRENCY} {monthly_expenses:,.0f}")
    st.metric("💵 Monthly Income", f"{CURRENCY} {monthly_income:,.0f}")
    st.metric("📊 Monthly Surplus", f"{CURRENCY} {monthly_surplus:,.0f}")
    st.metric("🎯 Emergency Fund Target", f"{CURRENCY} {settings.get('emergency_fund_target', 90000):,.0f}")

with col2:
    st.markdown("### 📥 Export Options")
    
    st.markdown("#### Excel Export")
    st.markdown("Export all your financial data to an Excel file with multiple sheets.")
    
    if st.button("📊 Export to Excel", type="primary", use_container_width=True):
        excel_file = export_to_excel(debts_df, expenses_df, income_df, settings)
        
        st.download_button(
            label="⬇️ Download Excel File",
            data=excel_file,
            file_name=f"financial_report_{username}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("---")
    
    st.markdown("#### PDF Report")
    st.markdown("Generate a comprehensive PDF report of your finances.")
    
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        pdf_file = generate_pdf_report(username, debts_df, expenses_df, income_df, settings, summary_data)
        
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_file,
            file_name=f"financial_report_{username}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")

st.markdown("### 📋 Data Overview")

tab1, tab2, tab3 = st.tabs(["💰 Debts", "💸 Expenses", "💵 Income"])

with tab1:
    if not debts_df.empty:
        st.dataframe(
            debts_df[['name', 'lender', 'balance', 'monthly_payment', 'status', 'priority']],
            use_container_width=True,
            hide_index=True
        )
    else:
        render_empty_state("No debts recorded", "💰")

with tab2:
    if not expenses_df.empty:
        st.dataframe(
            expenses_df[['category', 'amount', 'frequency', 'due_date', 'notes']],
            use_container_width=True,
            hide_index=True
        )
    else:
        render_empty_state("No expenses recorded", "💸")

with tab3:
    if not income_df.empty:
        st.dataframe(
            income_df[['source', 'amount', 'frequency', 'due_date', 'is_active']],
            use_container_width=True,
            hide_index=True
        )
    else:
        render_empty_state("No income recorded", "💵")

st.markdown("---")

st.markdown("### 📅 Report Information")
st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown(f"**Profile:** {username}")
st.markdown(f"**Currency:** {CURRENCY}")
