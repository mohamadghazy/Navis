import pandas as pd
from typing import List, Dict

def snowball_strategy(debts_df: pd.DataFrame) -> pd.DataFrame:
    if debts_df.empty:
        return debts_df
    
    active_debts = debts_df[debts_df['status'] == 'Active'].copy()
    inactive_debts = debts_df[debts_df['status'] != 'Active'].copy()
    
    sorted_debts = active_debts.sort_values('balance', ascending=True)
    
    sorted_debts['strategy_rank'] = range(1, len(sorted_debts) + 1)
    
    return pd.concat([sorted_debts, inactive_debts], ignore_index=True)

def avalanche_strategy(debts_df: pd.DataFrame) -> pd.DataFrame:
    if debts_df.empty:
        return debts_df
    
    active_debts = debts_df[debts_df['status'] == 'Active'].copy()
    inactive_debts = debts_df[debts_df['status'] != 'Active'].copy()
    
    active_debts['interest_rate'] = active_debts['interest_rate'].fillna(0)
    sorted_debts = active_debts.sort_values('interest_rate', ascending=False)
    
    sorted_debts['strategy_rank'] = range(1, len(sorted_debts) + 1)
    
    return pd.concat([sorted_debts, inactive_debts], ignore_index=True)

def calculate_snowball_payoff(debts_df: pd.DataFrame, extra_payment: float = 0) -> List[Dict]:
    if debts_df.empty:
        return []
    
    sorted_debts = snowball_strategy(debts_df)
    active_debts = sorted_debts[sorted_debts['status'] == 'Active'].to_dict('records')
    
    payoff_plan = []
    current_extra = extra_payment
    
    for i, debt in enumerate(active_debts):
        balance = debt['balance']
        monthly_payment = debt['monthly_payment']
        interest_rate = debt.get('interest_rate', 0) or 0
        
        total_monthly = monthly_payment + current_extra
        
        months = 0
        remaining_balance = balance
        
        while remaining_balance > 0 and total_monthly > 0:
            interest = remaining_balance * (interest_rate / 100 / 12)
            remaining_balance += interest
            remaining_balance -= total_monthly
            months += 1
            
            if months > 600:
                break
        
        payoff_plan.append({
            'rank': i + 1,
            'name': debt['name'],
            'balance': balance,
            'monthly_payment': monthly_payment,
            'extra_payment': current_extra,
            'total_payment': total_monthly,
            'months_to_payoff': months,
            'interest_paid': remaining_balance - balance if remaining_balance < 0 else 0
        })
        
        current_extra += monthly_payment
    
    return payoff_plan

def calculate_avalanche_payoff(debts_df: pd.DataFrame, extra_payment: float = 0) -> List[Dict]:
    if debts_df.empty:
        return []
    
    sorted_debts = avalanche_strategy(debts_df)
    active_debts = sorted_debts[sorted_debts['status'] == 'Active'].to_dict('records')
    
    payoff_plan = []
    current_extra = extra_payment
    
    for i, debt in enumerate(active_debts):
        balance = debt['balance']
        monthly_payment = debt['monthly_payment']
        interest_rate = debt.get('interest_rate', 0) or 0
        
        total_monthly = monthly_payment + current_extra
        
        months = 0
        remaining_balance = balance
        
        while remaining_balance > 0 and total_monthly > 0:
            interest = remaining_balance * (interest_rate / 100 / 12)
            remaining_balance += interest
            remaining_balance -= total_monthly
            months += 1
            
            if months > 600:
                break
        
        payoff_plan.append({
            'rank': i + 1,
            'name': debt['name'],
            'balance': balance,
            'interest_rate': interest_rate,
            'monthly_payment': monthly_payment,
            'extra_payment': current_extra,
            'total_payment': total_monthly,
            'months_to_payoff': months
        })
        
        current_extra += monthly_payment
    
    return payoff_plan

def compare_strategies(debts_df: pd.DataFrame, extra_payment: float = 0) -> Dict:
    if debts_df.empty:
        return {}
    
    snowball_plan = calculate_snowball_payoff(debts_df, extra_payment)
    avalanche_plan = calculate_avalanche_payoff(debts_df, extra_payment)
    
    snowball_months = sum(p['months_to_payoff'] for p in snowball_plan) if snowball_plan else 0
    avalanche_months = sum(p['months_to_payoff'] for p in avalanche_plan) if avalanche_plan else 0
    
    return {
        'snowball': {
            'total_months': snowball_months,
            'plan': snowball_plan
        },
        'avalanche': {
            'total_months': avalanche_months,
            'plan': avalanche_plan
        },
        'difference_months': abs(snowball_months - avalanche_months)
    }
