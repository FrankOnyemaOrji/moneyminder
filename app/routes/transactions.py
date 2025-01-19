from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import csv
import io

from app import db
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.forms.transaction import TransactionForm, TransactionFilterForm, BulkTransactionForm

transactions = Blueprint('transactions', __name__)


def get_complete_category_summary(user_id, start_date=None, end_date=None):
    """Get summary for all categories, including those with zero transactions"""
    # Get all preset categories
    all_categories = Category.PRESET_CATEGORIES.keys()

    # Initialize summary with zero values for all categories
    summary = {category: {
        'income': 0.0,
        'expense': 0.0,
        'transaction_count': 0
    } for category in all_categories}

    # Build query
    query = Transaction.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Update summary with actual transaction data
    for transaction in query.all():
        if transaction.category in summary:
            summary[transaction.category][transaction.transaction_type] += float(transaction.amount)
            summary[transaction.category]['transaction_count'] += 1

    return summary


@transactions.route('/')
@login_required
def index():
    """List all transactions with filtering"""
    form = TransactionFilterForm(current_user)

    # Get filter parameters
    start_date = request.args.get('start_date',
                                  (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date',
                                datetime.utcnow().strftime('%Y-%m-%d'))

    # Convert dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

    # Build transaction query
    query = Transaction.query.filter_by(user_id=current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Apply additional filters
    type_filter = request.args.get('type_filter', 'all')
    if type_filter != 'all':
        query = query.filter(Transaction.transaction_type == type_filter)

    account_filter = request.args.get('account_filter')
    if account_filter:
        query = query.filter(Transaction.account_id == account_filter)

    category_filter = request.args.get('category_filter')
    if category_filter:
        query = query.filter(Transaction.category == category_filter)

    tag_filter = request.args.get('tag_filter')
    if tag_filter:
        query = query.filter(Transaction.tag == tag_filter)

    min_amount = request.args.get('min_amount', type=float)
    if min_amount:
        query = query.filter(Transaction.amount >= min_amount)

    max_amount = request.args.get('max_amount', type=float)
    if max_amount:
        query = query.filter(Transaction.amount <= max_amount)

    search = request.args.get('search', '')
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))

    # Execute query
    transactions = query.order_by(Transaction.date.desc()).all()

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    # Get complete category summary including zero-value categories
    category_summary = get_complete_category_summary(
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )

    return render_template('transactions/list.html',
                           transactions=transactions,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           categories=Category.PRESET_CATEGORIES,
                           category_tags=Category.CATEGORY_TAGS,
                           category_summary=category_summary,
                           form=form)


@transactions.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new transaction"""
    form = TransactionForm(current_user)

    # Update tag choices if category is in query params
    category = request.args.get('category')
    if category:
        form.update_tag_choices(category)

    if request.method == 'POST' and form.validate():
        try:
            # Update tag choices before validation
            form.update_tag_choices(form.category.data)

            # Verify account exists
            account = Account.query.get(form.account_id.data)
            if not account:
                flash(f"Account not found", 'error')
                return render_template('transactions/create.html',
                                       form=form,
                                       categories=Category.PRESET_CATEGORIES,
                                       category_tags=Category.CATEGORY_TAGS)

            # Create transaction instance
            transaction = Transaction(
                amount=form.amount.data,
                transaction_type=form.transaction_type.data,
                description=form.description.data,
                date=form.date.data,
                account_id=form.account_id.data,
                category=form.category.data,
                tag=form.tag.data,
                user_id=current_user.id
            )

            # Try to save the transaction
            if transaction.save():
                flash('Transaction created successfully!', 'success')
                return redirect(url_for('transactions.index'))

            flash('Failed to save transaction', 'error')

        except Exception as e:
            db.session.rollback()
            flash('Error creating transaction', 'error')

    return render_template('transactions/create.html',
                           form=form,
                           categories=Category.PRESET_CATEGORIES,
                           category_tags=Category.CATEGORY_TAGS)


@transactions.route('/<transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    """Edit an existing transaction"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    form = TransactionForm(current_user, obj=transaction)

    if request.method == 'POST' and form.validate():
        try:
            transaction.amount = form.amount.data
            transaction.transaction_type = form.transaction_type.data
            transaction.description = form.description.data
            transaction.date = form.date.data
            transaction.account_id = form.account_id.data
            transaction.category = form.category.data
            transaction.tag = form.tag.data

            transaction.save()
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('transactions.index'))

        except Exception as e:
            flash('Error updating transaction: ' + str(e), 'error')
            return redirect(url_for('transactions.edit', transaction_id=transaction_id))

    return render_template('transactions/edit.html',
                           form=form,
                           transaction=transaction,
                           categories=Category.PRESET_CATEGORIES,
                           category_tags=Category.CATEGORY_TAGS)


