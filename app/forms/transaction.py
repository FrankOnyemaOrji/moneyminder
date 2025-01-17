from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DecimalField, SelectField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime


class TransactionForm(FlaskForm):
    amount = DecimalField('Amount',
                          validators=[
                              DataRequired(),
                              NumberRange(min=0.01, message='Amount must be greater than 0')
                          ]
                          )

    transaction_type = SelectField('Type',
                                   validators=[DataRequired()],
                                   choices=[
                                       ('income', 'Income'),
                                       ('expense', 'Expense')
                                   ]
                                   )

    category_id = SelectField('Category',
                              validators=[DataRequired()],
                              coerce=str
                              )

    account_id = SelectField('Account',
                             validators=[DataRequired()],
                             coerce=str
                             )

    date = DateField('Date',
                     validators=[DataRequired()],
                     default=datetime.utcnow
                     )

    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=500)]
                                )

    is_recurring = BooleanField('Recurring Transaction')

    recurrence_interval = SelectField('Repeat Every',
                                      choices=[
                                          ('', 'Never'),
                                          ('daily', 'Day'),
                                          ('weekly', 'Week'),
                                          ('monthly', 'Month'),
                                          ('yearly', 'Year')
                                      ],
                                      validators=[Optional()]
                                      )

    recurrence_end_date = DateField('End Date',
                                    validators=[Optional()]
                                    )

    submit = SubmitField('Save Transaction')

    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        # Populate account choices
        self.account_id.choices = [
            (str(account.id), account.name)
            for account in user.accounts
        ]
        # Populate category choices
        self.category_id.choices = [
            (str(category.id), category.name)
            for category in user.categories
        ]


class TransactionFilterForm(FlaskForm):
    start_date = DateField('From Date', validators=[Optional()])
    end_date = DateField('To Date', validators=[Optional()])

    type_filter = SelectField('Type',
                              choices=[
                                  ('all', 'All'),
                                  ('income', 'Income'),
                                  ('expense', 'Expense')
                              ],
                              default='all'
                              )

    account_filter = SelectField('Account',
                                 validators=[Optional()],
                                 coerce=str
                                 )

    category_filter = SelectField('Category',
                                  validators=[Optional()],
                                  coerce=str
                                  )

    min_amount = DecimalField('Min Amount',
                              validators=[Optional(), NumberRange(min=0)]
                              )

    max_amount = DecimalField('Max Amount',
                              validators=[Optional(), NumberRange(min=0)]
                              )

    search = StringField('Search',
                         validators=[Optional(), Length(max=100)]
                         )

    def __init__(self, user, *args, **kwargs):
        super(TransactionFilterForm, self).__init__(*args, **kwargs)
        # Add "All" option to account and category filters
        self.account_filter.choices = [('', 'All Accounts')] + [
            (str(account.id), account.name)
            for account in user.accounts
        ]
        self.category_filter.choices = [('', 'All Categories')] + [
            (str(category.id), category.name)
            for category in user.categories
        ]


class BulkTransactionForm(FlaskForm):
    file = FileField('CSV File',
                     validators=[
                         FileRequired(),
                         FileAllowed(['csv'], 'CSV files only!')
                     ]
                     )

    account_id = SelectField('Account',
                             validators=[DataRequired()],
                             coerce=str
                             )

    has_headers = BooleanField('File has headers', default=True)

    submit = SubmitField('Import Transactions')

    def __init__(self, user, *args, **kwargs):
        super(BulkTransactionForm, self).__init__(*args, **kwargs)
        self.account_id.choices = [
            (str(account.id), account.name)
            for account in user.accounts
        ]