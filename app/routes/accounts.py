from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from decimal import Decimal

from app import db
from app.forms.account import AccountForm, AccountEditForm, AccountDeleteForm
from app.models.account import Account
from app.models.transaction import Transaction
from datetime import datetime, timedelta

accounts = Blueprint('accounts', __name__)


@accounts.route('/')
@login_required
def index():
    """List all accounts"""
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(float(account.balance) for account in user_accounts)

    # Get account statistics
    account_stats = {}
    max_transactions = 0  # Initialize max_transactions

    for account in user_accounts:
        # Get monthly transaction totals
        start_date = datetime.utcnow() - timedelta(days=30)
        transactions = Transaction.query.filter_by(
            account_id=account.id,
            user_id=current_user.id
        ).filter(
            Transaction.date >= start_date
        ).all()

        transaction_count = len(transactions)
        max_transactions = max(max_transactions, transaction_count)  # Update max_transactions

        income = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
        expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')

        account_stats[account.id] = {
            'monthly_income': income,
            'monthly_expenses': expenses,
            'transaction_count': transaction_count
        }

    return render_template('accounts/list.html',
                           accounts=user_accounts,
                           total_balance=total_balance,
                           account_stats=account_stats,
                           max_transactions=max_transactions)  # Pass max_transactions to template


@accounts.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new account"""
    form = AccountForm()
    if request.method == 'POST' and form.validate():
        try:
            account = Account()
            account.name = form.name.data
            account.account_type = form.account_type.data
            account.currency = form.currency.data
            account.balance = Decimal(str(form.initial_balance.data))
            account.description = form.description.data
            account.user_id = current_user.id

            account.save()
            flash('Account created successfully!', 'success')

            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'redirect': url_for('accounts.index')
                })
            return redirect(url_for('accounts.index'))

        except Exception as e:
            print(f"Error creating account: {str(e)}")  # For debugging
            error_message = 'An error occurred while creating the account'

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 400

            flash(error_message, 'error')
            return redirect(url_for('accounts.create'))

    if form.errors:
        print(f"Form validation errors: {form.errors}")  # For debugging

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Please check the form for errors',
                'errors': form.errors
            }), 400

    return render_template('accounts/create.html', form=form)


@accounts.route('/<account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(account_id):
    """Edit an existing account"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    form = AccountEditForm(obj=account)
    form.current_balance.data = account.balance

    if request.method == 'POST' and form.validate():
        try:
            account.name = form.name.data
            account.account_type = form.account_type.data
            account.currency = form.currency.data
            account.description = form.description.data

            db.session.commit()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})

            flash('Account updated successfully!', 'success')
            return redirect(url_for('accounts.index'))

        except Exception as e:
            db.session.rollback()
            error_message = 'An error occurred while updating the account'

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 400

            flash(error_message, 'error')
            return redirect(url_for('accounts.edit', account_id=account_id))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and form.errors:
        return jsonify({
            'success': False,
            'message': 'Please correct the errors in the form',
            'errors': form.errors
        }), 400

    return render_template('accounts/edit.html', form=form, account=account)


@accounts.route('/<account_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(account_id):
    """Delete an account"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first_or_404()

    form = AccountDeleteForm()

    if request.method == 'POST' and form.validate():
        if account.balance == 0:
            try:
                # Delete all associated transactions first
                Transaction.query.filter_by(account_id=account.id).delete()
                db.session.delete(account)
                db.session.commit()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True})

                flash('Account deleted successfully!', 'success')
                return redirect(url_for('accounts.index'))

            except Exception as e:
                db.session.rollback()
                error_message = 'An error occurred while deleting the account'

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': error_message
                    }), 400

                flash(error_message, 'error')
                return redirect(url_for('accounts.delete', account_id=account_id))
        else:
            error_message = 'Cannot delete account with non-zero balance'

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': error_message
                }), 400

            flash(error_message, 'error')

    return render_template('accounts/delete.html', form=form, account=account)


@accounts.route('/<account_id>', methods=['GET'])
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


# Update this route definition in accounts.py
@accounts.route('/api/<account_id>/balance-history')  # Add '/api/' prefix
@login_required
def balance_history(account_id):
    """API endpoint for account balance history"""
    try:
        # Get days parameter from query string, default to 30
        days = int(request.args.get('days', 30))

        account = Account.query.filter_by(
            id=account_id,
            user_id=current_user.id
        ).first_or_404()

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        transactions = Transaction.query.filter(
            Transaction.account_id == account_id,
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.asc()).all()

        # Calculate daily balances
        daily_balances = []
        running_balance = float(account.balance)

        # Work backwards from current balance
        for transaction in reversed(transactions):
            if transaction.transaction_type == 'income':
                running_balance -= float(transaction.amount)
            else:
                running_balance += float(transaction.amount)

            daily_balances.append({
                'date': transaction.date.strftime('%Y-%m-%d'),
                'balance': round(running_balance, 2)
            })

        # Sort balances chronologically
        daily_balances.reverse()

        return jsonify({
            'success': True,
            'balances': daily_balances
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid days parameter'
        }), 400
    except Exception as e:
        print(f"Error in balance history: {str(e)}")  # For debugging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
