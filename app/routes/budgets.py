from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.forms.budget import BudgetForm
from app.models.budget import Budget
from app.models.category import Category

budgets = Blueprint('budgets', __name__, url_prefix='/budgets')  # Add url_prefix


@budgets.route('/', methods=['GET'])  # Changed from /budgets to /
@login_required
def index():
    """Display all budgets"""
    active_budgets = Budget.get_active_budgets(current_user.id)
    categories = Category.get_all_categories()
    form = BudgetForm()

    form.category.choices = [('', 'Select Category')] + [(cat, cat) for cat in categories.keys()]

    return render_template('budgets/index.html',
                           budgets=[b.to_dict() for b in active_budgets],
                           categories=categories,
                           form=form)


@budgets.route('/', methods=['POST'])  # Changed from /budgets to /
@login_required
def create_budget():
    """Create a new budget"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        form = BudgetForm(data=data)

        if form.validate():
            budget = Budget.create_budget(
                user_id=current_user.id,
                amount=float(form.amount.data),
                category=form.category.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                tag=form.tag.data if form.tag.data else None,
                notification_threshold=form.notification_threshold.data if hasattr(form,
                                                                                   'notification_threshold') else None
            )
            return jsonify(budget.to_dict()), 201
        else:
            return jsonify({'errors': form.errors}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@budgets.route('/api/budgets/<budget_id>', methods=['GET'])
@login_required
def get_budget(budget_id):
    """Get a specific budget"""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    return jsonify(budget.to_dict())


@budgets.route('/api/budgets/<budget_id>', methods=['PUT'])
@login_required
def update_budget(budget_id):
    """Update a specific budget"""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()

    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    form = BudgetForm(data=data)  # Initialize form with JSON data

    if form.validate():  # Use validate() instead of validate_on_submit() for API endpoints
        try:
            budget.amount = float(form.amount.data)
            budget.category = form.category.data
            budget.tag = form.tag.data if form.tag.data else None
            budget.start_date = form.start_date.data
            budget.end_date = form.end_date.data
            budget.notification_threshold = form.notification_threshold.data if hasattr(form,
                                                                                        'notification_threshold') else None

            db.session.commit()
            return jsonify(budget.to_dict())
        except ValueError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update budget'}), 500

    return jsonify({'errors': form.errors}), 400



@budgets.route('/api/budgets/<budget_id>', methods=['DELETE'])
@login_required
def delete_budget(budget_id):
    """Delete a specific budget"""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    try:
        db.session.delete(budget)
        db.session.commit()
        return '', 204
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete budget'}), 500


# Category and Tag Operations
@budgets.route('/api/categories/<category>/tags')
@login_required
def get_category_tags(category):
    """Get tags for a specific category"""
    try:
        tags = Category.get_tags_for_category(category)
        return jsonify(tags)
    except Exception as e:
        print(f"Error fetching tags: {e}")
        return jsonify([])