@transactions.route('/<transaction_id>/delete', methods=['POST'])
@login_required
def delete(transaction_id):
    """Delete a transaction"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    try:
        transaction.delete()
        flash('Transaction deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting transaction: ' + str(e), 'error')

    return redirect(url_for('transactions.index'))


@transactions.route('/api/categories/<category>/tags')
@login_required
def get_category_tags(category):
    """API endpoint to get tags for a category"""
    tags = Category.CATEGORY_TAGS.get(category, {}).get('Subcategories', [])
    return jsonify(tags)


@transactions.route('/api/transactions/stats')
@login_required
def transaction_stats():
    """API endpoint for transaction statistics"""
    try:
        # Parse date parameters
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get daily stats
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_stats[date_str] = {
                'income': 0.0,
                'expense': 0.0,
                'net': 0.0
            }
            current_date += timedelta(days=1)

        # Query transactions for the period
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date.between(start_date, end_date)
        ).all()

        # Update daily stats
        for transaction in transactions:
            date_str = transaction.date.strftime('%Y-%m-%d')
            amount = float(transaction.amount)

            if transaction.transaction_type == 'income':
                daily_stats[date_str]['income'] += amount
            else:
                daily_stats[date_str]['expense'] += amount

            daily_stats[date_str]['net'] = (
                    daily_stats[date_str]['income'] - daily_stats[date_str]['expense']
            )

        # Calculate totals
        total_income = sum(stat['income'] for stat in daily_stats.values())
        total_expenses = sum(stat['expense'] for stat in daily_stats.values())

        return jsonify({
            'daily_stats': daily_stats,
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_amount': float(total_income - total_expenses),
                'transaction_count': len(transactions)
            }
        })
    except Exception as e:
        print('Error in transaction_stats:', str(e))  # Add debug print
        return jsonify({'error': str(e)}), 500


@transactions.route('/import', methods=['GET', 'POST'])
@login_required
def import_transactions():
    """Import transactions from CSV"""
    form = BulkTransactionForm(current_user)

    if request.method == 'POST' and form.validate():
        try:
            file = form.file.data
            account = Account.get_by_id(form.account_id.data)

            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream) if form.has_headers.data else csv.reader(stream)

            transaction_count = 0
            error_count = 0

            for row in csv_reader:
                try:
                    if form.has_headers.data:
                        transaction = Transaction(
                            amount=float(row['amount']),
                            transaction_type=row['type'],
                            description=row['description'],
                            date=datetime.strptime(row['date'], '%Y-%m-%d'),
                            account_id=account.id,
                            category=row['category'],
                            tag=row['tag'],
                            user_id=current_user.id
                        )
                    else:
                        transaction = Transaction(
                            amount=float(row[0]),
                            transaction_type=row[1],
                            description=row[2],
                            date=datetime.strptime(row[3], '%Y-%m-%d'),
                            account_id=account.id,
                            category=row[4],
                            tag=row[5],
                            user_id=current_user.id
                        )

                    transaction.save()
                    transaction_count += 1

                except Exception as e:
                    error_count += 1
                    continue

            flash(f'Imported {transaction_count} transactions successfully. {error_count} errors.', 'success')
            return redirect(url_for('transactions.index'))

        except Exception as e:
            flash('Error importing transactions: ' + str(e), 'error')

    return render_template('transactions/import.html', form=form)
