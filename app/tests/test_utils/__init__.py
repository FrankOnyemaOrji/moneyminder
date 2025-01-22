"""
Utility tests package initialization.
Provides common utilities and fixtures for testing utility functions.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime


class UtilsTestMixin:
    """Base mixin class for utility tests."""

    @staticmethod
    def create_test_file(base_path: Path, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        if not base_path.exists():
            base_path.mkdir(parents=True)

        file_path = base_path / filename
        file_path.write_text(content)
        return file_path

    @staticmethod
    def cleanup_test_files(path: Path):
        """Clean up test files after testing."""
        if path.exists():
            shutil.rmtree(path)

    @staticmethod
    def get_test_file_path(base_path: Path, filename: str) -> Path:
        """Get path for a test file."""
        return base_path / filename

    @staticmethod
    def format_date(date: datetime) -> str:
        """Format date for testing."""
        return date.strftime('%Y-%m-%d')


# Constants for testing
TEST_FILES_DIR = Path(__file__).parent / 'test_files'

# Supported file formats
SUPPORTED_FORMATS = ['pdf', 'xlsx', 'csv']

# Sample test data for reports
SAMPLE_REPORT_DATA = {
    'title': 'Test Report',
    'date_range': 'Jan 2025 - Dec 2025',
    'columns': ['Date', 'Description', 'Amount', 'Category'],
    'summary': {
        'total_income': 1000.00,
        'total_expenses': 500.00,
        'net_amount': 500.00
    }
}
