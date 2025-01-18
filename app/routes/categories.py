from datetime import datetime

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.forms.category import CategoryForm
from app.models import Transaction
from app.models.category import Category

categories = Blueprint('categories', __name__)


@categories.route('/')
@login_required
def index():
    """List all categories"""
    root_categories = current_user.categories.filter_by(parent_id=None).all()
    return render_template('categories/index.html', categories=root_categories)


@categories.route('/create', methods=['POST'])
@login_required
def create():
    """Create a new category"""
    form = CategoryForm(current_user)

    if form.validate_on_submit():
        try:
            category = Category(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id,
                parent_id=form.parent_id.data if form.parent_id.data else None,
                icon=form.icon.data,
                color=form.color.data,
                is_active=form.is_active.data,
                is_budget_tracked=form.is_budget_tracked.data
            )

            db.session.add(category)
            db.session.commit()

            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'error', 'errors': form.errors}), 400


@categories.route('/<category_id>/edit', methods=['POST'])
@login_required
def edit(category_id):
    """Edit an existing category"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first_or_404()

    form = CategoryForm(current_user)

    if form.validate_on_submit():
        try:
            category.name = form.name.data
            category.description = form.description.data
            category.parent_id = form.parent_id.data if form.parent_id.data else None
            category.icon = form.icon.data
            category.color = form.color.data
            category.is_active = form.is_active.data
            category.is_budget_tracked = form.is_budget_tracked.data

            # Check for circular reference
            if category.parent_id and category.id == category.parent_id:
                raise ValueError('A category cannot be its own parent')

            # Check if new parent is not one of the category's children
            if category.parent_id:
                subcategories = category.get_all_subcategories()
                if any(sub.id == category.parent_id for sub in subcategories):
                    raise ValueError('Cannot set a subcategory as parent')

            db.session.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'error', 'errors': form.errors}), 400


@categories.route('/<category_id>/delete', methods=['POST'])
@login_required
def delete(category_id):
    """Delete a category"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first_or_404()

    # Check if category has transactions
    if category.transactions.count() > 0:
        return jsonify({
            'status': 'error',
            'message': 'Cannot delete category with existing transactions'
        }), 400

    try:
        # Move subcategories to parent category if exists
        for subcategory in category.subcategories:
            subcategory.parent_id = category.parent_id

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@categories.route('/api/categories/tree', methods=['GET'])
@login_required
def get_tree():
    """Get the full category tree structure"""
    def build_tree(categories, parent_id=None):
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                children = build_tree(categories, category.id)
                tree.append({
                    'id': category.id,
                    'name': category.name,
                    'icon': category.icon,
                    'color': category.color,
                    'is_active': category.is_active,
                    'is_budget_tracked': category.is_budget_tracked,
                    'children': children
                })
        return tree

    categories = Category.query.filter_by(user_id=current_user.id).all()
    tree = build_tree(categories)

    return jsonify(tree)


@categories.route('/api/categories/<category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """Get category details"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first_or_404()

    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'parent_id': category.parent_id,
        'icon': category.icon,
        'color': category.color,
        'is_active': category.is_active,
        'is_budget_tracked': category.is_budget_tracked
    })


@categories.route('/<category_id>', methods=['GET'])
@login_required
def view(category_id):
    """View a specific category and its transactions"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first_or_404()

    transactions = category.get_all_transactions()  # Include transactions from subcategories

    # Calculate category statistics
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')

    return render_template('categories/view.html',
                           category=category,
                           transactions=transactions,
                           total_income=total_income,
                           total_expenses=total_expenses)


@categories.route('/api/categories/stats', methods=['GET'])
@login_required
def get_stats():
    """Get category statistics"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Transaction.query.filter_by(user_id=current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))

    transactions = query.all()

    # Calculate statistics for each category
    stats = {}
    for category in current_user.categories:
        category_transactions = [t for t in transactions if t.category_id == category.id]
        stats[category.id] = {
            'name': category.name,
            'income': sum(t.amount for t in category_transactions if t.transaction_type == 'income'),
            'expenses': sum(t.amount for t in category_transactions if t.transaction_type == 'expense'),
            'transaction_count': len(category_transactions)
        }

    return jsonify(stats)
