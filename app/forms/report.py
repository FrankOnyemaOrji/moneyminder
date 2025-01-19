from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from wtforms.validators import DataRequired


class ReportFilterForm(FlaskForm):
    """Form for report filters"""
    start_date = DateField('Start Date',
                           validators=[DataRequired()],
                           description='Select start date')

    end_date = DateField('End Date',
                         validators=[DataRequired()],
                         description='Select end date')

    account_id = SelectField('Account',
                             validators=[DataRequired()],
                             description='Select account',
                             coerce=str)

    format = SelectField('Format',
                         choices=[
                             ('xlsx', 'Microsoft Excel (.xlsx)'),
                             ('pdf', 'Adobe PDF (.pdf)')
                         ],
                         default='xlsx',
                         description='Select export format')

    def __init__(self, user, *args, **kwargs):
        super(ReportFilterForm, self).__init__(*args, **kwargs)
        # Populate account choices with currency info
        self.account_id.choices = [('', 'Select Account')] + [
            (str(a.id), f"{a.name} ({a.currency})")
            for a in user.accounts
        ]
