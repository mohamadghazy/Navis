import hashlib
import json
import os
import streamlit as st
from config import USERS_DIR

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin: str, stored_hash: str) -> bool:
    return hash_pin(pin) == stored_hash

def get_user_settings(username: str) -> dict:
    user_dir = os.path.join(USERS_DIR, username)
    settings_path = os.path.join(user_dir, "settings.json")
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            return json.load(f)
    return {}

def save_user_settings(username: str, settings: dict):
    user_dir = os.path.join(USERS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    settings_path = os.path.join(user_dir, "settings.json")
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

def user_exists(username: str) -> bool:
    user_dir = os.path.join(USERS_DIR, username)
    return os.path.exists(user_dir)

def create_user(username: str, pin: str, **kwargs):
    user_dir = os.path.join(USERS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    
    settings = {
        "user_name": username,
        "pin_hash": hash_pin(pin),
        "emergency_fund_target": kwargs.get("emergency_fund_target", 90000),
        "currency": kwargs.get("currency", "EGP"),
        "created_date": kwargs.get("created_date", None)
    }
    
    save_user_settings(username, settings)
    
    debts_path = os.path.join(user_dir, "debts.csv")
    expenses_path = os.path.join(user_dir, "expenses.csv")
    income_path = os.path.join(user_dir, "income.csv")
    
    if not os.path.exists(debts_path):
        with open(debts_path, 'w') as f:
            f.write("id,name,lender,balance,interest_rate,installment_amount,monthly_payment,frequency,due_date,end_date,status,priority,notes\n")
    
    if not os.path.exists(expenses_path):
        with open(expenses_path, 'w') as f:
            f.write("id,category,amount,monthly_amount,frequency,due_date,notes\n")
    
    if not os.path.exists(income_path):
        with open(income_path, 'w') as f:
            f.write("id,source,amount,monthly_amount,frequency,due_date,is_active\n")

def get_all_users() -> list:
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
        return []
    
    users = []
    for item in os.listdir(USERS_DIR):
        user_dir = os.path.join(USERS_DIR, item)
        if os.path.isdir(user_dir):
            settings_path = os.path.join(user_dir, "settings.json")
            if os.path.exists(settings_path):
                users.append(item)
    return sorted(users)

def login_screen():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⛵ Navis")
    st.markdown("---")
    
    users = get_all_users()
    
    if not users:
        st.markdown("### 👋 Welcome! Create your profile")
        st.markdown("No profiles found. Create your first profile to get started.")
        
        with st.form("create_profile"):
            new_username = st.text_input("Profile Name", placeholder="e.g., Ahmed")
            new_pin = st.text_input("Create PIN (4 digits)", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            
            submitted = st.form_submit_button("Create Profile", type="primary")
            
            if submitted:
                if not new_username:
                    st.error("Please enter a profile name")
                elif not new_pin or not new_pin.isdigit() or len(new_pin) != 4:
                    st.error("PIN must be exactly 4 digits")
                elif new_pin != confirm_pin:
                    st.error("PINs do not match")
                elif user_exists(new_username):
                    st.error("Profile name already exists")
                else:
                    create_user(new_username, new_pin)
                    st.success(f"Profile '{new_username}' created successfully!")
                    st.rerun()
    else:
        st.markdown("### 🔐 Select your profile")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            selected_user = st.selectbox("Choose Profile", users, label_visibility="collapsed")
            
            pin = st.text_input("Enter PIN", type="password", max_chars=4)
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_btn = st.button("Login", type="primary", use_container_width=True)
            with col_b:
                create_btn = st.button("Create New Profile", use_container_width=True)
            
            if login_btn:
                if not pin:
                    st.error("Please enter your PIN")
                else:
                    settings = get_user_settings(selected_user)
                    if verify_pin(pin, settings.get("pin_hash", "")):
                        st.session_state.authenticated = True
                        st.session_state.current_user = selected_user
                        st.session_state.user_settings = settings
                        st.rerun()
                    else:
                        st.error("Incorrect PIN")
            
            if create_btn:
                st.session_state.creating_profile = True
                st.rerun()

def create_profile_screen():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("💰 Create New Profile")
    st.markdown("---")
    
    with st.form("create_new_profile"):
        new_username = st.text_input("Profile Name", placeholder="e.g., Ahmed")
        new_pin = st.text_input("Create PIN (4 digits)", type="password", max_chars=4)
        confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)
        emergency_target = st.number_input("Emergency Fund Target (EGP)", value=90000, min_value=0)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Create Profile", type="primary")
        with col2:
            cancel = st.form_submit_button("Cancel")
        
        if cancel:
            st.session_state.creating_profile = False
            st.rerun()
        
        if submitted:
            if not new_username:
                st.error("Please enter a profile name")
            elif not new_pin or not new_pin.isdigit() or len(new_pin) != 4:
                st.error("PIN must be exactly 4 digits")
            elif new_pin != confirm_pin:
                st.error("PINs do not match")
            elif user_exists(new_username):
                st.error("Profile name already exists")
            else:
                create_user(new_username, new_pin, emergency_fund_target=emergency_target)
                st.success(f"Profile '{new_username}' created successfully!")
                st.session_state.creating_profile = False
                st.rerun()

def logout():
    if "authenticated" in st.session_state:
        st.session_state.authenticated = False
    if "current_user" in st.session_state:
        st.session_state.current_user = None
    if "user_settings" in st.session_state:
        st.session_state.user_settings = None
    st.rerun()
