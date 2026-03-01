import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from config import PAGE_CONFIG, APP_NAME
import auth

st.set_page_config(**PAGE_CONFIG)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_settings" not in st.session_state:
    st.session_state.user_settings = {}
if "creating_profile" not in st.session_state:
    st.session_state.creating_profile = False

if st.session_state.creating_profile:
    auth.create_profile_screen()
elif not st.session_state.authenticated:
    auth.login_screen()
else:
    st.sidebar.markdown(f"### 👤 {st.session_state.current_user}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        auth.logout()
    
    # Main Content
    st.title("⛵ Navis")
    st.markdown("### Welcome back!")
    st.markdown("Use the sidebar to navigate to different sections.")
    
    st.markdown("---")
    
    from utils.file_handler import get_debts, get_expenses, get_income, get_payment_records, add_payment_record, get_payment_record_by_source_and_month
    from core.calculations import (
        calculate_total_debt_balance,
        calculate_avg_monthly_debt,
        calculate_avg_monthly_expenses,
        calculate_avg_monthly_income,
        calculate_avg_monthly_surplus,
        calculate_payment_points,
        calculate_savings_points,
        get_payment_points_milestone,
        get_savings_points_milestone,
        get_total_payment_points,
        get_total_savings_points
    )
    
    username = st.session_state.current_user
    debts_df = get_debts(username)
    expenses_df = get_expenses(username)
    income_df = get_income(username)
    payment_records_df = get_payment_records(username)
    settings = st.session_state.user_settings
    
    current_month = datetime.now().strftime('%Y-%m')
    
    total_debt = calculate_total_debt_balance(debts_df)
    avg_monthly_debt = calculate_avg_monthly_debt(debts_df, 12)
    avg_monthly_expenses = calculate_avg_monthly_expenses(expenses_df, 12)
    avg_monthly_income = calculate_avg_monthly_income(income_df, 12)
    avg_monthly_surplus = calculate_avg_monthly_surplus(income_df, expenses_df, debts_df, 12)
    emergency_target = settings.get('emergency_fund_target', 90000)
    
    # Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Debt", f"EGP {total_debt:,.0f}")
    
    with col2:
        st.metric("💸 Avg Monthly Debt", f"EGP {avg_monthly_debt:,.0f}")
    
    with col3:
        st.metric("💵 Avg Monthly Income", f"EGP {avg_monthly_income:,.0f}")
    
    with col4:
        delta_color = "normal" if avg_monthly_surplus >= 0 else "inverse"
        st.metric("📊 Avg Monthly Surplus", f"EGP {avg_monthly_surplus:,.0f}", delta_color=delta_color)
    
    st.markdown("---")
    
    # ===== PAYMENT POINTS DISPLAY =====
    payment_pts = get_total_payment_points(payment_records_df)
    savings_pts = get_total_savings_points(payment_records_df)
    
    payment_milestone = get_payment_points_milestone(payment_pts['total'])
    savings_milestone = get_savings_points_milestone(savings_pts['total'])
    
    col_pts1, col_pts2 = st.columns(2)
    
    with col_pts1:
        st.markdown("### ⏰ Payment Discipline")
        st.markdown(f"**{payment_milestone['title']}**")
        st.progress(payment_milestone['progress'] / 100)
        st.caption(f"{payment_pts['total']} points - Next: {payment_milestone['next_title']} at {payment_milestone['next_threshold']} pts")
    
    with col_pts2:
        st.markdown("### 💰 Savings Points")
        st.markdown(f"**{savings_milestone['title']}**")
        st.progress(savings_milestone['progress'] / 100)
        st.caption(f"{savings_pts['total']} points - Next: {savings_milestone['next_title']} at {savings_milestone['next_threshold']} pts")
    
    st.markdown("---")
    
    # ===== PAYMENT TRACKING SECTION =====
    st.subheader("💳 Payment Tracking")
    
    # Get user's upcoming days setting
    upcoming_days = settings.get('upcoming_days', 7)
    
    today = datetime.now().date()
    future_date = today + timedelta(days=upcoming_days)
    
    # Get all payments that have been paid (from any month) - track by (source_type, source_id, due_date)
    paid_payments = set()
    if not payment_records_df.empty:
        for _, record in payment_records_df.iterrows():
            due_date_str = record.get('due_date')
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    paid_payments.add((record['source_type'], record['source_id'], due_date))
                except:
                    pass
    
    # Build all payments list from debts and expenses with recurring dates
    all_payments = []
    
    freq_divisors = {
        'Monthly': 1,
        'Quarterly': 3,
        'Semester': 6,
        'One-time': None
    }
    
    if not debts_df.empty:
        active_debts = debts_df[debts_df['status'] == 'Active']
        for _, row in active_debts.iterrows():
            if not row.get('due_date'):
                continue
            
            try:
                start_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                end_str = row.get('end_date')
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None
                frequency = row.get('frequency', 'Monthly')
                divisor = freq_divisors.get(frequency)
                
                # Generate recurring due dates
                current_date = start_date
                while True:
                    if end_date and current_date > end_date:
                        break
                    
                    all_payments.append({
                        'id': row.get('id'),
                        'source_type': 'debt',
                        'name': row.get('name', 'Unknown'),
                        'amount': row.get('installment_amount', 0),
                        'due_date': current_date,
                        'type': '💰 Debt'
                    })
                    
                    if divisor is None:  # One-time
                        break
                    current_date = current_date + relativedelta(months=divisor)
            except:
                pass
    
    if not expenses_df.empty:
        for _, row in expenses_df.iterrows():
            if not row.get('due_date'):
                continue
            
            try:
                start_date = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                frequency = row.get('frequency', 'Monthly')
                divisor = freq_divisors.get(frequency)
                
                # Generate recurring due dates (expenses have no end_date, limit to 12 months)
                current_date = start_date
                for _ in range(12):
                    all_payments.append({
                        'id': row.get('id'),
                        'source_type': 'expense',
                        'name': row.get('category', 'Unknown'),
                        'amount': row.get('amount', 0),
                        'due_date': current_date,
                        'type': '💸 Expense'
                    })
                    
                    if divisor is None:  # One-time
                        break
                    current_date = current_date + relativedelta(months=divisor)
            except:
                pass
    
    # Categorize payments
    late_payments = []
    upcoming_payments = []
    
    for payment in all_payments:
        is_paid = (payment['source_type'], payment['id'], payment['due_date']) in paid_payments
        
        if payment['due_date'] < today and not is_paid:
            late_payments.append(payment)
        elif today <= payment['due_date'] <= future_date and not is_paid:
            upcoming_payments.append(payment)
    
    late_payments.sort(key=lambda x: x['due_date'])
    upcoming_payments.sort(key=lambda x: x['due_date'])
    
    # ===== PAID PAYMENTS =====
    # Filter to show only current month's payments
    current_month_str = today.strftime('%Y-%m')
    if not payment_records_df.empty:
        payment_records_df = payment_records_df.copy()
        payment_records_df['month_str'] = pd.to_datetime(payment_records_df['due_date'], errors='coerce').dt.strftime('%Y-%m')
        current_month_payments = payment_records_df[payment_records_df['month_str'] == current_month_str]
    else:
        current_month_payments = payment_records_df
    
    paid_count = len(current_month_payments) if not current_month_payments.empty else 0
    late_count = len(late_payments)
    upcoming_count = len(upcoming_payments)
    
    # Summary header
    if late_count > 0 or upcoming_count > 0:
        st.warning(f"🔴 {late_count} Late | 🟡 {upcoming_count} Upcoming | 🟢 {paid_count} Paid")
    else:
        st.info(f"🟢 {paid_count} Paid")
    
    # ===== LATE PAYMENTS =====
    with st.expander(f"🔴 Late Payments ({late_count})"):
        if late_payments:
            for payment in late_payments:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{payment['type']} {payment['name']}**")
                        st.caption(f"Due: {payment['due_date']} | Budgeted: EGP {payment['amount']:,.0f}")
                    with col2:
                        is_paid = st.checkbox("Mark as Paid", key=f"paid_late_{payment['source_type']}_{payment['id']}_{payment['due_date']}")
                    
                    if is_paid:
                        actual_amount = st.number_input(
                            "Actual Amount",
                            value=float(payment['amount']),
                            key=f"actual_late_{payment['source_type']}_{payment['id']}_{payment['due_date']}"
                        )
                        payment_date = st.date_input(
                            "Payment Date",
                            value=today,
                            key=f"date_late_{payment['source_type']}_{payment['id']}_{payment['due_date']}"
                        )
                        
                        if st.button("Submit", key=f"submit_late_{payment['source_type']}_{payment['id']}_{payment['due_date']}"):
                            payment_pts, _ = calculate_payment_points(
                                payment['amount'], 
                                actual_amount, 
                                payment['due_date'], 
                                payment_date
                            )
                            
                            if payment['source_type'] == 'expense':
                                savings_pts_calc = calculate_savings_points(payment['amount'], actual_amount)
                            else:
                                savings_pts_calc = 0
                            
                            record = {
                                'source_type': payment['source_type'],
                                'source_id': payment['id'],
                                'source_name': payment['name'],
                                'due_date': payment['due_date'].strftime('%Y-%m-%d'),
                                'payment_date': payment_date.strftime('%Y-%m-%d'),
                                'budgeted_amount': payment['amount'],
                                'actual_amount': actual_amount,
                                'month': current_month,
                                'payment_points': payment_pts,
                                'savings_points': savings_pts_calc,
                                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            add_payment_record(username, record)
                            st.rerun()
                    st.divider()
        else:
            st.success("✅ No late payments!")
    
    # ===== UPCOMING PAYMENTS =====
    with st.expander(f"🟡 Upcoming - Next {upcoming_days} Days ({upcoming_count})"):
        if upcoming_payments:
            for payment in upcoming_payments:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        days_until = (payment['due_date'] - today).days
                        st.markdown(f"**{payment['type']} {payment['name']}**")
                        st.caption(f"Due: {payment['due_date']} (in {days_until} days) | Budgeted: EGP {payment['amount']:,.0f}")
                    with col2:
                        is_paid = st.checkbox("Mark as Paid", key=f"paid_upcoming_{payment['source_type']}_{payment['id']}_{payment['due_date']}")
                    
                    if is_paid:
                        actual_amount = st.number_input(
                            "Actual Amount",
                            value=float(payment['amount']),
                            key=f"actual_upcoming_{payment['source_type']}_{payment['id']}_{payment['due_date']}"
                        )
                        payment_date = st.date_input(
                            "Payment Date",
                            value=payment['due_date'],
                            key=f"date_upcoming_{payment['source_type']}_{payment['id']}_{payment['due_date']}"
                        )
                        
                        if st.button("Submit", key=f"submit_upcoming_{payment['source_type']}_{payment['id']}_{payment['due_date']}"):
                            payment_pts, _ = calculate_payment_points(
                                payment['amount'], 
                                actual_amount, 
                                payment['due_date'], 
                                payment_date
                            )
                            
                            if payment['source_type'] == 'expense':
                                savings_pts_calc = calculate_savings_points(payment['amount'], actual_amount)
                            else:
                                savings_pts_calc = 0
                            
                            record = {
                                'source_type': payment['source_type'],
                                'source_id': payment['id'],
                                'source_name': payment['name'],
                                'due_date': payment['due_date'].strftime('%Y-%m-%d'),
                                'payment_date': payment_date.strftime('%Y-%m-%d'),
                                'budgeted_amount': payment['amount'],
                                'actual_amount': actual_amount,
                                'month': current_month,
                                'payment_points': payment_pts,
                                'savings_points': savings_pts_calc,
                                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            add_payment_record(username, record)
                            st.rerun()
                    st.divider()
        else:
            st.success(f"No upcoming payments in the next {upcoming_days} days!")
    
    # ===== PAID PAYMENTS =====
    with st.expander(f"🟢 Paid Payments ({paid_count})"):
        if not current_month_payments.empty:
            paid_sorted = current_month_payments.sort_values('created_at', ascending=False)
            for _, record in paid_sorted.iterrows():
                payment_date = record['payment_date']
                due_date = record['due_date']
                
                if isinstance(payment_date, str):
                    payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                
                if payment_date < due_date:
                    status_icon = "✅"
                    status_text = "Early"
                elif payment_date == due_date:
                    status_icon = "✅"
                    status_text = "On-time"
                else:
                    status_icon = "⚠️"
                    status_text = "Late"
                
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{status_icon} **{record['source_name']}** - {status_text}")
                        st.caption(f"Paid: EGP {record['actual_amount']:,.0f} on {record['payment_date']} | Due: {record['due_date']}")
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_paid_{record['id']}"):
                            st.session_state.editing_payment_id = record['id']
                            st.rerun()
                    
                    if 'editing_payment_id' in st.session_state and st.session_state.editing_payment_id == record['id']:
                        with st.form(key=f"edit_payment_form_{record['id']}"):
                            new_actual = st.number_input(
                                "Actual Amount Paid",
                                value=float(record['actual_amount']),
                                min_value=0.0,
                                step=100.0,
                                key=f"edit_amount_{record['id']}"
                            )
                            col_a, col_b = st.columns(2)
                            with col_a:
                                save_edit = st.form_submit_button("💾 Save", type="primary")
                            with col_b:
                                cancel_edit = st.form_submit_button("Cancel")
                            
                            if save_edit:
                                from utils.file_handler import update_payment_record
                                from core.calculations import calculate_savings_points
                                new_savings_pts = calculate_savings_points(record['budgeted_amount'], new_actual)
                                update_payment_record(username, record['id'], {
                                    'actual_amount': new_actual,
                                    'savings_points': new_savings_pts
                                })
                                st.success("Payment updated successfully!")
                                del st.session_state.editing_payment_id
                                st.rerun()
                            if cancel_edit:
                                del st.session_state.editing_payment_id
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No payments recorded yet!")
