from datetime import datetime
from core.calculations import (
    calculate_total_debt_balance,
    calculate_total_monthly_income,
    calculate_total_monthly_expenses,
    calculate_total_monthly_debt,
    calculate_monthly_surplus
)

def get_financial_summary(username, target_date=None):
    """
    Single source of truth for all financial calculations.
    
    Args:
        username: The username for the current user
        target_date: Optional datetime to calculate monthly values for specific month
                    (e.g., for including one-time income or respecting debt end dates)
    
    Returns:
        Dictionary containing:
        - debts_df: DataFrame of all debts
        - expenses_df: DataFrame of all expenses
        - income_df: DataFrame of all income
        - total_debt: Total balance of active debts
        - monthly_income: Monthly income (recurring + one-time for target month)
        - monthly_expenses: Monthly expenses
        - monthly_debt: Monthly debt payments
        - monthly_surplus: Income - Expenses - Debt
    """
    from utils.file_handler import get_debts, get_expenses, get_income
    
    debts_df = get_debts(username)
    expenses_df = get_expenses(username)
    income_df = get_income(username)
    
    return {
        'debts_df': debts_df,
        'expenses_df': expenses_df,
        'income_df': income_df,
        'total_debt': calculate_total_debt_balance(debts_df),
        'monthly_income': calculate_total_monthly_income(income_df, target_date),
        'monthly_expenses': calculate_total_monthly_expenses(expenses_df),
        'monthly_debt': calculate_total_monthly_debt(debts_df, target_date),
        'monthly_surplus': calculate_monthly_surplus(income_df, expenses_df, debts_df, target_date),
    }
