import os

APP_NAME = "Navis"
APP_VERSION = "1.0.0"
CURRENCY = "EGP"
CURRENCY_SYMBOL = "EGP"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DIR = os.path.join(BASE_DIR, "users")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DEFAULT_EMERGENCY_FUND_TARGET = 90000
DEFAULT_UPCOMING_DAYS = 7

PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "⛵",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

EXPENSE_CATEGORIES = [
    "Rent",
    "Utilities",
    "Infant Needs",
    "Groceries",
    "Transportation",
    "Entertainment",
    "Clothing",
    "Medical",
    "Children Activities",
    "Subscriptions",
    "Other"
]

INCOME_FREQUENCIES = ["Monthly", "Quarterly", "Semester", "Yearly", "One-time"]
DEBT_FREQUENCIES = ["Monthly", "Quarterly", "Semester", "Yearly"]
DEBT_STATUSES = ["Active", "Settled", "Defaulted"]
DEBT_PRIORITIES = ["High", "Medium", "Low"]

CHART_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ffbb33",
    "info": "#17a2b8"
}
