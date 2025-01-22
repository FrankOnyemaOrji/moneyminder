from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class NoCSRFForm(FlaskForm):
    class Meta:
        csrf = False


class AccountForm(NoCSRFForm):
    name = StringField('Account Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Account name must be between 2 and 100 characters')
    ])

    account_type = SelectField('Account Type', validators=[DataRequired()],
                            choices=[
                                ('bank', 'Bank Account'),
                                ('cash', 'Cash'),
                                ('credit', 'Credit Card'),
                                ('investment', 'Investment Account'),
                                ('mobile_money', 'Mobile Money'),
                                ('other', 'Other')
                            ])

    currency = SelectField('Currency', validators=[DataRequired()],
                        choices=[
                            ('USD', 'US Dollar (USD)'),
                            ('EUR', 'Euro (EUR)'),
                            ('GBP', 'British Pound (GBP)'),
                            ('JPY', 'Japanese Yen (JPY)'),
                            ('CNY', 'Chinese Yuan (CNY)'),
                            ('INR', 'Indian Rupee (INR)')
                        ])

    initial_balance = DecimalField('Initial Balance',
                                validators=[DataRequired(), NumberRange(min=0)],
                                default=0.00)

    description = TextAreaField('Description',
                            validators=[Optional(), Length(max=500)])

    submit = SubmitField('Save Account')


class AccountEditForm(AccountForm):
    current_balance = DecimalField('Current Balance', render_kw={'readonly': True})

    def __init__(self, *args, **kwargs):
        super(AccountEditForm, self).__init__(*args, **kwargs)
        # Remove initial balance field as it shouldn't be edited after creation
        if 'initial_balance' in self:
            del self.initial_balance


class AccountDeleteForm(NoCSRFForm):
    submit = SubmitField('Confirm Delete')
