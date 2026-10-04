"""
models.py
---------
Domain model classes for the Personal Expense & Budget Tracker.

Each class encapsulates:
  - field definitions
  - validate() -> raises ValueError with a human readable message
  - to_dict() -> plain dict ready for JSON storage

Categories are a fixed closed list (per the project brief) so that
category-wise summaries and budgets line up correctly.
"""

from datetime import datetime

EXPENSE_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Education", "Other",
]

PAYMENT_METHODS = [
    "Cash", "Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet",
]

BUDGET_SCOPE_OVERALL = "Overall"
BUDGET_CATEGORIES = [BUDGET_SCOPE_OVERALL] + EXPENSE_CATEGORIES


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _require(value, field_name):
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{field_name} is required")
    return value.strip() if isinstance(value, str) else value


def _require_choice(value, choices, field_name):
    value = _require(value, field_name)
    if value not in choices:
        raise ValueError(f"{field_name} must be one of: {', '.join(choices)}")
    return value


def _require_positive_number(value, field_name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number")
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero")
    return round(number, 2)


def _require_date(value, field_name):
    value = _require(value, field_name)
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{field_name} must be a valid date (YYYY-MM-DD)")
    return value


def _require_month(value, field_name):
    value = _require(value, field_name)
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError:
        raise ValueError(f"{field_name} must be a valid month (YYYY-MM)")
    return value


class Expense:
    def __init__(self, date, category, amount, description="",
                 payment_method="Cash", record_id=None, created_at=None):
        self.id = record_id
        self.date = date
        self.category = category
        self.amount = amount
        self.description = description or ""
        self.payment_method = payment_method or "Cash"
        self.created_at = created_at or now_iso()

    def validate(self):
        self.date = _require_date(self.date, "Date")
        self.category = _require_choice(self.category, EXPENSE_CATEGORIES, "Category")
        self.amount = _require_positive_number(self.amount, "Amount")
        self.payment_method = _require_choice(self.payment_method, PAYMENT_METHODS, "Payment method")
        if self.description and len(self.description) > 200:
            raise ValueError("Description must be 200 characters or fewer")
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "payment_method": self.payment_method,
            "created_at": self.created_at,
        }


class Budget:
    def __init__(self, month, category, limit_amount, record_id=None, created_at=None):
        self.id = record_id
        self.month = month
        self.category = category
        self.limit_amount = limit_amount
        self.created_at = created_at or now_iso()

    def validate(self):
        self.month = _require_month(self.month, "Month")
        self.category = _require_choice(self.category, BUDGET_CATEGORIES, "Category")
        self.limit_amount = _require_positive_number(self.limit_amount, "Limit amount")
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.month,
            "category": self.category,
            "limit_amount": self.limit_amount,
            "created_at": self.created_at,
        }
