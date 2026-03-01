from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

def generate_monthly_projection(
    income_df: pd.DataFrame,
    expenses_df: pd.DataFrame,
    debts_df: pd.DataFrame,
    emergency_fund_target: float,
    starting_balance: float = 0,
    months: int = 36,
    username: str = None
) -> pd.DataFrame:
    from core.calculations import (
        calculate_total_monthly_income,
        calculate_total_monthly_expenses,
        calculate_total_monthly_debt,
        get_actual_expenses_for_month
    )
    
    projections = []
    current_date = datetime.now()
    cumulative_savings = starting_balance
    
    budgeted_expenses = calculate_total_monthly_expenses(expenses_df)
    
    expenses_list = expenses_df.to_dict('records') if not expenses_df.empty else []
    debts_list = debts_df.to_dict('records') if not debts_df.empty else []
    active_debts = [d for d in debts_list if d.get('status') == 'Active']
    
    for month_num in range(1, months + 1):
        projection_date = current_date + relativedelta(months=month_num - 1)
        month_str = projection_date.strftime('%Y-%m')
        
        monthly_income = calculate_total_monthly_income(income_df, projection_date)
        
        month_debt_payment = 0
        for debt in active_debts:
            # Check END date - skip if debt already ended
            end_date_str = debt.get('end_date')
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    if end_date.year < projection_date.year or (end_date.year == projection_date.year and end_date.month < projection_date.month):
                        continue
                except:
                    pass
            
            # Check START date - skip if debt hasn't started yet (due_date is in the future)
            due_date_str = debt.get('due_date')
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                    if due_date.year > projection_date.year or (due_date.year == projection_date.year and due_date.month > projection_date.month):
                        continue  # Debt starts in the future, skip this month
                except:
                    pass
            
            month_debt_payment += debt.get('monthly_payment', 0)
        
        # Use actual expenses if available, otherwise use budgeted (filtered by start date)
        if username:
            actual_expenses = get_actual_expenses_for_month(username, month_str)
            if actual_expenses > 0:
                monthly_expenses = actual_expenses
            else:
                # Filter expenses by start date
                monthly_expenses = 0
                for expense in expenses_list:
                    due_date_str = expense.get('due_date')
                    if due_date_str:
                        try:
                            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                            if due_date.year < projection_date.year or (due_date.year == projection_date.year and due_date.month <= projection_date.month):
                                monthly_expenses += expense.get('monthly_amount', 0)
                        except:
                            pass
                if monthly_expenses == 0:
                    monthly_expenses = budgeted_expenses
        else:
            # Filter expenses by start date
            monthly_expenses = 0
            for expense in expenses_list:
                due_date_str = expense.get('due_date')
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                        if due_date.year < projection_date.year or (due_date.year == projection_date.year and due_date.month <= projection_date.month):
                            monthly_expenses += expense.get('monthly_amount', 0)
                    except:
                        pass
            if monthly_expenses == 0:
                monthly_expenses = budgeted_expenses
        
        monthly_surplus = monthly_income - monthly_expenses - month_debt_payment
        cumulative_savings += max(monthly_surplus, 0)
        
        progress_pct = min((cumulative_savings / emergency_fund_target) * 100, 100)
        
        projections.append({
            'month': month_num,
            'date': projection_date.strftime('%Y-%m'),
            'income': monthly_income,
            'expenses': monthly_expenses,
            'debt_payment': month_debt_payment,
            'surplus': monthly_surplus,
            'cumulative_savings': cumulative_savings,
            'target': emergency_fund_target,
            'progress_pct': progress_pct,
            'target_reached': cumulative_savings >= emergency_fund_target
        })
    
    return pd.DataFrame(projections)

def generate_budget_template(
    income_df: pd.DataFrame,
    expenses_df: pd.DataFrame,
    debts_df: pd.DataFrame,
    months: int = 12,
    username: str = None
) -> pd.DataFrame:
    from core.calculations import (
        calculate_total_monthly_income,
        calculate_total_monthly_expenses,
        calculate_total_monthly_debt,
        get_actual_expenses_for_month
    )
    
    budgeted_expenses = calculate_total_monthly_expenses(expenses_df)
    
    debts_list = debts_df.to_dict('records') if not debts_df.empty else []
    active_debts = [d for d in debts_list if d.get('status') == 'Active']
    
    current_date = datetime.now()
    budget_rows = []
    
    for month_num in range(1, months + 1):
        projection_date = current_date + relativedelta(months=month_num - 1)
        month_str = projection_date.strftime('%Y-%m')
        
        monthly_income = calculate_total_monthly_income(income_df, projection_date)
        
        month_debt = 0
        for debt in active_debts:
            end_date_str = debt.get('end_date')
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    if end_date.year < projection_date.year or (end_date.year == projection_date.year and end_date.month < projection_date.month):
                        continue
                except:
                    pass
            month_debt += debt.get('monthly_payment', 0)
        
        # Use actual expenses if available, otherwise use budgeted
        if username:
            actual_expenses = get_actual_expenses_for_month(username, month_str)
            if actual_expenses > 0:
                monthly_expenses = actual_expenses
            else:
                monthly_expenses = budgeted_expenses
        else:
            monthly_expenses = budgeted_expenses
        
        surplus = monthly_income - monthly_expenses - month_debt
        
        budget_rows.append({
            'month': month_num,
            'date': projection_date.strftime('%b-%Y'),
            'income': monthly_income,
            'expenses': monthly_expenses,
            'debt_payments': month_debt,
            'surplus': surplus,
            'savings': max(surplus, 0)
        })
    
    return pd.DataFrame(budget_rows)

def forecast_emergency_fund_completion(
    income_df,
    expenses_df,
    debts_df,
    target: float,
    starting_balance: float = 0
) -> dict:
    from core.calculations import (
        calculate_total_monthly_income,
        calculate_total_monthly_expenses,
        calculate_total_monthly_debt
    )
    
    current_date = datetime.now()
    cumulative_savings = starting_balance
    
    monthly_expenses = calculate_total_monthly_expenses(expenses_df)
    
    debts_list = debts_df.to_dict('records') if not debts_df.empty else []
    active_debts = [d for d in debts_list if d.get('status') == 'Active']
    
    for month_num in range(1, 601):
        projection_date = current_date + relativedelta(months=month_num - 1)
        
        monthly_income = calculate_total_monthly_income(income_df, projection_date)
        
        month_debt_payment = 0
        for debt in active_debts:
            end_date_str = debt.get('end_date')
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    if end_date.year < projection_date.year or (end_date.year == projection_date.year and end_date.month < projection_date.month):
                        continue
                except:
                    pass
            month_debt_payment += debt.get('monthly_payment', 0)
        
        monthly_surplus = monthly_income - monthly_expenses - month_debt_payment
        
        if monthly_surplus > 0:
            cumulative_savings += monthly_surplus
        
        if cumulative_savings >= target:
            completion_date = current_date + relativedelta(months=month_num)
            return {
                'months': month_num,
                'date': completion_date.strftime('%B %Y'),
                'achievable': True,
                'final_balance': cumulative_savings
            }
    
    return {
        'months': -1,
        'date': None,
        'achievable': False
    }
