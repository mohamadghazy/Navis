import os
import pandas as pd
import json
from datetime import datetime
from config import USERS_DIR, EXPENSE_CATEGORIES, DEFAULT_EMERGENCY_FUND_TARGET, DEFAULT_UPCOMING_DAYS

def get_user_dir(username: str) -> str:
    return os.path.join(USERS_DIR, username)

def read_csv(username: str, filename: str) -> pd.DataFrame:
    user_dir = get_user_dir(username)
    filepath = os.path.join(user_dir, filename)
    
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return pd.DataFrame()

def write_csv(username: str, filename: str, df: pd.DataFrame):
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    filepath = os.path.join(user_dir, filename)
    df.to_csv(filepath, index=False)

def get_next_id(df: pd.DataFrame) -> int:
    if df.empty or 'id' not in df.columns:
        return 1
    return int(df['id'].max()) + 1

def add_record(username: str, filename: str, record: dict) -> pd.DataFrame:
    df = read_csv(username, filename)
    
    if 'id' not in record:
        record['id'] = get_next_id(df)
    
    new_df = pd.DataFrame([record])
    df = pd.concat([df, new_df], ignore_index=True)
    write_csv(username, filename, df)
    return df

def update_record(username: str, filename: str, record_id: int, updates: dict) -> pd.DataFrame:
    df = read_csv(username, filename)
    
    if not df.empty and record_id in df['id'].values:
        idx = df[df['id'] == record_id].index[0]
        for key, value in updates.items():
            df.at[idx, key] = value
        write_csv(username, filename, df)
    
    return df

def delete_record(username: str, filename: str, record_id: int) -> pd.DataFrame:
    df = read_csv(username, filename)
    
    if not df.empty and record_id in df['id'].values:
        df = df[df['id'] != record_id]
        write_csv(username, filename, df)
    
    return df

def get_debts(username: str) -> pd.DataFrame:
    return read_csv(username, "debts.csv")

def get_expenses(username: str) -> pd.DataFrame:
    return read_csv(username, "expenses.csv")

def get_income(username: str) -> pd.DataFrame:
    return read_csv(username, "income.csv")

def save_debts(username: str, df: pd.DataFrame):
    write_csv(username, "debts.csv", df)

def save_expenses(username: str, df: pd.DataFrame):
    write_csv(username, "expenses.csv", df)

def save_income(username: str, df: pd.DataFrame):
    write_csv(username, "income.csv", df)

def get_settings(username: str) -> dict:
    user_dir = get_user_dir(username)
    filepath = os.path.join(user_dir, "settings.json")
    
    default_settings = {
        'emergency_fund_target': DEFAULT_EMERGENCY_FUND_TARGET,
        'upcoming_days': DEFAULT_UPCOMING_DAYS
    }
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            settings = json.load(f)
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            return settings
    return default_settings

def save_settings(username: str, settings: dict):
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    filepath = os.path.join(user_dir, "settings.json")
    
    with open(filepath, 'w') as f:
        json.dump(settings, f, indent=2)

def get_budget_template(username: str) -> pd.DataFrame:
    return read_csv(username, "budget_template.csv")

def save_budget_template(username: str, df: pd.DataFrame):
    write_csv(username, "budget_template.csv", df)

def get_tracker(username: str) -> pd.DataFrame:
    return read_csv(username, "tracker.csv")

def save_tracker(username: str, df: pd.DataFrame):
    write_csv(username, "tracker.csv", df)

# Category Management Functions
def get_categories(username: str) -> list:
    """Get all categories (default + custom)"""
    # Get default categories
    categories = list(EXPENSE_CATEGORIES)
    
    # Get custom categories from user
    custom_df = read_csv(username, "categories.csv")
    if not custom_df.empty and 'category' in custom_df.columns:
        custom_cats = custom_df['category'].tolist()
        categories.extend(custom_cats)
    
    return sorted(list(set(categories)))

