import streamlit as st
import pandas as pd
from datetime import datetime
from config import EXPENSE_CATEGORIES, INCOME_FREQUENCIES, DEBT_FREQUENCIES, DEBT_STATUSES, DEBT_PRIORITIES

def get_frequency_divisor(frequency):
    """Return the divisor to convert installment to monthly payment"""
    if frequency == "Monthly":
        return 1
    elif frequency == "Quarterly":
        return 3
    elif frequency == "Semester":
        return 6
    elif frequency == "Yearly":
        return 12
    return 1

def debt_input_form(key="debt_form", default_values=None):
    if default_values is None:
        default_values = {}
    
    is_edit = bool(default_values.get('id'))
    header = "✏️ Edit Debt" if is_edit else "➕ Add New Debt"
    btn_text = "💾 Update Debt" if is_edit else "💾 Save Debt"
    
    with st.form(key=key):
        st.subheader(header)
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Debt Name *", placeholder="e.g., Personal Loan", key=f"{key}_name", value=default_values.get('name', ''))
            lender = st.text_input("Lender/Bank", placeholder="e.g., Bank A", key=f"{key}_lender", value=default_values.get('lender', ''))
            balance = st.number_input("Current Balance *", min_value=0.0, step=1000.0, key=f"{key}_balance", value=float(default_values.get('balance', 0)))
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"{key}_interest", value=float(default_values.get('interest_rate', 0)))
        
        with col2:
            installment_amount = st.number_input("Installment Amount *", min_value=0.0, step=100.0, key=f"{key}_installment", value=float(default_values.get('installment_amount', 0)))
            freq_index = DEBT_FREQUENCIES.index(default_values.get('frequency', 'Monthly')) if default_values.get('frequency') in DEBT_FREQUENCIES else 0
            frequency = st.selectbox("Payment Frequency", DEBT_FREQUENCIES, key=f"{key}_frequency", index=freq_index)
            
            default_due = datetime.strptime(default_values.get('due_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') if default_values.get('due_date') else datetime.now()
            due_date = st.date_input("Due Date *", default_due, key=f"{key}_due_date", help="When is the next installment due?")
            
            default_end = datetime.strptime(default_values.get('end_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') if default_values.get('end_date') else datetime.now().replace(year=datetime.now().year + 1)
            end_date = st.date_input("End Date", default_end, key=f"{key}_end_date", help="When will this debt be fully paid?")
        
        col3, col4 = st.columns(2)
        with col3:
            status_index = DEBT_STATUSES.index(default_values.get('status', 'Active')) if default_values.get('status') in DEBT_STATUSES else 0
            status = st.selectbox("Status", DEBT_STATUSES, key=f"{key}_status", index=status_index)
        with col4:
            priority_index = DEBT_PRIORITIES.index(default_values.get('priority', 'Medium')) if default_values.get('priority') in DEBT_PRIORITIES else 1
            priority = st.selectbox("Priority", DEBT_PRIORITIES, key=f"{key}_priority", index=priority_index)
        
        notes = st.text_area("Notes", placeholder="Additional notes...", key=f"{key}_notes", value=default_values.get('notes', ''))
        
        submitted = st.form_submit_button(btn_text, type="primary")
        
        if submitted:
            if not name or balance <= 0 or installment_amount <= 0:
                st.error("❌ Please fill in all required fields (*)")
                return None
            
            divisor = get_frequency_divisor(frequency)
            monthly_payment = installment_amount / divisor
            
            result = {
                'name': name,
                'lender': lender,
                'balance': balance,
                'interest_rate': interest_rate,
                'installment_amount': installment_amount,
                'monthly_payment': monthly_payment,
                'frequency': frequency,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'status': status,
                'priority': priority,
                'notes': notes
            }
            
            if is_edit:
                result['id'] = default_values['id']
            
            return result
    
    return None

def expense_input_form(key="expense_form", categories=None, default_values=None):
    if categories is None:
        categories = EXPENSE_CATEGORIES
    if default_values is None:
        default_values = {}
        
    with st.form(key=key):
        st.subheader("➕ Add New Expense")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_index = categories.index(default_values.get('category', categories[0])) if default_values.get('category') in categories else 0
            category = st.selectbox("Category *", categories, key=f"{key}_category", index=cat_index)
            amount = st.number_input("Amount *", min_value=0.0, step=100.0, key=f"{key}_amount", value=float(default_values.get('amount', 0)))
        
        with col2:
            freq_index = INCOME_FREQUENCIES.index(default_values.get('frequency', 'Monthly')) if default_values.get('frequency') in INCOME_FREQUENCIES else 0
            frequency = st.selectbox("Frequency", INCOME_FREQUENCIES, key=f"{key}_frequency", index=freq_index)
            
            default_due = datetime.strptime(default_values.get('due_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') if default_values.get('due_date') else datetime.now()
            due_date = st.date_input("Due Date *", default_due, key=f"{key}_due_date", help="When is this expense due?")
        
        notes = st.text_input("Notes", placeholder="Optional notes...", key=f"{key}_notes", value=default_values.get('notes', ''))
        
        submitted = st.form_submit_button("💾 Save Expense", type="primary")
        
        if submitted:
            if not category or amount <= 0:
                st.error("❌ Please fill in all required fields (*)")
                return None
            
            if frequency == "One-time":
                monthly_amount = 0
            else:
                divisor = get_frequency_divisor(frequency)
                monthly_amount = amount / divisor
            
            result = {
                'category': category,
                'amount': amount,
                'monthly_amount': monthly_amount,
                'frequency': frequency,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'notes': notes
            }
            
            if default_values.get('id'):
                result['id'] = default_values['id']
            
            return result
    
    return None

def income_input_form(key="income_form", default_values=None):
    if default_values is None:
        default_values = {}
    
    is_edit = bool(default_values.get('id'))
    header = "✏️ Edit Income" if is_edit else "➕ Add New Income"
    btn_text = "💾 Update Income" if is_edit else "💾 Save Income"
    
    with st.form(key=key):
        st.subheader(header)
        
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.text_input("Income Source *", placeholder="e.g., Salary", key=f"{key}_source", value=default_values.get('source', ''))
            amount = st.number_input("Amount *", min_value=0.0, step=1000.0, key=f"{key}_amount", value=float(default_values.get('amount', 0)))
        
        with col2:
            freq_index = INCOME_FREQUENCIES.index(default_values.get('frequency', 'Monthly')) if default_values.get('frequency') in INCOME_FREQUENCIES else 0
            frequency = st.selectbox("Frequency", INCOME_FREQUENCIES, key=f"{key}_frequency", index=freq_index)
            
            default_due = datetime.strptime(default_values.get('due_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') if default_values.get('due_date') else datetime.now()
            due_date = st.date_input("Receipt Date", default_due, key=f"{key}_due_date", help="When do you receive this income?")
            
            is_active = st.checkbox("Active", value=default_values.get('is_active', True), key=f"{key}_active")
        
        submitted = st.form_submit_button(btn_text, type="primary")
        
        if submitted:
            if not source or amount <= 0:
                st.error("❌ Please fill in all required fields (*)")
                return None
            
            if frequency == "One-time":
                monthly_amount = 0
            else:
                divisor = get_frequency_divisor(frequency)
                monthly_amount = amount / divisor
            
            result = {
                'source': source,
                'amount': amount,
                'monthly_amount': monthly_amount,
                'frequency': frequency,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'is_active': is_active
            }
            
            if is_edit:
                result['id'] = default_values['id']
            
            return result
    
    return None

def category_management_form(key="category_form"):
    with st.form(key=key):
        st.subheader("➕ Add New Category")
        
        new_category = st.text_input("New Category Name", placeholder="e.g., Gym Membership", key=f"{key}_new")
        
        submitted = st.form_submit_button("➕ Add Category")
        
        if submitted:
            if not new_category:
                st.error("❌ Please enter a category name")
                return None
            return new_category.strip()
    
    return None

def settings_form(current_settings, key="settings_form"):
    with st.form(key=key):
        st.subheader("Profile Settings")
        
        emergency_target = st.number_input(
            "Emergency Fund Target",
            value=current_settings.get('emergency_fund_target', 90000),
            min_value=0,
            step=1000
        )
        
        col1, col2 = st.columns(2)
        with col1:
            current_pin = st.text_input("Current PIN", type="password", max_chars=4, key=f"{key}_current_pin")
        with col2:
            new_pin = st.text_input("New PIN (leave blank to keep current)", type="password", max_chars=4, key=f"{key}_new_pin")
        
        submitted = st.form_submit_button("Save Settings", type="primary")
        
        if submitted:
            return {
                'emergency_fund_target': emergency_target,
                'current_pin': current_pin,
                'new_pin': new_pin if new_pin else None
            }
    
    return None
