import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_debts, save_debts, add_record, update_record, delete_record
from components.forms import debt_input_form
from components.cards import render_empty_state
from components.charts import create_debt_bar_chart
from core.debt_strategies import snowball_strategy, avalanche_strategy, compare_strategies
from config import CURRENCY

st.set_page_config(page_title="Debts", page_icon="💰", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user

if 'success_message' in st.session_state:
    st.success(st.session_state.success_message)
    del st.session_state.success_message

st.title("💰 Debts Management")
st.markdown("Manage your debts and view payoff strategies")
st.markdown("---")

if 'editing_debt' in st.session_state:
    st.subheader("✏️ Edit Debt")
    default_values = st.session_state.editing_debt
    result = debt_input_form(key="debt_form_edit", default_values=default_values)
    
    if result:
        if 'id' in result:
            record_id = result.pop('id')
            update_record(username, "debts.csv", record_id, result)
            st.session_state.success_message = f"Debt '{result['name']}' updated successfully!"
        else:
            add_record(username, "debts.csv", result)
            st.session_state.success_message = f"Debt '{result['name']}' added successfully!"
        del st.session_state.editing_debt
        st.rerun()
    
    if st.button("Cancel Edit", key="cancel_debt_edit"):
        del st.session_state.editing_debt
        st.rerun()
    
    st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 All Debts", "➕ Add Debt", "📊 Strategies"])

with tab1:
    debts_df = get_debts(username)
    
    if not debts_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Debts", len(debts_df))
        with col2:
            active_debts = debts_df[debts_df['status'] == 'Active']
            st.metric("Active Debts", len(active_debts))
        with col3:
            total_balance = debts_df['balance'].sum()
            st.metric("Total Balance", f"{CURRENCY} {total_balance:,.0f}")
        
        st.markdown("---")
        
        st.subheader("Debt List")
        
        for idx, row in debts_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{row.get('name', 'Unknown')}**")
                if row.get('lender'):
                    st.markdown(f"<small>{row.get('lender')}</small>", unsafe_allow_html=True)
                if row.get('due_date'):
                    st.markdown(f"<small>📅 Due: {row.get('due_date')}</small>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{CURRENCY} {row.get('balance', 0):,.0f}**")
                monthly = row.get('monthly_payment', 0)
                st.markdown(f"<small>{CURRENCY} {monthly:,.0f}/mo</small>", unsafe_allow_html=True)
            
            with col3:
                status = row.get('status', 'Active')
                status_emoji = "✅" if status == "Settled" else "🔄"
                st.markdown(f"{status_emoji} {status}")
            
            with col4:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️", key=f"edit_{row['id']}", help="Edit debt"):
                        st.session_state.editing_debt = row.to_dict()
                        st.session_state.active_tab = 1
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️", key=f"delete_{row['id']}", help="Delete debt"):
                        delete_record(username, "debts.csv", row['id'])
                        st.rerun()
            
            st.markdown("---")
        
        st.subheader("📊 Debt Overview")
        debt_fig = create_debt_bar_chart(debts_df)
        st.plotly_chart(debt_fig, use_container_width=True)
        
        st.subheader("📋 Debt Details")
        
        display_cols = ['name', 'lender', 'balance', 'interest_rate', 'monthly_payment', 'frequency', 'due_date', 'end_date', 'status', 'priority']
        available_cols = [c for c in display_cols if c in debts_df.columns]
        display_df = debts_df[available_cols].copy()
        
        col_mapping = {
            'name': 'Name', 'lender': 'Lender', 'balance': 'Balance', 
            'interest_rate': 'Interest %', 'monthly_payment': 'Payment/mo',
            'frequency': 'Frequency', 'due_date': 'Due Date', 'end_date': 'End Date',
            'status': 'Status', 'priority': 'Priority'
        }
        display_df.columns = [col_mapping.get(c, c) for c in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        render_empty_state("No debts recorded yet. Add your first debt!", "💰")

with tab2:
    result = debt_input_form(key="debt_form_add")
    
    if result:
        add_record(username, "debts.csv", result)
        st.session_state.success_message = f"Debt '{result['name']}' added successfully!"
        st.rerun()

with tab3:
    st.subheader("📊 Debt Payoff Strategies")
    
    debts_df = get_debts(username)
    
    if not debts_df.empty:
        active_debts = debts_df[debts_df['status'] == 'Active']
        
        if not active_debts.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ❄️ Snowball Method")
                st.markdown("Pay smallest balance first for quick wins")
                
                snowball_df = snowball_strategy(debts_df)
                snowball_active = snowball_df[snowball_df['status'] == 'Active'][['name', 'balance', 'monthly_payment']]
                
                if 'strategy_rank' in snowball_df.columns:
                    snowball_active = snowball_df[snowball_df['status'] == 'Active'][['strategy_rank', 'name', 'balance', 'monthly_payment']]
                    snowball_active.columns = ['Order', 'Debt Name', 'Balance', 'Payment/mo']
                else:
                    snowball_active.columns = ['Debt Name', 'Balance', 'Payment/mo']
                
                st.dataframe(snowball_active, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("### 🏔️ Avalanche Method")
                st.markdown("Pay highest interest first to save money")
                
                avalanche_df = avalanche_strategy(debts_df)
                avalanche_active = avalanche_df[avalanche_df['status'] == 'Active']
                
                if 'strategy_rank' in avalanche_df.columns:
                    avalanche_display = avalanche_active[['strategy_rank', 'name', 'balance', 'interest_rate', 'monthly_payment']]
                    avalanche_display.columns = ['Order', 'Debt Name', 'Balance', 'Interest %', 'Payment/mo']
                else:
                    avalanche_display = avalanche_active[['name', 'balance', 'interest_rate', 'monthly_payment']]
                    avalanche_display.columns = ['Debt Name', 'Balance', 'Interest %', 'Payment/mo']
                
                st.dataframe(avalanche_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("📈 Strategy Comparison")
            
            extra_payment = st.number_input("Extra Monthly Payment Available", min_value=0, value=0, step=100)
            
            if st.button("Compare Strategies"):
                comparison = compare_strategies(debts_df, extra_payment)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Snowball Months", comparison['snowball']['total_months'])
                with col2:
                    st.metric("Avalanche Months", comparison['avalanche']['total_months'])
                with col3:
                    st.metric("Difference", f"{comparison['difference_months']} months")
                
                if comparison['difference_months'] > 0:
                    st.info("💡 Avalanche method will pay off debt faster!")
                elif comparison['difference_months'] < 0:
                    st.info("💡 Snowball method will pay off debt faster!")
                else:
                    st.info("💡 Both methods have the same timeline!")
        else:
            st.success("🎉 All debts are settled!")
    else:
        render_empty_state("Add debts to see payoff strategies", "📊")
