"""
Form tests package initialization.
Provides common utilities and constants for form testing.
"""
from flask_wtf import FlaskForm

# Common form validation error messages
FORM_ERRORS = {
    'required': 'This field is required.',
    'min_length': 'Field must be at least {min} characters long.',
    'max_length': 'Field cannot be longer than {max} characters.',
    'number_range': 'Amount must be greater than 0',
    'invalid_choice': 'Not a valid choice',
    'invalid_email': 'Invalid email address.',
    'invalid_currency': 'Invalid currency code.',
    'invalid_amount': 'Amount must be greater than 0',
    'password_mismatch': 'Passwords must match'
}


class FormTestMixin:
    """Mixin class with helper methods for form testing."""

    @staticmethod
    def validate_field_error(form: FlaskForm, field_name: str, expected_error: str) -> bool:
        """Check if a field has a specific error message."""
        if field_name not in form.errors:
            return False
        # Convert both strings to lowercase for comparison
        return any(expected_error.lower() in error.lower() for error in form.errors[field_name])

    @staticmethod
    def get_field_errors(form: FlaskForm, field_name: str) -> list:
        """Get all errors for a specific field."""
        return form.errors.get(field_name, [])

    @staticmethod
    def assert_field_required(form: FlaskForm, field_name: str) -> None:
        """Assert that a field is required."""
        assert FormTestMixin.validate_field_error(form, field_name, FORM_ERRORS['required'])
