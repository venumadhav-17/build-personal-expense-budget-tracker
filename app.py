"""
app.py
------
Flask application entry point for the Personal Expense & Budget Tracker.

Routes are grouped into:
  - Dashboard            (/)
  - Expenses CRUD         (/expenses, /expenses/add, /expenses/<id>/edit, /expenses/<id>/delete)
  - Budgets CRUD          (/budgets, /budgets/add, /budgets/<id>/edit, /budgets/<id>/delete)
  - Summary / reports     (/summary)
  - JSON API              (/api/summary)
"""

from collections import defaultdict
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from models import (
    Expense, Budget, EXPENSE_CATEGORIES, PAYMENT_METHODS,
    BUDGET_CATEGORIES, BUDGET_SCOPE_OVERALL,
)
from repository import JSONRepository, RecordNotFoundError

app = Flask(__name__)
app.secret_key = "expense-budget-tracker-secret-key-2026"

expense_repo = JSONRepository("data/expenses.json")
budget_repo = JSONRepository("data/budgets.json")


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def current_month():
    return datetime.now().strftime("%Y-%m")


def month_of(date_str):
    return date_str[:7]


def compute_month_summary(month):
    """Return totals & category breakdown for a given YYYY-MM month,
    plus budget utilisation for that month."""
    expenses = [e for e in expense_repo.all() if month_of(e["date"]) == month]
    budgets = [b for b in budget_repo.all() if b["month"] == month]

    total_spent = round(sum(e["amount"] for e in expenses), 2)

    by_category = defaultdict(float)
    for e in expenses:
        by_category[e["category"]] += e["amount"]
    by_category = {k: round(v, 2) for k, v in by_category.items()}

    budget_map = {b["category"]: b["limit_amount"] for b in budgets}
    overall_limit = budget_map.get(BUDGET_SCOPE_OVERALL)

    category_progress = []
    for cat in EXPENSE_CATEGORIES:
        spent = by_category.get(cat, 0.0)
        limit = budget_map.get(cat)
        pct = round((spent / limit) * 100, 1) if limit else None
        category_progress.append({
            "category": cat,
            "spent": round(spent, 2),
            "limit": limit,
            "pct": pct,
            "over": bool(limit and spent > limit),
        })

    overall_pct = round((total_spent / overall_limit) * 100, 1) if overall_limit else None

    return {
        "month": month,
        "total_spent": total_spent,
        "by_category": by_category,
        "category_progress": category_progress,
        "overall_limit": overall_limit,
        "overall_pct": overall_pct,
        "overall_over": bool(overall_limit and total_spent > overall_limit),
        "expense_count": len(expenses),
    }


# ----------------------------------------------------------------------
# dashboard
# ----------------------------------------------------------------------
@app.route("/")
def dashboard():
    month = request.args.get("month", current_month())
    summary = compute_month_summary(month)
    recent = sorted(expense_repo.all(), key=lambda e: (e["date"], e["id"]), reverse=True)[:6]
    all_months = sorted({month_of(e["date"]) for e in expense_repo.all()} | {current_month()}, reverse=True)
    return render_template(
        "dashboard.html",
        summary=summary,
        recent=recent,
        all_months=all_months,
        selected_month=month,
        total_expenses=expense_repo.count(),
        total_budgets=budget_repo.count(),
    )


