import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_expenses, save_expenses, add_record, update_record, delete_record, get_categories
from components.forms import expense_input_form
from components.cards import render_empty_state
from components.charts import create_expense_pie_chart
from core.calculations import calculate_total_monthly_expenses
from config import CURRENCY

st.set_page_config(page_title="Expenses", page_icon="💸", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user

if 'success_message' in st.session_state:
    st.success(st.session_state.success_message)
    del st.session_state.success_message

st.title("💸 Expenses Management")
st.markdown("Track and categorize your monthly expenses")
st.markdown("---")

if 'editing_expense' in st.session_state:
    st.subheader("✏️ Edit Expense")
    categories = get_categories(username)
    default_values = st.session_state.editing_expense
    result = expense_input_form(key="expense_form_edit", categories=categories, default_values=default_values)
    
    if result:
        if 'id' in result:
            record_id = result.pop('id')
            update_record(username, "expenses.csv", record_id, result)
            st.session_state.success_message = f"Expense '{result['category']}' updated successfully!"
        else:
            add_record(username, "expenses.csv", result)
            st.session_state.success_message = f"Expense '{result['category']}' added successfully!"
        del st.session_state.editing_expense
        st.rerun()
    
    if st.button("Cancel Edit", key="cancel_expense_edit"):
        del st.session_state.editing_expense
        st.rerun()
    
    st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 All Expenses", "➕ Add Expense", "📊 Analytics"])

with tab1:
    expenses_df = get_expenses(username)
    
    if not expenses_df.empty:
        total_monthly = calculate_total_monthly_expenses(expenses_df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(expenses_df))
        with col2:
            st.metric("Monthly Total", f"{CURRENCY} {total_monthly:,.0f}")
        with col3:
            categories = expenses_df['category'].nunique()
            st.metric("Categories", categories)
        
        st.markdown("---")
        
        st.subheader("Expense List")
        
        for idx, row in expenses_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{row.get('category', 'Unknown')}**")
            
            with col2:
                amount = row.get('amount', 0)
                monthly = row.get('monthly_amount', 0)
                freq = row.get('frequency', 'Monthly')
                st.markdown(f"**{CURRENCY} {amount:,.0f}**")
                st.markdown(f"<small>{CURRENCY} {monthly:,.0f}/mo ({freq})</small>", unsafe_allow_html=True)
            
            with col3:
                if row.get('due_date'):
                    st.markdown(f"<small>📅 Due: {row.get('due_date')}</small>", unsafe_allow_html=True)
                if row.get('notes'):
                    st.markdown(f"<small>{row.get('notes')}</small>", unsafe_allow_html=True)
            
            with col4:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️", key=f"edit_exp_{row['id']}", help="Edit expense"):
                        st.session_state.editing_expense = row.to_dict()
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️", key=f"delete_exp_{row['id']}", help="Delete expense"):
                        delete_record(username, "expenses.csv", row['id'])
                        st.rerun()
        
        st.markdown("---")
        
        st.subheader("📋 Expense Details")
        
        display_cols = ['category', 'amount', 'monthly_amount', 'frequency', 'due_date', 'notes']
        available_cols = [c for c in display_cols if c in expenses_df.columns]
        display_df = expenses_df[available_cols].copy()
        
        col_mapping = {
            'category': 'Category', 'amount': 'Amount', 'monthly_amount': 'Monthly',
            'frequency': 'Frequency', 'due_date': 'Due Date', 'notes': 'Notes'
        }
        display_df.columns = [col_mapping.get(c, c) for c in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        render_empty_state("No expenses recorded yet. Add your first expense!", "💸")

with tab2:
    categories = get_categories(username)
    result = expense_input_form(key="expense_form_add", categories=categories)
    
    if result:
        add_record(username, "expenses.csv", result)
        st.session_state.success_message = f"Expense '{result['category']}' added successfully!"
        st.rerun()

with tab3:
    st.subheader("📊 Expense Analytics")
    
    expenses_df = get_expenses(username)
    
    if not expenses_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥧 Expense Breakdown")
            pie_fig = create_expense_pie_chart(expenses_df)
            st.plotly_chart(pie_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 By Category")
            
            category_summary = expenses_df.groupby('category').agg({
                'amount': 'sum',
                'monthly_amount': 'sum'
            }).reset_index()
            category_summary.columns = ['Category', 'Total Amount', 'Monthly Amount']
            category_summary = category_summary.sort_values('Total Amount', ascending=False)
            
            st.dataframe(
                category_summary,
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")
        
        st.markdown("### 📈 Expense Summary")
        
        total = calculate_total_monthly_expenses(expenses_df)
        avg = expenses_df['monthly_amount'].mean()
        max_expense = expenses_df.loc[expenses_df['monthly_amount'].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Monthly Expenses", f"{CURRENCY} {total:,.0f}")
        with col2:
            st.metric("Average Monthly Expense", f"{CURRENCY} {avg:,.0f}")
        with col3:
            st.metric("Largest Monthly Expense", f"{max_expense['category']}: {CURRENCY} {max_expense['monthly_amount']:,.0f}")
    else:
        render_empty_state("Add expenses to see analytics", "📊")
