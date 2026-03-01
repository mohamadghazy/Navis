import streamlit as st
from config import CURRENCY

def render_metric_card(label, value, delta=None, delta_color="normal"):
    if delta is not None:
        st.metric(label=label, value=f"{CURRENCY} {value:,.0f}", delta=delta, delta_color=delta_color)
    else:
        st.metric(label=label, value=f"{CURRENCY} {value:,.0f}")

def render_progress_bar(current, target, label="Progress"):
    if target <= 0:
        percentage = 0
    else:
        percentage = min((current / target) * 100, 100)
    
    st.markdown(f"**{label}**")
    st.progress(int(percentage))
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<small>{CURRENCY} {current:,.0f} / {CURRENCY} {target:,.0f}</small>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<small style='text-align: right'>{percentage:.1f}%</small>", unsafe_allow_html=True)

def render_summary_cards(total_debt, monthly_expenses, monthly_income, monthly_surplus, emergency_fund_target, current_savings):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Debt",
            value=f"{CURRENCY} {total_debt:,.0f}"
        )
    
    with col2:
        st.metric(
            label="💸 Monthly Expenses",
            value=f"{CURRENCY} {monthly_expenses:,.0f}"
        )
    
    with col3:
        st.metric(
            label="💵 Monthly Income",
            value=f"{CURRENCY} {monthly_income:,.0f}"
        )
    
    with col4:
        delta_color = "normal" if monthly_surplus >= 0 else "inverse"
        st.metric(
            label="📊 Monthly Surplus",
            value=f"{CURRENCY} {monthly_surplus:,.0f}",
            delta_color=delta_color
        )
    
    st.markdown("---")
    
    st.subheader("🎯 Emergency Fund Progress")
    render_progress_bar(current_savings, emergency_fund_target, "Emergency Fund")

def render_debt_card(debt):
    balance = debt.get('balance', 0)
    monthly_payment = debt.get('monthly_payment', 0)
    name = debt.get('name', 'Unknown')
    lender = debt.get('lender', '')
    status = debt.get('status', 'Active')
    interest_rate = debt.get('interest_rate', 0) or 0
    
    status_emoji = "✅" if status == "Settled" else "🔄" if status == "Active" else "⚠️"
    
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{name}**")
            if lender:
                st.markdown(f"<small>{lender}</small>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{CURRENCY} {balance:,.0f}**")
            st.markdown(f"<small>{CURRENCY} {monthly_payment:,.0f}/mo</small>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"{status_emoji} {status}")
            if interest_rate > 0:
                st.markdown(f"<small>{interest_rate}% interest</small>", unsafe_allow_html=True)
        
        st.markdown("---")

def render_empty_state(message, icon="📭"):
    st.markdown(f"""
    <div style="text-align: center; padding: 50px;">
        <div style="font-size: 48px;">{icon}</div>
        <div style="font-size: 18px; color: #666; margin-top: 10px;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_milestone_timeline(milestones):
    for milestone in milestones:
        completed = milestone.get('completed', False)
        icon = "✅" if completed else "⬜"
        
        col1, col2 = st.columns([1, 11])
        with col1:
            st.markdown(f"### {icon}")
        with col2:
            st.markdown(f"**{milestone.get('name', '')}**")
            st.markdown(f"<small>{milestone.get('date', '')}</small>", unsafe_allow_html=True)
