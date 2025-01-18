from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, BooleanField,
    SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.models import Category


class CategoryForm(FlaskForm):
    """Form for creating and editing categories"""

    # Basic Information
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Category name must be between 2 and 100 characters')
    ])

    description = TextAreaField('Description',
                                validators=[Optional(), Length(max=500)],
                                description='Optional description for this category'
                                )

    # Category Type Selection
    category_type = SelectField('Category Type',
                                choices=[
                                    ('existing', 'Use Existing Category'),
                                    ('new', 'Create New Category')
                                ],
                                default='new'
                                )

    # Parent Category Selection
    parent_id = SelectField('Parent Category',
                            validators=[Optional()],
                            coerce=str,
                            description='Select a parent category or leave empty for top-level category'
                            )

    # Styling Options
    icon = SelectField('Category Icon',
                       choices=[],  # Will be populated from Category.ICON_CHOICES
                       description='Choose an icon to represent this category'
                       )

    color = SelectField('Category Color',
                        choices=[],  # Will be populated from Category.COLOR_CHOICES
                        description='Choose a color for charts and displays'
                        )

    # Additional Options
    is_active = BooleanField('Active Category',
                             default=True,
                             description='Inactive categories won\'t appear in transaction forms'
                             )

    is_budget_tracked = BooleanField('Track in Budget',
                                     default=True,
                                     description='Include this category in budget tracking and reports'
                                     )

    # For subcategories/tags
    subcategory_name = StringField('Subcategory/Tag Name',
                                   validators=[Optional(), Length(max=100)],
                                   description='Optional subcategory or tag name'
                                   )

    submit = SubmitField('Save Category')

    def __init__(self, user, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        # Populate icon choices from Category model
        self.icon.choices = [
            (icon_value, icon_name)
            for icon_value, icon_name in Category.ICON_CHOICES.items()
        ]

        # Populate color choices from Category model
        self.color.choices = [
            (color_value, color_info['name'])
            for color_value, color_info in Category.COLOR_CHOICES.items()
        ]

        # Populate parent category choices
        self.parent_id.choices = [('', 'No Parent (Top Level)')] + [
            (str(cat.id), cat.get_full_name())
            for cat in user.categories.filter_by(parent_id=None).all()
        ]

        self.user = user  # Store user for validation

    def validate_parent_id(self, field):
        if field.data:
            # Check if parent category exists and belongs to user
            parent = Category.query.filter_by(id=field.data).first()
            if not parent:
                raise ValidationError('Selected parent category does not exist.')
            if parent.user_id != self.user.id:
                raise ValidationError('Invalid parent category selected.')

            # Prevent circular reference when editing
            if hasattr(self, 'category_id') and field.data == self.category_id:
                raise ValidationError('A category cannot be its own parent.')

    def validate_subcategory_name(self, field):
        if field.data and not self.parent_id.data:
            raise ValidationError('Cannot create a subcategory without selecting a parent category.')


class CategoryDeleteForm(FlaskForm):
    """Form for deleting categories"""

    confirm_name = StringField('Confirm Category Name',
                               validators=[DataRequired()],
                               description='Enter the category name to confirm deletion'
                               )

    transfer_transactions = SelectField('Transfer Transactions To',
                                        validators=[Optional()],
                                        coerce=str,
                                        description='Optionally move existing transactions to another category'
                                        )

    submit = SubmitField('Delete Category')

    def __init__(self, user, category, *args, **kwargs):
        super(CategoryDeleteForm, self).__init__(*args, **kwargs)
        self.category = category

        # Populate transfer category choices excluding current category and its subcategories
        excluded_ids = [category.id] + [c.id for c in category.get_all_subcategories()]
        self.transfer_transactions.choices = [('', 'Delete Transactions')] + [
            (str(cat.id), cat.get_full_name())
            for cat in user.categories.filter(
                Category.id.notin_(excluded_ids)
            ).all()
        ]

    def validate_confirm_name(self, field):
        if field.data != self.category.name:
            raise ValidationError('Category name does not match. Please enter the exact name to confirm deletion.')
