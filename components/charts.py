import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import CURRENCY, CHART_COLORS

def create_debt_bar_chart(debts_df, title="Debt Balances"):
    if debts_df.empty:
        return go.Figure()
    
    active_debts = debts_df[debts_df['status'] == 'Active'].copy()
    
    if active_debts.empty:
        return go.Figure()
    
    fig = px.bar(
        active_debts.sort_values('balance', ascending=True),
        x='balance',
        y='name',
        orientation='h',
        title=title,
        color='balance',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title=f"Balance ({CURRENCY})",
        yaxis_title="",
        height=400,
        showlegend=False
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Balance: ' + CURRENCY + ' %{x:,.0f}<extra></extra>'
    )
    
    return fig

def create_expense_pie_chart(expenses_df, title="Expense Breakdown"):
    if expenses_df.empty:
        return go.Figure()
    
    expense_by_category = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(
        expense_by_category,
        values='amount',
        names='category',
        title=title,
        hole=0.4
    )
    
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: ' + CURRENCY + ' %{value:,.0f}<br>%{percent}<extra></extra>'
    )
    
    return fig

def create_savings_line_chart(projections_df, target, title="Emergency Fund Progress"):
    if projections_df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=projections_df['month'],
        y=projections_df['cumulative_savings'],
        mode='lines+markers',
        name='Savings',
        line=dict(color=CHART_COLORS['primary'], width=3),
        marker=dict(size=6),
        hovertemplate='Month %{x}<br>Savings: ' + CURRENCY + ' %{y:,.0f}<extra></extra>'
    ))
    
    fig.add_hline(
        y=target,
        line_dash="dash",
        line_color=CHART_COLORS['success'],
        annotation_text=f"Target: {CURRENCY} {target:,.0f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title=f"Savings ({CURRENCY})",
        height=400,
        showlegend=False
    )
    
    return fig

def create_surplus_bar_chart(projections_df, title="Monthly Surplus"):
    if projections_df.empty:
        return go.Figure()
    
    colors = [CHART_COLORS['success'] if s >= 0 else CHART_COLORS['danger'] 
              for s in projections_df['surplus']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=projections_df['month'],
        y=projections_df['surplus'],
        marker_color=colors,
        hovertemplate='Month %{x}<br>Surplus: ' + CURRENCY + ' %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title=f"Surplus ({CURRENCY})",
        height=350,
        showlegend=False
    )
    
    return fig

def create_income_expense_comparison(income_df, expenses_df, debts_df, target_date=None, title="Income vs Outflow"):
    from core.calculations import (
        calculate_total_monthly_income,
        calculate_total_monthly_expenses,
        calculate_total_monthly_debt
    )
    
    total_income = calculate_total_monthly_income(income_df, target_date)
    total_expenses = calculate_total_monthly_expenses(expenses_df)
    total_debt = calculate_total_monthly_debt(debts_df, target_date)
    
    categories = ['Income', 'Expenses', 'Debt Payments', 'Surplus']
    values = [total_income, total_expenses, total_debt, total_income - total_expenses - total_debt]
    colors = [CHART_COLORS['success'], CHART_COLORS['warning'], CHART_COLORS['danger'], CHART_COLORS['info']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f"{CURRENCY} {v:,.0f}" for v in values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' + CURRENCY + ' %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=f"Amount ({CURRENCY})",
        height=350,
        showlegend=False
    )
    
    return fig

def create_progress_gauge(current, target, title="Progress"):
    percentage = min((current / target) * 100, 100) if target > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': CHART_COLORS['primary']},
            'steps': [
                {'range': [0, 25], 'color': "#ffcccc"},
                {'range': [25, 50], 'color': "#ffe6cc"},
                {'range': [50, 75], 'color': "#ffffcc"},
                {'range': [75, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': CHART_COLORS['success'], 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        },
        number={'suffix': '%'}
    ))
    
    fig.update_layout(height=300)
    
    return fig

def create_health_gauge(avg_debt, avg_expenses, avg_income, title="Financial Health"):
    if avg_income <= 0:
        percentage = 100
        status = "No Income"
        color = "#ef4444"
    else:
        burden_ratio = ((avg_debt + avg_expenses) / avg_income) * 100
        percentage = min(burden_ratio, 100)
        
        if percentage <= 50:
            status = "Excellent"
            color = "#22c55e"
        elif percentage <= 75:
            status = "Good"
            color = "#3b82f6"
        elif percentage <= 90:
            status = "Warning"
            color = "#eab308"
        else:
            status = "Critical"
            color = "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "#ccffcc"},
                {'range': [50, 75], 'color': "#dbeafe"},
                {'range': [75, 90], 'color': "#ffffcc"},
                {'range': [90, 100], 'color': "#ffcccc"}
            ],
            'threshold': {
                'line': {'color': CHART_COLORS['success'], 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        },
        number={'suffix': '%'}
    ))
    
    fig.update_layout(height=300)
    
    return fig, status