# ----------------------------------------------------------------------
# expenses
# ----------------------------------------------------------------------
@app.route("/expenses")
def list_expenses():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    payment_method = request.args.get("payment_method", "")

    records = expense_repo.all()

    if query:
        records = [r for r in records if query in r.get("description", "").lower()]
    if category:
        records = [r for r in records if r.get("category") == category]
    if month:
        records = [r for r in records if month_of(r.get("date", "")) == month]
    if payment_method:
        records = [r for r in records if r.get("payment_method") == payment_method]

    records.sort(key=lambda e: (e["date"], e["id"]), reverse=True)
    total = round(sum(r["amount"] for r in records), 2)

    all_months = sorted({month_of(e["date"]) for e in expense_repo.all()}, reverse=True)

    return render_template(
        "expenses.html",
        expenses=records,
        total=total,
        categories=EXPENSE_CATEGORIES,
        payment_methods=PAYMENT_METHODS,
        all_months=all_months,
        filters={"q": query, "category": category, "month": month, "payment_method": payment_method},
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        form = request.form
        try:
            expense = Expense(
                date=form.get("date"),
                category=form.get("category"),
                amount=form.get("amount"),
                description=form.get("description"),
                payment_method=form.get("payment_method"),
            ).validate()
            expense_repo.add(expense.to_dict())
            flash("Expense added successfully.", "success")
            return redirect(url_for("list_expenses"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("add_expense.html", categories=EXPENSE_CATEGORIES,
                                    payment_methods=PAYMENT_METHODS, form=form)

    return render_template("add_expense.html", categories=EXPENSE_CATEGORIES,
                            payment_methods=PAYMENT_METHODS, form={})


@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):
    try:
        existing = expense_repo.get_or_raise(expense_id)
    except RecordNotFoundError:
        flash("Expense not found.", "error")
        return redirect(url_for("list_expenses"))

    if request.method == "POST":
        form = request.form
        try:
            expense = Expense(
                date=form.get("date"),
                category=form.get("category"),
                amount=form.get("amount"),
                description=form.get("description"),
                payment_method=form.get("payment_method"),
                record_id=expense_id,
                created_at=existing.get("created_at"),
            ).validate()
            updates = expense.to_dict()
            updates.pop("id", None)
            expense_repo.update(expense_id, updates)
            flash("Expense updated successfully.", "success")
            return redirect(url_for("list_expenses"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("edit_expense.html", expense={**existing, **form},
                                    categories=EXPENSE_CATEGORIES, payment_methods=PAYMENT_METHODS)

    return render_template("edit_expense.html", expense=existing,
                            categories=EXPENSE_CATEGORIES, payment_methods=PAYMENT_METHODS)


@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    try:
        expense_repo.delete(expense_id)
        flash("Expense deleted.", "success")
    except RecordNotFoundError:
        flash("Expense not found.", "error")
    return redirect(url_for("list_expenses"))


# ----------------------------------------------------------------------
# budgets
# ----------------------------------------------------------------------
@app.route("/budgets")
def list_budgets():
    records = sorted(budget_repo.all(), key=lambda b: (b["month"], b["category"]), reverse=True)
    return render_template("budgets.html", budgets=records, categories=BUDGET_CATEGORIES)


@app.route("/budgets/add", methods=["GET", "POST"])
def add_budget():
    if request.method == "POST":
        form = request.form
        try:
            budget = Budget(
                month=form.get("month"),
                category=form.get("category"),
                limit_amount=form.get("limit_amount"),
            ).validate()

            existing_dupe = next(
                (b for b in budget_repo.all()
                 if b["month"] == budget.month and b["category"] == budget.category), None
            )
            if existing_dupe:
                raise ValueError(
                    f"A budget for {budget.category} in {budget.month} already exists. "
                    "Edit that budget instead."
                )

            budget_repo.add(budget.to_dict())
            flash("Budget set successfully.", "success")
            return redirect(url_for("list_budgets"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("add_budget.html", categories=BUDGET_CATEGORIES, form=form)

    return render_template("add_budget.html", categories=BUDGET_CATEGORIES,
                            form={"month": current_month()})


@app.route("/budgets/<int:budget_id>/edit", methods=["GET", "POST"])
def edit_budget(budget_id):
    try:
        existing = budget_repo.get_or_raise(budget_id)
    except RecordNotFoundError:
        flash("Budget not found.", "error")
        return redirect(url_for("list_budgets"))

    if request.method == "POST":
        form = request.form
        try:
            budget = Budget(
                month=form.get("month"),
                category=form.get("category"),
                limit_amount=form.get("limit_amount"),
                record_id=budget_id,
                created_at=existing.get("created_at"),
            ).validate()
            updates = budget.to_dict()
            updates.pop("id", None)
            budget_repo.update(budget_id, updates)
            flash("Budget updated successfully.", "success")
            return redirect(url_for("list_budgets"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("edit_budget.html", budget={**existing, **form},
                                    categories=BUDGET_CATEGORIES)

    return render_template("edit_budget.html", budget=existing, categories=BUDGET_CATEGORIES)


@app.route("/budgets/<int:budget_id>/delete", methods=["POST"])
def delete_budget(budget_id):
    try:
        budget_repo.delete(budget_id)
        flash("Budget deleted.", "success")
    except RecordNotFoundError:
        flash("Budget not found.", "error")
    return redirect(url_for("list_budgets"))


# ----------------------------------------------------------------------
# summary / reports
# ----------------------------------------------------------------------
@app.route("/summary")
def summary():
    month = request.args.get("month", current_month())
    data = compute_month_summary(month)
    all_months = sorted({month_of(e["date"]) for e in expense_repo.all()} | {current_month()}, reverse=True)

    trend = []
    for m in sorted({month_of(e["date"]) for e in expense_repo.all()} | {current_month()})[-6:]:
        trend.append({"month": m, "total": compute_month_summary(m)["total_spent"]})

    return render_template("summary.html", summary=data, all_months=all_months,
                            selected_month=month, trend=trend)


@app.route("/api/summary")
def api_summary():
    month = request.args.get("month", current_month())
    return jsonify(compute_month_summary(month))


# ----------------------------------------------------------------------
# error handling
# ----------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