def add_category(username: str, category: str) -> bool:
    """Add a custom category"""
    if not category or category in EXPENSE_CATEGORIES:
        return False
    
    df = read_csv(username, "categories.csv")
    
    # Check if already exists
    if not df.empty and category in df['category'].values:
        return False
    
    new_df = pd.DataFrame([{'category': category, 'added_date': datetime.now().strftime('%Y-%m-%d')}])
    df = pd.concat([df, new_df], ignore_index=True)
    write_csv(username, "categories.csv", df)
    return True

def delete_category(username: str, category: str) -> bool:
    """Delete a custom category"""
    if category in EXPENSE_CATEGORIES:
        return False  # Can't delete default categories
    
    df = read_csv(username, "categories.csv")
    if not df.empty and category in df['category'].values:
        df = df[df['category'] != category]
        write_csv(username, "categories.csv", df)
        return True
    return False

def get_custom_categories(username: str) -> list:
    """Get only custom categories"""
    df = read_csv(username, "categories.csv")
    if not df.empty and 'category' in df.columns:
        return sorted(df['category'].tolist())
    return []

def initialize_user_files(username: str):
    user_dir = get_user_dir(username)
    os.makedirs(user_dir, exist_ok=True)
    
    # Debts CSV - Updated schema
    debts_path = os.path.join(user_dir, "debts.csv")
    if not os.path.exists(debts_path):
        pd.DataFrame(columns=[
            "id", "name", "lender", "balance", "interest_rate", 
            "installment_amount", "monthly_payment", "frequency", 
            "due_date", "end_date", "status", "priority", "notes"
        ]).to_csv(debts_path, index=False)
    
    # Expenses CSV - Updated schema
    expenses_path = os.path.join(user_dir, "expenses.csv")
    if not os.path.exists(expenses_path):
        pd.DataFrame(columns=[
            "id", "category", "amount", "monthly_amount", "frequency", 
            "due_date", "notes"
        ]).to_csv(expenses_path, index=False)
    
    # Income CSV - Updated schema
    income_path = os.path.join(user_dir, "income.csv")
    if not os.path.exists(income_path):
        pd.DataFrame(columns=[
            "id", "source", "amount", "monthly_amount", "frequency", 
            "due_date", "is_active"
        ]).to_csv(income_path, index=False)
    
    # Categories CSV
    categories_path = os.path.join(user_dir, "categories.csv")
    if not os.path.exists(categories_path):
        pd.DataFrame(columns=["category", "added_date"]).to_csv(categories_path, index=False)
    
    # Payment Records CSV
    payment_records_path = os.path.join(user_dir, "payment_records.csv")
    if not os.path.exists(payment_records_path):
        pd.DataFrame(columns=[
            "id", "source_type", "source_id", "source_name", 
            "due_date", "payment_date", "budgeted_amount", "actual_amount",
            "month", "payment_points", "savings_points", "created_at"
        ]).to_csv(payment_records_path, index=False)

def get_payment_records(username: str) -> pd.DataFrame:
    return read_csv(username, "payment_records.csv")

def save_payment_records(username: str, df: pd.DataFrame):
    write_csv(username, "payment_records.csv", df)

def add_payment_record(username: str, record: dict) -> pd.DataFrame:
    return add_record(username, "payment_records.csv", record)

def get_payment_record_by_source_and_month(username: str, source_type: str, source_id: int, month: str) -> pd.DataFrame:
    df = get_payment_records(username)
    if df.empty:
        return pd.DataFrame()
    return df[(df['source_type'] == source_type) & (df['source_id'] == source_id) & (df['month'] == month)]

def get_monthly_payment_records(username: str, month: str) -> pd.DataFrame:
    df = get_payment_records(username)
    if df.empty:
        return pd.DataFrame()
    return df[df['month'] == month]

def update_payment_record(username: str, record_id: int, updates: dict) -> pd.DataFrame:
    return update_record(username, "payment_records.csv", record_id, updates)

def delete_payment_record(username: str, record_id: int) -> pd.DataFrame:
    return delete_record(username, "payment_records.csv", record_id)
