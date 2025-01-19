from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional


class ReportFilterForm(FlaskForm):
    """Form for report filters"""
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])

    accounts = SelectMultipleField('Accounts', coerce=str)
    categories = SelectMultipleField('Categories')

    transaction_type = SelectField('Transaction Type',
                                   choices=[
                                       ('all', 'All'),
                                       ('income', 'Income'),
                                       ('expense', 'Expense')
                                   ])

    group_by = SelectField('Group By',
                           choices=[
                               ('date', 'Date'),
                               ('category', 'Category'),
                               ('account', 'Account')
                           ])

    format = SelectField('Format',
                         choices=[
                             ('csv', 'CSV'),
                             ('excel', 'Excel')
                         ])

    include_summary = BooleanField('Include Summary', default=True)
    include_charts = BooleanField('Include Charts', default=True)

    def __init__(self, user, *args, **kwargs):
        super(ReportFilterForm, self).__init__(*args, **kwargs)
        # Populate account choices
        self.accounts.choices = [(str(a.id), a.name) for a in user.accounts]


class ReportTemplateForm(FlaskForm):
    """Form for saving report templates"""
    name = StringField('Template Name',
                       validators=[DataRequired(), Length(max=100)])

    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=500)])

    is_default = BooleanField('Set as Default Template')