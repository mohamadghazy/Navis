import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_monthly_payment(amount: float, frequency: str) -> float:
    if frequency == "Monthly":
        return amount
    elif frequency == "Quarterly":
        return amount / 3
    elif frequency == "One-time":
        return 0
    return amount

def calculate_total_monthly_debt(debts_df: pd.DataFrame, target_date: datetime = None) -> float:
    if debts_df.empty:
        return 0.0
    
    active_debts = debts_df[debts_df['status'] == 'Active']
    
    if target_date is None:
        return active_debts['monthly_payment'].sum()
    
    total = 0.0
    for _, row in active_debts.iterrows():
        end_date_str = row.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                if end_date.year < target_date.year or (end_date.year == target_date.year and end_date.month < target_date.month):
                    continue
            except:
                pass
        total += row.get('monthly_payment', 0)
    
    return total

def calculate_total_monthly_expenses(expenses_df: pd.DataFrame) -> float:
    if expenses_df.empty:
        return 0.0
    
    return expenses_df['monthly_amount'].sum()

def calculate_total_monthly_income(income_df: pd.DataFrame, target_date: datetime = None) -> float:
    if income_df.empty:
        return 0.0
    
    active_income = income_df[income_df['is_active'] == True]
    
    recurring_income = active_income[active_income['frequency'] != 'One-time']
    total = recurring_income['monthly_amount'].sum()
    
    if target_date is not None:
        today = datetime.now().date()
        target_month_start = target_date.replace(day=1).date()
        target_month_end = ((target_date.replace(day=28) + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)).date()
        
        one_time_income = active_income[active_income['frequency'] == 'One-time']
        for _, row in one_time_income.iterrows():
            try:
                receipt_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                if receipt_date >= today and target_month_start <= receipt_date <= target_month_end:
                    total += row['amount']
            except:
                pass
    
    return total

def calculate_monthly_surplus(income_df: pd.DataFrame, expenses_df: pd.DataFrame, debts_df: pd.DataFrame, target_date: datetime = None) -> float:
    total_income = calculate_total_monthly_income(income_df, target_date)
    total_expenses = calculate_total_monthly_expenses(expenses_df)
    total_debts = calculate_total_monthly_debt(debts_df, target_date)
    
    return total_income - total_expenses - total_debts

def calculate_avg_monthly_debt(debts_df: pd.DataFrame, months: int = 12) -> float:
    if debts_df.empty:
        return 0.0
    
    active_debts = debts_df[debts_df['status'] == 'Active']
    if active_debts.empty:
        return 0.0
    
    debts_list = active_debts.to_dict('records')
    current_date = datetime.now()
    
    total_payment = 0.0
    
    for month_num in range(months):
        projection_date = current_date + relativedelta(months=month_num)
        
        month_payment = 0.0
        for debt in debts_list:
            end_date_str = debt.get('end_date')
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    if end_date.year < projection_date.year or (end_date.year == projection_date.year and end_date.month < projection_date.month):
                        continue
                except:
                    pass
            month_payment += debt.get('monthly_payment', 0)
        
        total_payment += month_payment
    
    return total_payment / months

def calculate_avg_monthly_expenses(expenses_df: pd.DataFrame, months: int = 12) -> float:
    if expenses_df.empty:
        return 0.0
    
    return expenses_df['monthly_amount'].sum()

def calculate_avg_monthly_income(income_df: pd.DataFrame, months: int = 12) -> float:
    if income_df.empty:
        return 0.0
    
    active_income = income_df[income_df['is_active'] == True]
    if active_income.empty:
        return 0.0
    
    recurring_income = active_income[active_income['frequency'] != 'One-time']
    recurring_total = recurring_income['monthly_amount'].sum()
    
    current_date = datetime.now()
    one_time_income = active_income[active_income['frequency'] == 'One-time']
    one_time_total = 0.0
    
    for month_num in range(months):
        projection_date = current_date + relativedelta(months=month_num)
        target_month_start = projection_date.replace(day=1)
        target_month_end = (projection_date.replace(day=28) + relativedelta(months=1)).replace(day=1).date() - relativedelta(days=1)
        
        for _, row in one_time_income.iterrows():
            try:
                receipt_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                if target_month_start <= receipt_date <= target_month_end:
                    one_time_total += row['amount']
            except:
                pass
    
    return (recurring_total * months + one_time_total) / months

