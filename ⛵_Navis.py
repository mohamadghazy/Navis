import streamlit as st
from datetime import datetime, timedelta
from config import PAGE_CONFIG, APP_NAME
import auth

st.set_page_config(**PAGE_CONFIG)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_settings" not in st.session_state:
    st.session_state.user_settings = {}
if "creating_profile" not in st.session_state:
    st.session_state.creating_profile = False

if st.session_state.creating_profile:
    auth.create_profile_screen()
elif not st.session_state.authenticated:
    auth.login_screen()
else:
    st.sidebar.markdown(f"### 👤 {st.session_state.current_user}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        auth.logout()
    
    # Main Content
    st.title("💰 Personal Finance Planner")
    st.markdown("### Welcome back!")
    st.markdown("Use the sidebar to navigate to different sections.")
    
    st.markdown("---")
    
    from utils.file_handler import get_debts, get_expenses, get_income
    from core.calculations import (
        calculate_total_debt_balance,
        calculate_avg_monthly_debt,
        calculate_avg_monthly_expenses,
        calculate_avg_monthly_income,
        calculate_avg_monthly_surplus
    )
    
    username = st.session_state.current_user
    debts_df = get_debts(username)
    expenses_df = get_expenses(username)
    income_df = get_income(username)
    settings = st.session_state.user_settings
    
    total_debt = calculate_total_debt_balance(debts_df)
    avg_monthly_debt = calculate_avg_monthly_debt(debts_df, 12)
    avg_monthly_expenses = calculate_avg_monthly_expenses(expenses_df, 12)
    avg_monthly_income = calculate_avg_monthly_income(income_df, 12)
    avg_monthly_surplus = calculate_avg_monthly_surplus(income_df, expenses_df, debts_df, 12)
    emergency_target = settings.get('emergency_fund_target', 90000)
    
    # Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Debt", f"EGP {total_debt:,.0f}")
    
    with col2:
        st.metric("💸 Avg Monthly Debt", f"EGP {avg_monthly_debt:,.0f}")
    
    with col3:
        st.metric("💵 Avg Monthly Income", f"EGP {avg_monthly_income:,.0f}")
    
    with col4:
        delta_color = "normal" if avg_monthly_surplus >= 0 else "inverse"
        st.metric("📊 Avg Monthly Surplus", f"EGP {avg_monthly_surplus:,.0f}", delta_color=delta_color)
    
    st.markdown("---")
    
    # Upcoming Payments Notification Section
    st.subheader("🔔 Upcoming Payments")
    
    today = datetime.now().date()
    six_days_later = today + timedelta(days=6)
    
    # Collect all due payments
    upcoming_payments = []
    
    # Check debts
    if not debts_df.empty:
        active_debts = debts_df[debts_df['status'] == 'Active']
        for _, row in active_debts.iterrows():
            if row.get('due_date'):
                try:
                    due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                    upcoming_payments.append({
                        'name': row.get('name', 'Unknown'),
                        'amount': row.get('installment_amount', 0),
                        'due_date': due_date,
                        'type': '💰 Debt'
                    })
                except:
                    pass
    
    # Check expenses
    if not expenses_df.empty:
        for _, row in expenses_df.iterrows():
            if row.get('due_date'):
                try:
                    due_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                    upcoming_payments.append({
                        'name': row.get('category', 'Unknown'),
                        'amount': row.get('amount', 0),
                        'due_date': due_date,
                        'type': '💸 Expense'
                    })
                except:
                    pass
    
    # Sort by due date
    upcoming_payments.sort(key=lambda x: x['due_date'])
    
    # Filter payments due within 3 days
    due_soon = [p for p in upcoming_payments if p['due_date'] <= six_days_later]
    
    if due_soon:
        st.warning("⚠️ Payments due within 6 days:")
        for payment in due_soon:
            days_left = (payment['due_date'] - today).days
            st.markdown(f"• **{payment['type']} {payment['name']}** - Due: {payment['due_date']} ({days_left} day(s)) - EGP {payment['amount']:,.0f}")
    elif upcoming_payments:
        st.info("📅 No payments due within 6 days. Next upcoming payments:")
        # Show next 3 soonest
        for payment in upcoming_payments[:3]:
            days_until = (payment['due_date'] - today).days
            st.markdown(f"• **{payment['type']} {payment['name']}** - Due: {payment['due_date']} (in {days_until} days) - EGP {payment['amount']:,.0f}")
    else:
        st.success("✅ No upcoming payments scheduled!")
