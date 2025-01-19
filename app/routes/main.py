from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.budget import Budget
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


def get_time_based_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


@main.route('/')
@main.route('/index')
@main.route('/dashboard')
@login_required
def index():
    # Get account summaries
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(float(account.balance) for account in accounts)

    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Transaction.date.desc()
    ).limit(5).all()

    # Get current month's income and expenses
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

    month_transactions = Transaction.get_by_date_range(
        current_user.id,
        start_of_month,
        end_of_month
    )

    total_income = sum(
        float(t.amount) for t in month_transactions
        if t.transaction_type == 'income'
    )
    total_expenses = sum(
        float(t.amount) for t in month_transactions
        if t.transaction_type == 'expense'
    )

    # Get active budgets and their status
    active_budgets = Budget.get_active_budgets(current_user.id)
    budget_status = [
        {
            'category': budget.category,
            'amount': float(budget.amount),
            'spent': float(budget.get_spent_amount()),
            'remaining': float(budget.get_remaining_amount()),
            'percentage': float(budget.get_spending_percentage()),
            'is_exceeded': budget.is_exceeded()
        }
        for budget in active_budgets
    ]

    # Calculate total monthly budget and spending
    total_budget = sum(float(budget.amount) for budget in active_budgets)
    total_spent = sum(float(budget.get_spent_amount()) for budget in active_budgets)

    # Get the time-based greeting
    greeting = get_time_based_greeting()

    return render_template('dashboard/index.html',
                           greeting=greeting,
                           accounts=accounts,
                           total_balance=total_balance,
                           recent_transactions=recent_transactions,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           budget_status=budget_status,
                           total_budget=total_budget,
                           total_spent=total_spent)
