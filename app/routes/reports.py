from flask import Blueprint, render_template, request, send_file, current_app
from flask_login import login_required, current_user
from app.forms.report import ReportFilterForm
from app.models import Transaction
from app.utils.filters import ExportFilters
from app.utils.report_generator import ReportGenerator
import io

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_report():
    form = ReportFilterForm(current_user)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create filters from form data
            filters = ExportFilters(
                user_id=current_user.id,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                account_id=form.account_id.data,
                format=form.format.data
            )

            # Get transactions based on filters
            transactions = Transaction.query.filter_by(user_id=current_user.id)
            transactions = filters.build_query(transactions).order_by(Transaction.date.desc()).all()

            if not transactions:
                current_app.logger.info(f"No transactions found for the given filters")
                return render_template('reports/generate.html', form=form,
                                       error="No transactions found for the selected period")

            # Generate report
            generator = ReportGenerator(transactions, filters)
            output, mimetype, filename = generator.export()

            if not isinstance(output, io.BytesIO):
                output = io.BytesIO(output)

            output.seek(0)

            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
                max_age=0  # Prevent caching
            )

        except Exception as e:
            current_app.logger.error(f"Error generating report: {str(e)}")
            return render_template('reports/generate.html', form=form,
                                   error="An error occurred while generating the report")

    return render_template('reports/generate.html', form=form)
