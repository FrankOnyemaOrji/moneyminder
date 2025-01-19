document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('createAccountForm');
    const accountTypeSelect = document.getElementById('account_type');
    const currencySelect = document.getElementById('currency');
    const currencySymbol = document.querySelector('.currency-symbol');
    const initialBalanceInput = document.getElementById('initial_balance');
    const descriptionInput = document.getElementById('description');
    const descriptionCounter = document.querySelector('.description-counter');

    // Currency symbol mapping
    const CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'INR': '₹'
    };

    if (form) {
        // Initialize form validation
        initializeFormValidation();

        // Handle form submission
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default submission

            // Validate all required fields
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            requiredFields.forEach(field => {
                if (!validateField({target: field})) {
                    isValid = false;
                }
            });

            if (isValid) {
                // Show loading state
                const submitButton = form.querySelector('[type="submit"]');
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

                // Submit the form using Fetch API
                fetch(form.action || window.location.href, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'Accept': 'application/json'
                    }
                })
                    .then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;
                            return;
                        }

                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            return response.json().then(data => {
                                if (!response.ok) {
                                    return Promise.reject(data);
                                }
                                return data;
                            });
                        } else {
                            // If response is not JSON and not a redirect, something went wrong
                            throw new Error('Unexpected response format');
                        }
                    })
                    .then(data => {
                        if (data && data.success) {
                            window.location.href = data.redirect;
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Save Account';

                        // Show error message
                        const errorMessage = error.message || 'An error occurred while creating the account';
                        showFlashMessage(errorMessage, 'error');
                    });
            } else {
                // Focus first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
        });
    }

    // Update currency symbol when currency changes
    if (currencySelect && currencySymbol) {
        currencySelect.addEventListener('change', function () {
            const currency = this.value;
            currencySymbol.textContent = CURRENCY_SYMBOLS[currency] || currency;
        });
    }

    // Add description character counter
    if (descriptionInput && descriptionCounter) {
        descriptionInput.addEventListener('input', function () {
            const length = this.value.length;
            descriptionCounter.textContent = `${length}/500`;
            descriptionCounter.style.color = length > 450 ? '#dc2626' : '#6b7280';
        });

        // Initialize counter
        descriptionCounter.textContent = `${descriptionInput.value.length}/500`;
    }

    function initializeFormValidation() {
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', validateField);
            field.addEventListener('input', clearError);
        });
    }

    function validateField(event) {
        const field = event.target;
        const errorDiv = field.parentElement.querySelector('.error-message');

        if (!field.value.trim()) {
            showError(field, errorDiv, 'This field is required');
            return false;
        }

        switch (field.id) {
            case 'name':
                return validateName(field, errorDiv);
            case 'initial_balance':
                return validateInitialBalance(field, errorDiv);
            default:
                clearError(field, errorDiv);
                return true;
        }
    }

    function validateName(field, errorDiv) {
        const value = field.value.trim();
        if (value.length < 2) {
            showError(field, errorDiv, 'Account name must be at least 2 characters');
            return false;
        }
        if (value.length > 100) {
            showError(field, errorDiv, 'Account name cannot exceed 100 characters');
            return false;
        }
        clearError(field, errorDiv);
        return true;
    }

    function validateInitialBalance(field, errorDiv) {
        const value = parseFloat(field.value);
        if (isNaN(value)) {
            showError(field, errorDiv, 'Please enter a valid number');
            return false;
        }
        if (value < 0) {
            showError(field, errorDiv, 'Initial balance cannot be negative');
            return false;
        }
        clearError(field, errorDiv);
        return true;
    }

    function showError(field, errorDiv, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    function clearError(field, errorDiv) {
        if (field.target) {
            field = field.target;
            errorDiv = field.parentElement.querySelector('.error-message');
        }
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (errorDiv) {
            errorDiv.textContent = '';
            errorDiv.style.display = 'none';
        }
    }

    function showFlashMessage(message, category = 'error') {
        const flashMessages = document.querySelector('.flash-messages');
        if (!flashMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `flash-message ${category}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${category === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
            <button class="close-flash">&times;</button>
        `;

        flashMessages.appendChild(messageDiv);

        // Add event listener to close button
        const closeButton = messageDiv.querySelector('.close-flash');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                messageDiv.remove();
            });
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => messageDiv.remove(), 300);
            }
        }, 5000);
    }

    // Add hover effect for help items
    const helpItems = document.querySelectorAll('.help-item');
    helpItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });

        item.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
});