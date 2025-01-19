from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import csv
import io
import pandas as pd

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.models.report_template import ReportTemplate
from app.forms.report import ReportTemplateForm

reports = Blueprint('reports', __name__, url_prefix='/reports')


@reports.route('/')
@login_required
def index():
    """Display reports dashboard"""
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    categories = Category.PRESET_CATEGORIES.keys()
    form = ReportTemplateForm()

    return render_template('reports/index.html',
                           accounts=accounts,
                           categories=list(categories),
                           form=form)


@reports.route('/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate transaction report based on filters"""
    try:
        # Create export filters from request
        filters = ExportFilters.from_request(request.form, current_user.id)

        # Build and execute query
        query = Transaction.query.filter_by(user_id=current_user.id)
        query = filters.build_query(query)
        transactions = query.all()

        if not transactions:
            return jsonify({'error': 'No transactions found for the selected criteria'}), 404

        # Generate report
        generator = ReportGenerator(transactions, filters)
        output, mimetype = generator.export()

        # Return file
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filters.get_filename()
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports.route('/preview')
@login_required
def preview_report():
    """Preview report results without downloading"""
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        account_ids = request.args.getlist('accounts')
        categories = request.args.getlist('categories')
        transaction_type = request.args.get('transaction_type', 'all')
        group_by = request.args.get('group_by', 'date')

        # Convert dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # Build query
        query = Transaction.query.filter_by(user_id=current_user.id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        if categories:
            query = query.filter(Transaction.category.in_(categories))
        if transaction_type != 'all':
            query = query.filter(Transaction.transaction_type == transaction_type)

        # Get total count for pagination info
        total_count = query.count()

        # Get transactions for preview
        transactions = query.order_by(Transaction.date.desc()).limit(10).all()

        # Convert transactions to dictionary for preview
        preview_data = []
        for t in transactions:
            preview_data.append({
                'Date': t.date.strftime('%Y-%m-%d'),
                'Account': t.account.name,
                'Type': t.transaction_type.capitalize(),
                'Category': t.category,
                'Description': t.description,
                'Amount': f"${float(t.amount):,.2f}"
            })

        # Calculate summary statistics using all transactions (not just preview)
        all_transactions = query.all()
        total_income = sum(float(t.amount) for t in all_transactions if t.transaction_type == 'income')
        total_expenses = sum(float(t.amount) for t in all_transactions if t.transaction_type == 'expense')

        return jsonify({
            'preview': preview_data,
            'summary': {
                'total_income': f"${total_income:,.2f}",
                'total_expenses': f"${total_expenses:,.2f}",
                'net_amount': f"${total_income - total_expenses:,.2f}",
                'transaction_count': total_count,
                'preview_count': len(preview_data)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports.route('/advanced', methods=['POST'])
@login_required
def generate_advanced_report():
    """Generate advanced analytics report"""
    try:
        filters = ExportFilters.from_request(request.form, current_user.id)
        query = Transaction.query.filter_by(user_id=current_user.id)
        query = filters.build_query(query)
        transactions = query.all()

        if not transactions:
            return jsonify({'error': 'No transactions found'}), 404

        generator = AdvancedReportGenerator(transactions, filters)
        output = generator.export_advanced_excel()

        filename = f'advanced_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports.route('/templates', methods=['GET'])
@login_required
def list_templates():
    """List all saved report templates"""
    try:
        templates = ReportTemplate.get_user_templates(current_user.id)
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports.route('/templates', methods=['POST'])
@login_required
def save_template():
    """Save a new report template"""
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('filters'):
            return jsonify({'error': 'Name and filters are required'}), 400

        template = ReportTemplate(
            name=data['name'],
            filters=data['filters'],
            description=data.get('description'),
            user_id=current_user.id
        )

        template.save()
        return jsonify(template.to_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports.route('/templates/<template_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_template(template_id):
    """Update or delete a report template"""
    try:
        template = ReportTemplate.query.filter_by(
            id=template_id,
            user_id=current_user.id
        ).first_or_404()

        if request.method == 'DELETE':
            template.delete()
            return '', 204

        data = request.get_json()
        if 'name' in data:
            template.name = data['name']
        if 'filters' in data:
            template.filters = data['filters']
        if 'description' in data:
            template.description = data['description']

        template.save()
        return jsonify(template.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500
