from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError
from datetime import datetime, date


class BudgetForm(FlaskForm):
    amount = DecimalField('Budget Amount',
                          validators=[
                              DataRequired(),
                              NumberRange(min=0.01, message='Amount must be greater than 0')
                          ]
                          )

    category_id = SelectField('Category',
                              validators=[DataRequired()],
                              coerce=str
                              )

    start_date = DateField('Start Date',
                           validators=[DataRequired()],
                           default=date.today
                           )

    end_date = DateField('End Date',
                         validators=[DataRequired()]
                         )

    notification_threshold = IntegerField('Alert Threshold (%)',
                                          validators=[
                                              Optional(),
                                              NumberRange(min=1, max=100)
                                          ],
                                          default=80
                                          )

    submit = SubmitField('Save Budget')

    def __init__(self, user, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # Populate category choices from user's categories
        self.category_id.choices = [
            (str(category.id), category.name)
            for category in user.categories
        ]

    def validate_end_date(self, field):
        if field.data <= self.start_date.data:
            raise ValidationError('End date must be after start date')
