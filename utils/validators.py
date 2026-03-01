from datetime import datetime
from dateutil.relativedelta import relativedelta

def validate_required_fields(data: dict, required_fields: list) -> tuple:
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)
    
    return len(missing) == 0, missing

def validate_positive_number(value, field_name: str) -> tuple:
    if value is None or value < 0:
        return False, f"{field_name} must be a positive number"
    return True, ""

def validate_date(date_str: str) -> tuple:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_pin_format(pin: str) -> tuple:
    if not pin:
        return False, "PIN is required"
    if not pin.isdigit():
        return False, "PIN must contain only digits"
    if len(pin) != 4:
        return False, "PIN must be exactly 4 digits"
    return True, ""

def validate_debt_data(data: dict) -> tuple:
    required = ["name", "balance", "monthly_payment"]
    is_valid, missing = validate_required_fields(data, required)
    
    if not is_valid:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    is_valid, msg = validate_positive_number(data.get("balance"), "Balance")
    if not is_valid:
        return False, msg
    
    is_valid, msg = validate_positive_number(data.get("monthly_payment"), "Monthly Payment")
    if not is_valid:
        return False, msg
    
    if data.get("interest_rate"):
        is_valid, msg = validate_positive_number(data.get("interest_rate"), "Interest Rate")
        if not is_valid:
            return False, msg
    
    return True, "Valid"

def validate_expense_data(data: dict) -> tuple:
    required = ["category", "amount"]
    is_valid, missing = validate_required_fields(data, required)
    
    if not is_valid:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    is_valid, msg = validate_positive_number(data.get("amount"), "Amount")
    if not is_valid:
        return False, msg
    
    return True, "Valid"

def validate_income_data(data: dict) -> tuple:
    required = ["source", "amount"]
    is_valid, missing = validate_required_fields(data, required)
    
    if not is_valid:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    is_valid, msg = validate_positive_number(data.get("amount"), "Amount")
    if not is_valid:
        return False, msg
    
    return True, "Valid"

def sanitize_string(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip()

def sanitize_number(value) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
