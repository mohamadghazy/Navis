import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_handler import get_settings, save_settings, get_categories, add_category, delete_category, get_custom_categories
from auth import hash_pin, verify_pin
from config import CURRENCY, EXPENSE_CATEGORIES, DEFAULT_EMERGENCY_FUND_TARGET, DEFAULT_UPCOMING_DAYS

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("Navis.py")

username = st.session_state.current_user
settings = st.session_state.user_settings

st.title("⚙️ Settings")
st.markdown("Manage your profile and preferences")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "📝 Categories", "🎯 Goals", "ℹ️ About"])

with tab1:
    st.subheader("👤 Profile Settings")
    
    st.markdown(f"**Profile Name:** {username}")
    st.markdown(f"**Created Date:** {settings.get('created_date', 'N/A')}")
    
    st.markdown("---")
    
    st.markdown("### 🔐 Change PIN")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_pin = st.text_input("Current PIN", type="password", max_chars=4, key="current_pin")
    
    with col2:
        new_pin = st.text_input("New PIN", type="password", max_chars=4, key="new_pin")
    
    confirm_pin = st.text_input("Confirm New PIN", type="password", max_chars=4, key="confirm_pin")
    
    if st.button("Update PIN", type="primary"):
        if not current_pin or not new_pin or not confirm_pin:
            st.error("❌ Please fill in all PIN fields")
        elif not verify_pin(current_pin, settings.get('pin_hash', '')):
            st.error("❌ Current PIN is incorrect")
        elif not new_pin.isdigit() or len(new_pin) != 4:
            st.error("❌ New PIN must be exactly 4 digits")
        elif new_pin != confirm_pin:
            st.error("❌ New PINs do not match")
        else:
            settings['pin_hash'] = hash_pin(new_pin)
            save_settings(username, settings)
            st.session_state.user_settings = settings
            st.toast("PIN updated successfully!")

with tab2:
    st.subheader("📝 Expense Categories")
    st.markdown("Manage your expense categories")
    
    st.markdown("#### Default Categories")
    st.info(f"Default: {', '.join(EXPENSE_CATEGORIES)}")
    
    st.markdown("---")
    
    # Add new category
    col1, col2 = st.columns([3, 1])
    with col1:
        new_category = st.text_input("Add New Category", placeholder="e.g., Gym Membership", key="new_category_input")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", key="add_category_btn"):
            if new_category.strip():
                if add_category(username, new_category.strip()):
                    st.toast(f"Category '{new_category}' added!")
                    st.rerun()
                else:
                    st.error("❌ Category already exists or is a default category")
            else:
                st.error("❌ Please enter a category name")
    
    st.markdown("---")
    
    # Show custom categories
    st.markdown("#### Custom Categories")
    custom_cats = get_custom_categories(username)
    
    if custom_cats:
        for cat in custom_cats:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"• {cat}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_cat_{cat}"):
                    if delete_category(username, cat):
                        st.toast(f"Category '{cat}' deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Could not delete category")
    else:
        st.info("No custom categories added yet.")

with tab3:
    st.subheader("🎯 Financial Goals")
    
    st.markdown("#### Emergency Fund Target")
    
    current_target = settings.get('emergency_fund_target', 90000)
    
    new_target = st.number_input(
        "Emergency Fund Target",
        value=current_target,
        min_value=0,
        step=1000,
        key="emergency_target"
    )
    
    if st.button("Save Target", type="primary"):
        settings['emergency_fund_target'] = new_target
        save_settings(username, settings)
        st.session_state.user_settings = settings
        st.toast(f"Emergency fund target updated to {CURRENCY} {new_target:,.0f}")
    
    st.markdown("---")
    
    st.markdown("#### 📅 Payment Tracking")
    
    current_upcoming = settings.get('upcoming_days', DEFAULT_UPCOMING_DAYS)
    
    upcoming_days = st.number_input(
        "Upcoming Payments Window (Days)",
        value=current_upcoming,
        min_value=1,
        max_value=60,
        step=1,
        key="upcoming_days"
    )
    
    if st.button("Save Payment Window", type="primary"):
        settings['upcoming_days'] = upcoming_days
        save_settings(username, settings)
        st.session_state.user_settings = settings
        st.toast(f"Payment window updated to {upcoming_days} days")
    
    st.caption(f"Shows payments due within the next {upcoming_days} days in the Payment Tracking section.")
    
    st.markdown("---")
    
    st.markdown("#### 💡 Goal Recommendations")
    
    from utils.file_handler import get_expenses
    from core.calculations import calculate_total_monthly_expenses
    
    expenses_df = get_expenses(username)
    monthly_expenses = calculate_total_monthly_expenses(expenses_df)
    
    if monthly_expenses > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("3 Months (Minimum)", f"{CURRENCY} {monthly_expenses * 3:,.0f}")
        
        with col2:
            st.metric("6 Months (Recommended)", f"{CURRENCY} {monthly_expenses * 6:,.0f}")
        
        with col3:
            st.metric("9 Months (Conservative)", f"{CURRENCY} {monthly_expenses * 9:,.0f}")
    else:
        st.info("Add expenses to see goal recommendations")

with tab4:
    st.subheader("ℹ️ About Navis")
    
    st.markdown("""
    ### ⛵ Navis v1.0.0
    
    A privacy-focused personal finance management application.
    
    #### Features:
    - 💰 Debt management with payoff strategies
    - 💸 Expense tracking and categorization
    - 💵 Income management
    - 📋 Budget planning and projections
    - 📄 PDF and Excel report generation
    - 🔐 PIN-protected profiles
    
    #### Privacy:
    - ✅ All data stored locally
    - ✅ No internet connection required
    - ✅ No external APIs or services
    - ✅ Complete data ownership
    
    #### Data Storage:
    - 📁 CSV files in your local directory
    - 🔄 Easy backup and export
    - 📤 Migration-ready for future database
    
    ---
    
    **Developed for personal financial planning**
    
    **Currency:** Egyptian Pound (EGP)
    """)
    
    st.markdown("---")
    
    st.markdown("#### 📁 Data Location")
    
    from config import USERS_DIR
    
    user_dir = os.path.join(USERS_DIR, username)
    st.code(user_dir, language="plaintext")
    
    st.markdown("#### 📄 Files")
    
    files_info = [
        ("debts.csv", "Debt records"),
        ("expenses.csv", "Expense records"),
        ("income.csv", "Income records"),
        ("categories.csv", "Custom categories"),
        ("settings.json", "Profile settings")
    ]
    
    for filename, description in files_info:
        filepath = os.path.join(user_dir, filename)
        exists = "✅" if os.path.exists(filepath) else "❌"
        st.markdown(f"{exists} `{filename}` - {description}")
