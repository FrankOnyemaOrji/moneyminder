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
    type_filter = request.args.get('type_filter', 'all')
    account_filter = request.args.get('account_filter', '')
    category_filter = request.args.get('category_filter', '')
    tag_filter = request.args.get('tag_filter', '')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    search = request.args.get('search', '')

    # Build transaction query
    query = Transaction.query.filter_by(user_id=current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if type_filter != 'all':
        query = query.filter(Transaction.transaction_type == type_filter)
    if account_filter:
        query = query.filter(Transaction.account_id == account_filter)
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
    if tag_filter:
        query = query.filter(Transaction.tag == tag_filter)
    if min_amount:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount:
        query = query.filter(Transaction.amount <= max_amount)
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))

    transactions = query.order_by(Transaction.date.desc()).all()

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    # Get category summary
    category_summary = Transaction.get_category_summary(
        current_user.id,
        start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
        end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
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

    if form.validate_on_submit():
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

    # If there are form errors, they will be displayed in the template
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

    if form.validate_on_submit():
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
    start_date = request.args.get('start_date',
                                  (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date',
                                datetime.utcnow().strftime('%Y-%m-%d'))

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Get category summary
    category_summary = Transaction.get_category_summary(current_user.id, start_date, end_date)

    # Get daily stats
    daily_stats = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        daily_stats[date_str] = {
            'income': 0,
            'expense': 0,
            'net': 0
        }
        current_date += timedelta(days=1)

    transactions = Transaction.get_by_date_range(current_user.id, start_date, end_date)
    for transaction in transactions:
        date_str = transaction.date.strftime('%Y-%m-%d')
        if transaction.transaction_type == 'income':
            daily_stats[date_str]['income'] += float(transaction.amount)
        else:
            daily_stats[date_str]['expense'] += float(transaction.amount)
        daily_stats[date_str]['net'] = (
                daily_stats[date_str]['income'] - daily_stats[date_str]['expense']
        )

    # Account breakdown
    account_stats = {}
    for transaction in transactions:
        account_name = transaction.account.name
        if account_name not in account_stats:
            account_stats[account_name] = {
                'income': 0,
                'expense': 0,
                'transaction_count': 0
            }
        account_stats[account_name][transaction.transaction_type] += float(transaction.amount)
        account_stats[account_name]['transaction_count'] += 1

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    return jsonify({
        'category_summary': category_summary,
        'daily_stats': daily_stats,
        'account_stats': account_stats,
        'summary': {
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_amount': float(total_income - total_expenses),
            'transaction_count': len(transactions)
        }
    })


@transactions.route('/import', methods=['GET', 'POST'])
@login_required
def import_transactions():
    """Import transactions from CSV"""
    form = BulkTransactionForm(current_user)

    if form.validate_on_submit():
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
