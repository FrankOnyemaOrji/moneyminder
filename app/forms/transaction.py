from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DecimalField, SelectField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime
from app.models.category import Category


class TransactionForm(FlaskForm):
    amount = DecimalField('Amount',
                          validators=[
                              DataRequired(),
                              NumberRange(min=0.01, message='Amount must be greater than 0')
                          ])

    transaction_type = SelectField('Type',
                                   validators=[DataRequired()],
                                   choices=[
                                       ('income', 'Income'),
                                       ('expense', 'Expense')
                                   ])

    category = SelectField('Category',
                           validators=[DataRequired()],
                           choices=[])  # Will be populated from PRESET_CATEGORIES

    tag = SelectField('Tag',
                      validators=[DataRequired()],
                      choices=[])  # Will be populated based on selected category

    account_id = SelectField('Account',
                             validators=[DataRequired()],
                             coerce=str)

    date = DateField('Date',
                     validators=[DataRequired()],
                     default=datetime.utcnow)

    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=500)])

    is_recurring = BooleanField('Recurring Transaction')

    recurrence_interval = SelectField('Repeat Every',
                                      choices=[
                                          ('', 'Never'),
                                          ('daily', 'Day'),
                                          ('weekly', 'Week'),
                                          ('monthly', 'Month'),
                                          ('yearly', 'Year')
                                      ],
                                      validators=[Optional()])

    recurrence_end_date = DateField('End Date',
                                    validators=[Optional()])

    submit = SubmitField('Save Transaction')

    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Populate account choices
        self.account_id.choices = [
            (str(account.id), account.name)
            for account in user.accounts
        ]

        # Populate category choices from preset categories
        self.category.choices = [('', 'Select Category')] + [
            (cat, cat) for cat in Category.PRESET_CATEGORIES.keys()
        ]

        # Initialize tag choices based on category if one is selected
        if self.category.data:
            self.update_tag_choices(self.category.data)
        else:
            self.tag.choices = [('', 'Select Tag')]

    def update_tag_choices(self, category):
        """Update tag choices based on selected category"""
        if category:
            tags = Category.get_tags_for_category(category)
            self.tag.choices = [('', 'Select Tag')] + [(tag, tag) for tag in tags]
        else:
            self.tag.choices = [('', 'Select Tag')]


class TransactionFilterForm(FlaskForm):
    start_date = DateField('From Date', validators=[Optional()])
    end_date = DateField('To Date', validators=[Optional()])

    type_filter = SelectField('Type',
                              choices=[
                                  ('all', 'All'),
                                  ('income', 'Income'),
                                  ('expense', 'Expense')
                              ],
                              default='all')

    account_filter = SelectField('Account',
                                 validators=[Optional()],
                                 coerce=str)

    category_filter = SelectField('Category',
                                  validators=[Optional()])

    tag_filter = SelectField('Tag',
                             validators=[Optional()])

    min_amount = DecimalField('Min Amount',
                              validators=[Optional(), NumberRange(min=0)])

    max_amount = DecimalField('Max Amount',
                              validators=[Optional(), NumberRange(min=0)])

    search = StringField('Search',
                         validators=[Optional(), Length(max=100)])

    def __init__(self, user, *args, **kwargs):
        super(TransactionFilterForm, self).__init__(*args, **kwargs)
        # Add "All" option to account filter
        self.account_filter.choices = [('', 'All Accounts')] + [
            (str(account.id), account.name)
            for account in user.accounts
        ]
        # Add "All" option to category filter using preset categories
        self.category_filter.choices = [('', 'All Categories')] + [
            (cat, cat) for cat in Category.PRESET_CATEGORIES.keys()
        ]
        # Initialize tag filter (will be populated via JavaScript)
        self.tag_filter.choices = [('', 'All Tags')]

    def update_tag_choices(self, category):
        """Update tag choices for the filter form"""
        if category:
            tags = Category.get_tags_for_category(category)
            self.tag_filter.choices = [('', 'All Tags')] + [(tag, tag) for tag in tags]
        else:
            self.tag_filter.choices = [('', 'All Tags')]


class BulkTransactionForm(FlaskForm):
    file = FileField('CSV File',
                     validators=[
                         FileRequired(),
                         FileAllowed(['csv'], 'CSV files only!')
                     ])

    account_id = SelectField('Account',
                             validators=[DataRequired()],
                             coerce=str)

    has_headers = BooleanField('File has headers', default=True)

    submit = SubmitField('Import Transactions')

    def __init__(self, user, *args, **kwargs):
        super(BulkTransactionForm, self).__init__(*args, **kwargs)
        self.account_id.choices = [
            (str(account.id), account.name)
            for account in user.accounts
        ]
