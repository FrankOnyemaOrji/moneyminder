document.addEventListener('DOMContentLoaded', function () {
    // Form elements
    const form = document.querySelector('.transaction-form');
    const typeSelect = document.querySelector('select[name="transaction_type"]');
    const typeRadios = document.querySelectorAll('.transaction-type-radio');
    const amountInput = document.querySelector('input[name="amount"]');
    const dateInput = document.querySelector('input[name="date"]');
    const categorySelect = document.querySelector('select[name="category"]');
    const tagSelect = document.querySelector('select[name="tag"]');
    const isRecurringCheckbox = document.getElementById('is_recurring');
    const recurrenceOptions = document.getElementById('recurrenceOptions');
    const submitButton = document.querySelector('button[type="submit"]');

    // Initialize form
    initializeForm();

    // Event Listeners
    if (typeRadios.length > 0) {
        typeRadios.forEach(radio => {
            radio.addEventListener('change', handleTransactionTypeChange);
        });
    } else if (typeSelect) {
        typeSelect.addEventListener('change', handleTransactionTypeChange);
    }

    if (amountInput) {
        amountInput.addEventListener('input', handleAmountInput);
        amountInput.addEventListener('blur', formatAmount);
    }

    if (categorySelect && tagSelect) {
        categorySelect.addEventListener('change', function (event) {
            handleCategoryChange.call(this, event);
        });
    }

    if (isRecurringCheckbox && recurrenceOptions) {
        isRecurringCheckbox.addEventListener('change', handleRecurringChange);
    }

    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Form Initialization
    function initializeForm() {
        // Set initial transaction type class from radio if present
        const checkedRadio = document.querySelector('.transaction-type-radio:checked');
        if (checkedRadio) {
            form.classList.add(checkedRadio.value);
            updateAmountPrefix(checkedRadio.value);
        } else if (typeSelect && typeSelect.value) {
            // Fallback to select if no radio buttons
            form.classList.add(typeSelect.value);
            updateAmountPrefix(typeSelect.value);
        }

        // Set today's date if empty
        if (dateInput && !dateInput.value) {
            dateInput.valueAsDate = new Date();
        }

        // Initialize category tags if category is selected
        if (categorySelect && categorySelect.value && tagSelect) {
            handleCategoryChange.call(categorySelect, {target: categorySelect});
        }
    }

    // Event Handlers
    function handleTransactionTypeChange() {
        form.classList.remove('income', 'expense');
        form.classList.add(this.value);
        updateAmountPrefix(this.value);
    }

    function handleAmountInput(e) {
        // Remove any non-numeric characters except decimal point
        let value = this.value.replace(/[^\d.]/g, '');

        // Ensure only one decimal point
        const decimalPoints = value.match(/\./g) || [];
        if (decimalPoints.length > 1) {
            value = value.replace(/\./, '');
        }

        // Limit to two decimal places
        const parts = value.split('.');
        if (parts[1] && parts[1].length > 2) {
            parts[1] = parts[1].slice(0, 2);
            value = parts.join('.');
        }

        this.value = value;
    }

    function formatAmount() {
        if (this.value) {
            const amount = parseFloat(this.value);
            if (!isNaN(amount)) {
                this.value = amount.toFixed(2);
            }
        }
    }

    async function handleCategoryChange(event) {
        const category = event ? event.target.value : this.value;
        if (!category) {
            resetTagSelect();
            return;
        }

        try {
            showLoading(tagSelect);

            // First, get the available tags
            const response = await fetch(`/transactions/api/categories/${category}/tags`);
            if (!response.ok) {
                throw new Error('Failed to fetch tags');
            }
            const tags = await response.json();

            // Update the tag select with new choices
            updateTagSelect(tags);
        } catch (error) {
            console.error('Error fetching tags:', error);
            showError('Failed to load tags for the selected category');
            resetTagSelect();
        } finally {
            hideLoading(tagSelect);
        }
    }

    function handleRecurringChange() {
        if (this.checked) {
            recurrenceOptions.classList.add('show');
        } else {
            recurrenceOptions.classList.remove('show');
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        try {
            showSubmitLoading();
            const formData = new FormData(this);

            // Add the selected transaction type
            const selectedType = document.querySelector('.transaction-type-radio:checked');
            if (selectedType) {
                formData.set('transaction_type', selectedType.value);
            }

            const response = await fetch(this.action, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to create transaction');
            }

            showSuccess('Transaction created successfully!');
            setTimeout(() => {
                window.location.href = '/transactions';
            }, 1500);

        } catch (error) {
            console.error('Error:', error);
            showError('Failed to create transaction. Please try again.');
        } finally {
            hideSubmitLoading();
        }
    }

    // Utility Functions
    function updateAmountPrefix(transactionType) {
        const prefix = document.querySelector('.input-group-text');
        if (prefix) {
            prefix.className = `input-group-text ${transactionType || ''}`;
        }
    }

    function confirmDelete(event) {
        event.preventDefault();
        if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
            event.target.submit();
        }
        return false;
    }

    function updateTagSelect(tags) {
        // Save current selected value if any
        const currentValue = tagSelect.value;

        // Clear and populate options
        tagSelect.innerHTML = '<option value="">Select a tag</option>';
        tags.forEach(tag => {
            const option = new Option(tag, tag, false, tag === currentValue);
            tagSelect.add(option);
        });

        // Enable the select
        tagSelect.disabled = false;

        // Trigger change event if value changed
        if (tagSelect.value !== currentValue) {
            tagSelect.dispatchEvent(new Event('change'));
        }
    }

    function resetTagSelect() {
        tagSelect.innerHTML = '<option value="">Select a category first</option>';
        tagSelect.disabled = true;
        tagSelect.dispatchEvent(new Event('change'));
    }

    function validateForm() {
        let isValid = true;
        const requiredFields = [
            {element: amountInput, message: 'Please enter an amount'},
            {element: dateInput, message: 'Please select a date'},
            {element: categorySelect, message: 'Please select a category'},
            {element: tagSelect, message: 'Please select a tag'}
        ];

        // Clear all previous errors first
        clearAllErrors();

        // Validate transaction type
        const selectedType = document.querySelector('.transaction-type-radio:checked') ||
            (typeSelect && typeSelect.value);
        if (!selectedType) {
            const typeContainer = document.querySelector('.type-selector');
            if (typeContainer) {
                showFieldError(typeContainer, 'Please select a transaction type');
            }
            isValid = false;
        }

        // Validate required fields
        requiredFields.forEach(field => {
            if (!field.element?.value) {
                showFieldError(field.element, field.message);
                isValid = false;
            }
        });

        // Additional validation for amount
        if (amountInput?.value && parseFloat(amountInput.value) <= 0) {
            showFieldError(amountInput, 'Amount must be greater than zero');
            isValid = false;
        }

        return isValid;
    }

    function clearAllErrors() {
        document.querySelectorAll('.error').forEach(error => error.remove());
        document.querySelectorAll('.form-control.error').forEach(field => {
            field.classList.remove('error');
        });
    }

    function showFieldError(element, message) {
        if (!element) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        const parent = element.closest('.form-group');
        if (parent) {
            parent.appendChild(errorDiv);
            element.classList.add('error');
        }
    }

    function showLoading(element) {
        if (element) {
            element.disabled = true;
            element.classList.add('loading');
        }
    }

    function hideLoading(element) {
        if (element) {
            element.disabled = false;
            element.classList.remove('loading');
        }
    }

    function showSubmitLoading() {
        if (submitButton) {
            submitButton.classList.add('btn-loading');
            submitButton.disabled = true;
        }
    }

    function hideSubmitLoading() {
        if (submitButton) {
            submitButton.classList.remove('btn-loading');
            submitButton.disabled = false;
        }
    }

    function showSuccess(message) {
        const toast = createToast('success', message);
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function showError(message) {
        const toast = createToast('error', message);
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    function createToast(type, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        return toast;
    }
});
