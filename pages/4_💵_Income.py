import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_income, save_income, add_record, update_record, delete_record
from components.forms import income_input_form
from components.cards import render_empty_state
from core.calculations import calculate_total_monthly_income
from config import CURRENCY

st.set_page_config(page_title="Income", page_icon="💵", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user

if 'success_message' in st.session_state:
    st.success(st.session_state.success_message)
    del st.session_state.success_message

st.title("💵 Income Management")
st.markdown("Track your income sources and frequency")
st.markdown("---")

if 'editing_income' in st.session_state:
    st.subheader("✏️ Edit Income")
    default_values = st.session_state.editing_income
    result = income_input_form(key="income_form_edit", default_values=default_values)
    
    if result:
        if 'id' in result:
            record_id = result.pop('id')
            update_record(username, "income.csv", record_id, result)
            st.session_state.success_message = f"Income '{result['source']}' updated successfully!"
        else:
            add_record(username, "income.csv", result)
            st.session_state.success_message = f"Income '{result['source']}' added successfully!"
        del st.session_state.editing_income
        st.rerun()
    
    if st.button("Cancel Edit", key="cancel_income_edit"):
        del st.session_state.editing_income
        st.rerun()
    
    st.markdown("---")

tab1, tab2 = st.tabs(["📋 All Income", "➕ Add Income"])

with tab1:
    income_df = get_income(username)
    
    if not income_df.empty:
        now = datetime.now()
        total_monthly = calculate_total_monthly_income(income_df, now)
        active_income = income_df[income_df['is_active'] == True]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sources", len(income_df))
        with col2:
            st.metric("Active Sources", len(active_income))
        with col3:
            st.metric("Monthly Income", f"{CURRENCY} {total_monthly:,.0f}")
        
        st.markdown("---")
        
        st.subheader("Income List")
        
        for idx, row in income_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{row.get('source', 'Unknown')}**")
            
            with col2:
                amount = row.get('amount', 0)
                monthly = row.get('monthly_amount', 0)
                freq = row.get('frequency', 'Monthly')
                st.markdown(f"**{CURRENCY} {amount:,.0f}**")
                st.markdown(f"<small>{CURRENCY} {monthly:,.0f}/mo ({freq})</small>", unsafe_allow_html=True)
            
            with col3:
                is_active = row.get('is_active', True)
                status = "✅ Active" if is_active else "⏸️ Inactive"
                st.markdown(status)
            
            with col4:
                if row.get('due_date'):
                    st.markdown(f"<small>📅 {row.get('due_date')}</small>", unsafe_allow_html=True)
            
            with col5:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️", key=f"edit_inc_{row['id']}", help="Edit income"):
                        st.session_state.editing_income = row.to_dict()
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️", key=f"delete_inc_{row['id']}", help="Delete income"):
                        delete_record(username, "income.csv", row['id'])
                        st.rerun()
        
        st.markdown("---")
        
        st.subheader("📋 Income Details")
        
        display_cols = ['source', 'amount', 'monthly_amount', 'frequency', 'due_date', 'is_active']
        available_cols = [c for c in display_cols if c in income_df.columns]
        display_df = income_df[available_cols].copy()
        display_df['is_active'] = display_df['is_active'].apply(lambda x: 'Yes' if x else 'No')
        
        col_mapping = {
            'source': 'Source', 'amount': 'Amount', 'monthly_amount': 'Monthly',
            'frequency': 'Frequency', 'due_date': 'Due Date', 'is_active': 'Active'
        }
        display_df.columns = [col_mapping.get(c, c) for c in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        st.subheader("📊 Income Breakdown")
        
        import plotly.express as px
        
        active_df = income_df[income_df['is_active'] == True]
        
        if not active_df.empty:
            fig = px.bar(
                active_df,
                x='source',
                y='amount',
                title='Active Income Sources',
                color='amount',
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                xaxis_title="Source",
                yaxis_title=f"Amount ({CURRENCY})",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("No income recorded yet. Add your first income source!", "💵")

with tab2:
    result = income_input_form(key="income_form_add")
    
    if result:
        add_record(username, "income.csv", result)
        st.session_state.success_message = f"Income '{result['source']}' added successfully!"
        st.rerun()
