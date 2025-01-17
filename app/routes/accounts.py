from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from decimal import Decimal
from app.forms.account import AccountForm, AccountEditForm, AccountDeleteForm
from app.models.account import Account
from app.models.transaction import Transaction
from datetime import datetime, timedelta

accounts = Blueprint('accounts', __name__)


@accounts.route('/accounts')
@login_required
def index():
    """List all accounts"""
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(float(account.balance) for account in user_accounts)

    # Get account statistics
    account_stats = {}
    for account in user_accounts:
        # Get monthly transaction totals
        start_date = datetime.utcnow() - timedelta(days=30)
        transactions = Transaction.query.filter_by(
            account_id=account.id,
            user_id=current_user.id
        ).filter(
            Transaction.date >= start_date
        ).all()

        income = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
        expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')

        account_stats[account.id] = {
            'monthly_income': income,
            'monthly_expenses': expenses,
            'transaction_count': len(transactions)
        }

    return render_template('accounts/list.html',
                           accounts=user_accounts,
                           total_balance=total_balance,
                           account_stats=account_stats)


@accounts.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new account"""
    form = AccountForm()
    if form.validate_on_submit():
        account = Account()
        account.name = form.name.data
        account.account_type = form.account_type.data
        account.currency = form.currency.data
        account.balance = Decimal(str(form.initial_balance.data))
        account.description = form.description.data
        account.user_id = current_user.id

        try:
            account.save()
            flash('Account created successfully!', 'success')
            return redirect(url_for('accounts.index'))
        except Exception as e:
            flash('An error occurred while creating the account.', 'error')
            return redirect(url_for('accounts.create'))

    return render_template('accounts/create.html', form=form)


@accounts.route('/accounts/<account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(account_id):
    """Edit an existing account"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    form = AccountEditForm(obj=account)
    form.current_balance.data = account.balance

    if form.validate_on_submit():
        account.name = form.name.data
        account.account_type = form.account_type.data
        account.currency = form.currency.data
        account.description = form.description.data

        try:
            account.update()
            flash('Account updated successfully!', 'success')
            return redirect(url_for('accounts.index'))
        except Exception as e:
            flash('An error occurred while updating the account.', 'error')
            return redirect(url_for('accounts.edit', account_id=account_id))

    return render_template('accounts/edit.html', form=form, account=account)


@accounts.route('/accounts/<account_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(account_id):
    """Delete an account"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    form = AccountDeleteForm()

    if form.validate_on_submit():
        try:
            account.delete()
            flash('Account deleted successfully!', 'success')
            return redirect(url_for('accounts.index'))
        except Exception as e:
            flash('An error occurred while deleting the account.', 'error')
            return redirect(url_for('accounts.delete', account_id=account_id))

    return render_template('accounts/delete.html',
                           form=form,
                           account=account)


@accounts.route('/accounts/<account_id>')
@login_required
def view(account_id):
    """View account details and transaction history"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    # Get date range from query parameters or default to last 30 days
    end_date = datetime.utcnow()
    start_date = request.args.get('start_date',
                                  (end_date - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', end_date.strftime('%Y-%m-%d'))

    # Convert string dates to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Get transactions for the date range
    transactions = Transaction.query.filter(
        Transaction.account_id == account_id,
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date.desc()).all()

    # Calculate statistics
    total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')

    return render_template('accounts/view.html',
                           account=account,
                           transactions=transactions,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           start_date=start_date,
                           end_date=end_date)


@accounts.route('/api/accounts/<account_id>/balance-history')
@login_required
def balance_history(account_id):
    """API endpoint for account balance history"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    # Get transactions for the last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    transactions = Transaction.query.filter(
        Transaction.account_id == account_id,
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date.asc()).all()

    # Calculate daily balances
    daily_balances = []
    current_balance = float(account.balance)
    current_date = end_date

    for transaction in reversed(transactions):
        while current_date.date() > transaction.date.date():
            daily_balances.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'balance': round(current_balance, 2)
            })
            current_date = current_date - timedelta(days=1)

        if transaction.transaction_type == 'income':
            current_balance -= float(transaction.amount)
        else:
            current_balance += float(transaction.amount)

    # Fill in remaining days
    while current_date.date() >= start_date.date():
        daily_balances.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'balance': round(current_balance, 2)
        })
        current_date = current_date - timedelta(days=1)

    return {'balances': daily_balances}
