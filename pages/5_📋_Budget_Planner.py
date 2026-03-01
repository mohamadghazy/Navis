import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_debts, get_expenses, get_income
from core.calculations import (
    calculate_avg_monthly_debt,
    calculate_avg_monthly_expenses,
    calculate_avg_monthly_income,
    calculate_avg_monthly_surplus,
    calculate_emergency_fund_timeline
)
from core.projections import generate_monthly_projection, generate_budget_template, forecast_emergency_fund_completion
from components.cards import render_progress_bar, render_empty_state
from components.charts import create_savings_line_chart, create_surplus_bar_chart
from config import CURRENCY

st.set_page_config(page_title="Budget Planner", page_icon="📋", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user
settings = st.session_state.user_settings

debts_df = get_debts(username)
expenses_df = get_expenses(username)
income_df = get_income(username)

avg_monthly_debt = calculate_avg_monthly_debt(debts_df, 12)
avg_monthly_expenses = calculate_avg_monthly_expenses(expenses_df, 12)
avg_monthly_income = calculate_avg_monthly_income(income_df, 12)
avg_monthly_surplus = calculate_avg_monthly_surplus(income_df, expenses_df, debts_df, 12)
emergency_target = settings.get('emergency_fund_target', 90000)

st.title("📋 Budget Planner")
st.markdown("Plan your monthly budget and track projections")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💵 Avg Income", f"{CURRENCY} {avg_monthly_income:,.0f}")

with col2:
    st.metric("💸 Expenses", f"{CURRENCY} {avg_monthly_expenses:,.0f}")

with col3:
    st.metric("💰 Debt Payments", f"{CURRENCY} {avg_monthly_debt:,.0f}")

with col4:
    delta_color = "normal" if avg_monthly_surplus >= 0 else "inverse"
    st.metric("📊 Surplus", f"{CURRENCY} {avg_monthly_surplus:,.0f}", delta_color=delta_color)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Monthly Budget", "📈 Projections", "🎯 Emergency Fund", "💳 Payment Tracking"])

with tab1:
    st.subheader("📊 Monthly Budget Summary")
    
    if avg_monthly_income > 0:
        st.markdown("### Income Breakdown")
        
        if not income_df.empty:
            active_income = income_df[income_df['is_active'] == True]
            
            for _, row in active_income.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"• {row['source']}")
                with col2:
                    st.markdown(f"{CURRENCY} {row['monthly_amount']:,.0f}")
        else:
            st.info("No income sources added")
        
        st.markdown("---")
        st.markdown("### Expense Breakdown")
        
        if not expenses_df.empty:
            for _, row in expenses_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"• {row['category']}")
                with col2:
                    st.markdown(f"{CURRENCY} {row['monthly_amount']:,.0f}")
        else:
            st.info("No expenses added")
        
        st.markdown("---")
        st.markdown("### Debt Payments")
        
        if not debts_df.empty:
            active_debts = debts_df[debts_df['status'] == 'Active']
            
            for _, row in active_debts.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"• {row['name']}")
                with col2:
                    st.markdown(f"{CURRENCY} {row['monthly_payment']:,.0f}")
        else:
            st.info("No active debts")
        
        st.markdown("---")
        
        st.subheader("📊 Budget Allocation")
        
        total_outflow = avg_monthly_expenses + avg_monthly_debt
        
        if total_outflow > 0:
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[go.Pie(
                labels=['Expenses', 'Debt Payments', 'Savings'],
                values=[avg_monthly_expenses, avg_monthly_debt, max(avg_monthly_surplus, 0)],
                hole=.4
            )])
            
            fig.update_layout(
                title="Monthly Budget Allocation",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        render_empty_state("Add income sources to see budget breakdown", "📊")

with tab2:
    st.subheader("📈 Monthly Projections")
    
    months = st.slider("Projection Period (months)", 6, 60, 24)
    
    if avg_monthly_income > 0:
        projections_df = generate_monthly_projection(
            income_df, expenses_df, debts_df,
            emergency_target, 0, months, username
        )
        
        if not projections_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💰 Savings Growth")
                savings_fig = create_savings_line_chart(projections_df, emergency_target)
                st.plotly_chart(savings_fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Monthly Surplus")
                surplus_fig = create_surplus_bar_chart(projections_df)
                st.plotly_chart(surplus_fig, use_container_width=True)
            
            st.markdown("---")
            
            st.subheader("📋 Projection Details")
            
            display_cols = ['month', 'date', 'income', 'expenses', 'debt_payment', 'surplus', 'cumulative_savings']
            display_df = projections_df[display_cols].copy()
            display_df.columns = ['Month', 'Date', 'Income', 'Expenses', 'Debt', 'Surplus', 'Cumulative']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
    else:
        render_empty_state("Add income sources to see projections", "📈")

with tab3:
    st.subheader("🎯 Emergency Fund Planning")
    
    st.markdown(f"**Target:** {CURRENCY} {emergency_target:,.0f}")
    
    starting_balance = st.number_input("Current Savings", min_value=0, value=0, step=1000)
    
    if avg_monthly_surplus > 0:
        forecast = forecast_emergency_fund_completion(income_df, expenses_df, debts_df, emergency_target, starting_balance)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Surplus", f"{CURRENCY} {avg_monthly_surplus:,.0f}")
        
        with col2:
            st.metric("Months to Target", forecast['months'])
        
        with col3:
            if forecast['achievable']:
                st.metric("Completion Date", forecast['date'])
            else:
                st.metric("Status", "Not Achievable")
        
        st.markdown("---")
        
        render_progress_bar(starting_balance, emergency_target, "Emergency Fund Progress")
        
        if forecast['achievable']:
            st.success(f"🎯 You will reach your emergency fund target in **{forecast['months']} months** ({forecast['date']})")
            
            projections_df = generate_monthly_projection(
                income_df, expenses_df, debts_df,
                emergency_target, starting_balance, min(forecast['months'] + 6, 36), username
            )
            
            if not projections_df.empty:
                st.markdown("### 📈 Savings Projection to Target")
                fig = create_savings_line_chart(projections_df, emergency_target)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No surplus available. Review your income and expenses to create a surplus.")
        
        st.markdown("**Suggestions:**")
        st.markdown("• Reduce discretionary expenses")
        st.markdown("• Look for additional income sources")
        st.markdown("• Pay off high-interest debt first")

with tab4:
    st.subheader("💳 Payment Tracking")
    
    from utils.file_handler import get_payment_records, add_payment_record, get_payment_record_by_source_and_month
    from core.calculations import (
        calculate_payment_points, calculate_savings_points,
        get_payment_points_milestone, get_savings_points_milestone,
        get_total_payment_points, get_total_savings_points
    )
    
    payment_records_df = get_payment_records(username)
    current_month = datetime.now().strftime('%Y-%m')
    
    payment_pts = get_total_payment_points(payment_records_df)
    savings_pts = get_total_savings_points(payment_records_df)
    
    col_pts1, col_pts2 = st.columns(2)
    
    with col_pts1:
        st.markdown("### ⏰ Payment Discipline")
        payment_milestone = get_payment_points_milestone(payment_pts['total'])
        st.markdown(f"**{payment_milestone['title']}** - {payment_pts['total']} points")
        st.progress(payment_milestone['progress'] / 100)
        st.caption(f"Next: {payment_milestone['next_title']} at {payment_milestone['next_threshold']} pts")
    
    with col_pts2:
        st.markdown("### 💰 Savings Points")
        savings_milestone = get_savings_points_milestone(savings_pts['total'])
        st.markdown(f"**{savings_milestone['title']}** - {savings_pts['total']} points")
        st.progress(savings_milestone['progress'] / 100)
        st.caption(f"Next: {savings_milestone['next_title']} at {savings_milestone['next_threshold']} pts")
    
    st.markdown("---")
    
    # Get all unique months from payment records
    available_months = []
    if not payment_records_df.empty:
        available_months = payment_records_df['month'].unique().tolist()
    
    # Add current month if not present
    if current_month not in available_months:
        available_months.append(current_month)
    
    # Sort chronologically (newest first)
    available_months.sort(reverse=True)
    
    selected_month = st.selectbox(
        "Select Month",
        options=available_months,
        index=0
    )
    
    month_records = payment_records_df[payment_records_df['month'] == selected_month] if not payment_records_df.empty else pd.DataFrame()
    
    st.markdown(f"### Payments for {selected_month}")
    
    if not month_records.empty:
        st.dataframe(
            month_records[['source_name', 'source_type', 'budgeted_amount', 'actual_amount', 'payment_points', 'savings_points']],
            use_container_width=True
        )
        
        total_budgeted = month_records['budgeted_amount'].sum()
        total_actual = month_records['actual_amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Budgeted", f"{CURRENCY} {total_budgeted:,.0f}")
        with col2:
            st.metric("Total Actual", f"{CURRENCY} {total_actual:,.0f}")
        with col3:
            diff = total_budgeted - total_actual
            st.metric("Difference", f"{CURRENCY} {diff:,.0f}", delta_color="normal" if diff >= 0 else "inverse")
    else:
        st.info("No payment records for this month")
