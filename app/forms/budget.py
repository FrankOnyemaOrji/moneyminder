from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime
from app.models.category import Category


class NoCSRFForm(FlaskForm):
    class Meta:
        csrf = False


class BudgetForm(NoCSRFForm):
    amount = DecimalField('Budget Amount',
                          validators=[
                              DataRequired(),
                              NumberRange(min=0.01, message='Amount must be greater than 0')
                          ])

    category = SelectField('Category',
                           validators=[DataRequired()],
                           choices=[])  # Will be populated from PRESET_CATEGORIES

    tag = SelectField('Tag',
                      validators=[Optional()],
                      choices=[])  # Will be populated based on selected category

    start_date = DateField('Start Date',
                           validators=[DataRequired()],
                           default=datetime.utcnow)

    end_date = DateField('End Date',
                         validators=[DataRequired()],
                         default=datetime.utcnow)

    notification_threshold = IntegerField('Notification Threshold (%)',
                                          validators=[Optional(),
                                                      NumberRange(min=1, max=100)],
                                          default=80)

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)

        # Populate category choices from preset categories
        self.category.choices = [('', 'Select Category')] + [
            (cat, cat) for cat in Category.PRESET_CATEGORIES.keys()
        ]

        # Initialize tag choices
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
