import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_debts, get_expenses, get_income
from core.calculations import (
    calculate_total_debt_balance,
    calculate_total_monthly_expenses,
    calculate_total_monthly_income,
    calculate_monthly_surplus,
    calculate_emergency_fund_timeline,
    calculate_debt_payoff_projection,
    calculate_avg_monthly_debt,
    calculate_avg_monthly_expenses,
    calculate_avg_monthly_income,
    calculate_avg_monthly_surplus
)
from core.projections import generate_monthly_projection, forecast_emergency_fund_completion
from components.charts import (
    create_debt_bar_chart,
    create_expense_pie_chart,
    create_savings_line_chart,
    create_income_expense_comparison,
    create_health_gauge
)
from components.cards import render_progress_bar, render_empty_state
from config import CURRENCY

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user
settings = st.session_state.user_settings

debts_df = get_debts(username)
expenses_df = get_expenses(username)
income_df = get_income(username)

total_debt = calculate_total_debt_balance(debts_df)
avg_monthly_debt = calculate_avg_monthly_debt(debts_df, 12)
avg_monthly_expenses = calculate_avg_monthly_expenses(expenses_df, 12)
avg_monthly_income = calculate_avg_monthly_income(income_df, 12)
avg_monthly_surplus = calculate_avg_monthly_surplus(income_df, expenses_df, debts_df, 12)
now = datetime.now()
monthly_income = calculate_total_monthly_income(income_df, now)
monthly_surplus = calculate_monthly_surplus(income_df, expenses_df, debts_df, now)
emergency_target = settings.get('emergency_fund_target', 90000)

st.title("📊 Dashboard")
st.markdown(f"**Profile:** {username}")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💰 Total Debt",
        value=f"{CURRENCY} {total_debt:,.0f}"
    )

with col2:
    st.metric(
        label="💸 Avg Monthly Debt",
        value=f"{CURRENCY} {avg_monthly_debt:,.0f}"
    )

with col3:
    st.metric(
        label="💵 Avg Monthly Expenses",
        value=f"{CURRENCY} {avg_monthly_expenses:,.0f}"
    )

with col4:
    st.metric(
        label="💰 Avg Monthly Income",
        value=f"{CURRENCY} {avg_monthly_income:,.0f}"
    )

with col5:
    st.metric(
        label="💹 Avg Monthly Surplus",
        value=f"{CURRENCY} {avg_monthly_surplus:,.0f}",
        delta_color="normal" if avg_monthly_surplus >= 0 else "inverse"
    )

st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🎯 Emergency Fund Progress")
    
    current_savings = 0
    
    render_progress_bar(current_savings, emergency_target, "Emergency Fund")
    
    if monthly_surplus > 0:
        forecast = forecast_emergency_fund_completion(income_df, expenses_df, debts_df, emergency_target, current_savings)
        
        if forecast['achievable']:
            st.success(f"🎯 Target will be reached in **{forecast['months']} months** ({forecast['date']})")
        else:
            st.warning("⚠️ Unable to reach target with current surplus")
    else:
        st.warning("⚠️ No surplus available for savings. Review your budget.")
    
    st.markdown("---")
    st.subheader("📈 Savings Projection")
    
    projections_df = generate_monthly_projection(
        income_df, expenses_df, debts_df,
        emergency_target, current_savings, 24, username
    )
    
    has_any_surplus = not projections_df.empty and projections_df['surplus'].max() > 0
    
    if not projections_df.empty:
        fig = create_savings_line_chart(projections_df, emergency_target)
        st.plotly_chart(fig, use_container_width=True)
        
        if not has_any_surplus:
            st.warning("⚠️ No months with positive surplus in the projection period. Consider reducing expenses or increasing income.")
    else:
        render_empty_state("Add income and expenses to see projections", "📈")

with col_right:
    st.subheader("📊 Financial Health")
    
    gauge_fig, health_status = create_health_gauge(avg_monthly_debt, avg_monthly_expenses, avg_monthly_income, "Burden Ratio")
    st.plotly_chart(gauge_fig, use_container_width=True)
    
    status_colors = {
        "Excellent": "🟢",
        "Good": "🔵",
        "Warning": "🟡",
        "Critical": "🔴",
        "No Income": "⚫"
    }
    st.metric("Health Status", f"{status_colors.get(health_status, '')} {health_status}")
    
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    
    st.metric("Debt-to-Income Ratio", f"{(total_debt / avg_monthly_income * 100) if avg_monthly_income > 0 else 0:.1f}%")
    
    expense_ratio = (avg_monthly_expenses / avg_monthly_income * 100) if avg_monthly_income > 0 else 0
    st.metric("Expense Ratio", f"{expense_ratio:.1f}%")

st.markdown("---")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("💰 Debt Balances")
    
    if not debts_df.empty:
        debt_fig = create_debt_bar_chart(debts_df)
        st.plotly_chart(debt_fig, use_container_width=True)
    else:
        render_empty_state("No debts recorded", "💰")

with col_chart2:
    st.subheader("💸 Expense Breakdown")
    
    if not expenses_df.empty:
        expense_fig = create_expense_pie_chart(expenses_df)
        st.plotly_chart(expense_fig, use_container_width=True)
    else:
        render_empty_state("No expenses recorded", "💸")

st.markdown("---")

st.subheader("📊 Income vs Outflow")
comparison_fig = create_income_expense_comparison(income_df, expenses_df, debts_df, now)
st.plotly_chart(comparison_fig, use_container_width=True)

st.markdown("---")

st.subheader("📅 Debt Payoff Timeline")

if not debts_df.empty:
    projections = calculate_debt_payoff_projection(debts_df)
    
    if projections:
        import pandas as pd
        proj_df = pd.DataFrame(projections)
        
        st.dataframe(
            proj_df[['name', 'balance', 'monthly_payment', 'months_to_payoff', 'payoff_date']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("All debts are settled!")
else:
    render_empty_state("No active debts", "✅")