def calculate_avg_monthly_surplus(income_df: pd.DataFrame, expenses_df: pd.DataFrame, debts_df: pd.DataFrame, months: int = 12) -> float:
    avg_income = calculate_avg_monthly_income(income_df, months)
    avg_expenses = calculate_avg_monthly_expenses(expenses_df, months)
    avg_debt = calculate_avg_monthly_debt(debts_df, months)
    
    return avg_income - avg_expenses - avg_debt

def calculate_emergency_fund_timeline(target: float, monthly_surplus: float) -> int:
    if monthly_surplus <= 0:
        return -1
    import math
    return math.ceil(target / monthly_surplus)

def calculate_debt_payoff_months(balance: float, monthly_payment: float, interest_rate: float = 0) -> int:
    if monthly_payment <= 0:
        return -1
    
    if interest_rate <= 0:
        import math
        return math.ceil(balance / monthly_payment)
    
    monthly_rate = interest_rate / 100 / 12
    
    if monthly_payment <= balance * monthly_rate:
        return -1
    
    import math
    n = math.log(monthly_payment / (monthly_payment - balance * monthly_rate)) / math.log(1 + monthly_rate)
    return math.ceil(n)

def calculate_total_debt_balance(debts_df: pd.DataFrame) -> float:
    if debts_df.empty:
        return 0.0
    
    active_debts = debts_df[debts_df['status'] == 'Active']
    return active_debts['balance'].sum()

def calculate_debt_payoff_projection(debts_df: pd.DataFrame, start_date: datetime = None) -> list:
    if debts_df.empty:
        return []
    
    if start_date is None:
        start_date = datetime.now()
    
    projections = []
    active_debts = debts_df[debts_df['status'] == 'Active'].copy()
    
    for _, row in active_debts.iterrows():
        balance = row.get('balance', 0)
        payment = row.get('monthly_payment', 0)
        interest = row.get('interest_rate', 0)
        
        months = calculate_debt_payoff_months(balance, payment, interest)
        
        if months > 0:
            payoff_date = start_date + relativedelta(months=months)
            projections.append({
                'name': row.get('name', ''),
                'balance': balance,
                'monthly_payment': payment,
                'months_to_payoff': months,
                'payoff_date': payoff_date.strftime('%Y-%m-%d')
            })
    
    return sorted(projections, key=lambda x: x['months_to_payoff'])

def calculate_savings_projection(monthly_surplus: float, months: int, starting_balance: float = 0) -> list:
    if monthly_surplus <= 0:
        return []
    
    projections = []
    balance = starting_balance
    
    for month in range(1, months + 1):
        balance += monthly_surplus
        projections.append({
            'month': month,
            'balance': balance
        })
    
    return projections

def calculate_payment_points(budgeted_amount: float, actual_amount: float, due_date, payment_date) -> tuple:
    """
    Calculate payment points and savings points for a payment.
    
    Returns: (payment_points, savings_points)
    - payment_points: +1 for on-time, -2 for late (for debts AND expenses)
    - savings_points: + (under budget) or - (over budget), max +/-10 (expenses only)
    """
    from datetime import date
    
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    if isinstance(payment_date, str):
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
    
    payment_points = 0
    savings_points = 0
    
    if payment_date <= due_date:
        payment_points = 1
    else:
        payment_points = -2
    
    savings_points = 0
    
    return payment_points, savings_points

def get_payment_points_milestone(points: int) -> dict:
    """Get milestone info for payment points."""
    milestones = [
        (0, "🌱 Newbie"),
        (6, "📝 Consistent"),
        (16, "⏰ Punctual"),
        (31, "🎯 Reliable"),
        (51, "💎 Professional"),
        (101, "👑 Master"),
        (201, "🏆 Legend"),
    ]
    
    if points < 0:
        return {
            'title': "⚠️ Needs Improvement",
            'next_title': "🌱 Newbie",
            'next_threshold': 0,
            'progress': 0
        }
    
    title = milestones[0][1]
    next_threshold = milestones[1][0]
    next_title = milestones[1][1]
    
    for threshold, milestone_title in milestones:
        if points >= threshold:
            title = milestone_title
            next_threshold = threshold
    
    for threshold, milestone_title in milestones:
        if points < threshold:
            next_threshold = threshold
            next_title = milestone_title
            break
    
    progress = 0
    if next_threshold > points:
        for i, (threshold, _) in enumerate(milestones):
            if points < threshold:
                prev_threshold = milestones[i-1][0] if i > 0 else 0
                if threshold > prev_threshold:
                    progress = ((points - prev_threshold) / (threshold - prev_threshold)) * 100
                break
    
    return {
        'title': title,
        'next_title': next_title,
        'next_threshold': next_threshold,
        'progress': max(0, min(progress, 100))
    }

def get_savings_points_milestone(points: int) -> dict:
    """Get milestone info for savings points."""
    if points < 0:
        return {
            'title': "⚠️ Needs Improvement",
            'next_title': "🌱 Spender",
            'next_threshold': 0,
            'progress': 0
        }
    
    milestones = [
        (0, "🌱 Spender"),
        (11, "💰 Watchful"),
        (26, "🎯 Budgeter"),
        (51, "🏦 Saver"),
        (101, "💎 Frugal"),
        (201, "🐙 Minimalist"),
    ]
    
    title = milestones[0][1]
    next_threshold = milestones[1][0]
    next_title = milestones[1][1]
    
    for threshold, milestone_title in milestones:
        if points >= threshold:
            title = milestone_title
            next_threshold = threshold
    
    for threshold, milestone_title in milestones:
        if points < threshold:
            next_threshold = threshold
            next_title = milestone_title
            break
    
    progress = 0
    if next_threshold > points:
        for i, (threshold, _) in enumerate(milestones):
            if points < threshold:
                prev_threshold = milestones[i-1][0] if i > 0 else 0
                progress = ((points - prev_threshold) / (threshold - prev_threshold)) * 100
                break
    
    return {
        'title': title,
        'next_title': next_title,
        'next_threshold': next_threshold,
        'progress': min(progress, 100)
    }

def calculate_savings_points(budgeted_amount: float, actual_amount: float) -> int:
    """
    Calculate savings points for an expense.
    - Under budget: + (savings / budgeted * 10), max +10
    - Over budget: - (overspend / budgeted * 10), max -10
    Only applies to expenses (not debts).
    """
    if budgeted_amount <= 0:
        return 0
    
    difference = budgeted_amount - actual_amount
    percentage = (difference / budgeted_amount) * 10
    
    if percentage > 10:
        percentage = 10
    elif percentage < -10:
        percentage = -10
    
    return round(percentage)

def get_total_payment_points(payment_records_df) -> dict:
    """Get total payment points and breakdown."""
    if payment_records_df.empty:
        return {
            'total': 0,
            'on_time': 0,
            'late': 0
        }
    
    on_time = payment_records_df[payment_records_df['payment_points'] > 0]['payment_points'].sum()
    late = payment_records_df[payment_records_df['payment_points'] < 0]['payment_points'].sum()
    
    return {
        'total': on_time + late,
        'on_time': on_time,
        'late': late
    }

def get_total_savings_points(payment_records_df) -> dict:
    """Get total savings points and breakdown."""
    if payment_records_df.empty:
        return {
            'total': 0,
            'under_budget': 0,
            'over_budget': 0
        }
    
    under_budget = payment_records_df[payment_records_df['savings_points'] > 0]['savings_points'].sum()
    over_budget = payment_records_df[payment_records_df['savings_points'] < 0]['savings_points'].sum()
    
    return {
        'total': under_budget + over_budget,
        'under_budget': under_budget,
        'over_budget': over_budget
    }

def calculate_actual_monthly_surplus(username, income_df, expenses_df, debts_df, month: str) -> float:
    """Calculate actual surplus for a specific month based on payment records."""
    from utils.file_handler import get_payment_records
    
    payment_records = get_payment_records(username)
    
    if payment_records.empty or month not in payment_records['month'].values:
        return None
    
    month_records = payment_records[payment_records['month'] == month]
    
    budgeted_income = calculate_total_monthly_income(income_df)
    actual_expenses = month_records[month_records['source_type'] == 'expense']['actual_amount'].sum()
    actual_debt = month_records[month_records['source_type'] == 'debt']['actual_amount'].sum()
    
    return budgeted_income - actual_expenses - actual_debt

def get_actual_expenses_for_month(username, month: str) -> float:
    """Get actual expenses paid for a specific month from payment records."""
    from utils.file_handler import get_payment_records
    
    payment_records = get_payment_records(username)
    
    if payment_records.empty:
        return 0.0
    
    month_records = payment_records[
        (payment_records['month'] == month) & 
        (payment_records['source_type'] == 'expense')
    ]
    
    return month_records['actual_amount'].sum()
