document.addEventListener('DOMContentLoaded', function () {
    // Form elements initialization with corrected IDs
    const elements = {
        form: document.getElementById('budgetForm'),
        modal: document.getElementById('budgetModal'),
        modalTitle: document.getElementById('modalTitle'),
        category: document.getElementById('category'),
        tag: document.getElementById('tag'),
        amount: document.getElementById('amount'),
        quickPeriod: document.getElementById('quickPeriod'),
        startDate: document.getElementById('start_date'),  // Use underscore
        endDate: document.getElementById('end_date'),      // Use underscore
        submitButton: document.querySelector('button[type="submit"]'),
        createButtons: document.querySelectorAll('.create-budget-btn')
    };

    // Debug logging
    console.log('DOM loaded');
    console.log('Elements found:', {
        form: elements.form,
        modal: elements.modal,
        startDate: elements.startDate,
        endDate: elements.endDate,
        quickPeriod: elements.quickPeriod,
        createButtons: elements.createButtons?.length
    });

    // Initialize form and attach event listeners
    initializeForm();
    attachEventListeners();

    // Modal Functions
    // When opening modal for edit
function openBudgetModal(budgetId = null) {
    console.log('Opening modal for budget:', budgetId);
    if (!elements.modal) {
        console.error('Modal element not found');
        return;
    }

    elements.modalTitle.textContent = budgetId ? 'Edit Budget' : 'New Budget';
    elements.form.reset();

    // Update hidden budget ID field
    const budgetIdInput = document.getElementById('budgetId');
    if (budgetIdInput) {
        budgetIdInput.value = budgetId || '';
    }

    if (budgetId) {
        fetchBudgetData(budgetId);
    } else {
        initializeForm();
        initializeCategories();
    }

    elements.modal.style.display = 'block';
}

    function closeBudgetModal() {
        console.log('Closing modal');
        if (!elements.modal) {
            console.error('Modal element not found');
            return;
        }
        elements.modal.style.display = 'none';
        elements.form.reset();
        clearAllErrors();
    }

    // Make functions available globally
    window.openBudgetModal = openBudgetModal;
    window.closeBudgetModal = closeBudgetModal;
    window.editBudget = function (budgetId) {
        openBudgetModal(budgetId);
    };

    // Delete budget function
window.deleteBudget = async function (budgetId) {
    // Custom confirmation dialog instead of default browser confirm
    if (!window.confirm('Are you sure you want to delete this budget?')) {
        return;
    }

    try {
        const response = await fetch(`/budgets/api/budgets/${budgetId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrf_token]').value // Add CSRF token
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete budget');
        }

        showSuccess('Budget deleted successfully!');

        // Delay reload to show success message
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to delete budget. Please try again.');
    }
};

    // Event Listeners Initialization
    function attachEventListeners() {
        // Direct click handler for new budget buttons
        const createButtons = document.querySelectorAll('.create-budget-btn');
        console.log('Found create buttons:', createButtons.length);

        createButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                console.log('Button clicked');
                e.preventDefault();
                e.stopPropagation(); // Prevent event bubbling
                openBudgetModal();
            });
        });

        if (elements.category) {
            elements.category.addEventListener('change', function () {
                // Only call handleCategoryChange, remove updateTags call since it's called inside handleCategoryChange
                handleCategoryChange.call(this);
            });
        }

        if (elements.quickPeriod) {
            elements.quickPeriod.addEventListener('change', updateDateRange);
        }

        if (elements.amount) {
            elements.amount.addEventListener('input', handleAmountInput);
            elements.amount.addEventListener('blur', formatAmount);
        }

        if (elements.form) {
            elements.form.addEventListener('submit', handleBudgetSubmit);
        }

        // Close modal when clicking outside
        window.addEventListener('click', function (event) {
            if (event.target === elements.modal) {
                closeBudgetModal();
            }
        });
    }

    // Initialize categories and tags
    function initializeCategories() {
        console.log('Initializing categories');
        if (!elements.category) {
            console.error('Category element not found');
            return;
        }

        // Clear existing options
        elements.category.innerHTML = '<option value="">Select Category</option>';

        // Add categories from the server-provided data
        if (typeof categoryData !== 'undefined') {
            console.log('Category data available:', categoryData);
            for (const [category, details] of Object.entries(categoryData)) {
                const option = new Option(category, category);
                elements.category.appendChild(option);
            }
        } else {
            console.error('Category data not available');
        }
    }

    function updateTags(category) {
        if (!elements.tag) {
            console.error('Tag element not found');
            return;
        }

        // Clear existing options
        elements.tag.innerHTML = '<option value="">Select Tag</option>';

        // Add tags from categoryData
        if (category && categoryData && categoryData[category] && categoryData[category].tags) {
            const tags = categoryData[category].tags;
            console.log('Adding tags for category:', category, tags);

            tags.forEach(tag => {
                const option = new Option(tag, tag);
                elements.tag.appendChild(option);
            });

            // Enable the tag select
            elements.tag.disabled = false;
        }
    }


    // Form Handling Functions
    function initializeForm() {
        console.log('Initializing form with elements:', {
            quickPeriod: elements.quickPeriod?.id,
            startDate: elements.startDate?.id,
            endDate: elements.endDate?.id
        });

        if (elements.quickPeriod && elements.startDate && elements.endDate) {
            updateDateRange();
        }

        if (elements.category && elements.category.value) {
            handleCategoryChange.call(elements.category);
        }
    }

    async function handleCategoryChange() {
        const category = this.value;
        console.log('Category changed to:', category);

        if (!category) {
            resetTagSelect();
            return;
        }

        try {
            showLoading(elements.tag);
            // Use categoryData directly instead of API call
            if (categoryData && categoryData[category]) {
                updateTags(category);  // Pass the category, not the tags
            } else {
                throw new Error('Category data not found');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Failed to load tags');
            resetTagSelect();
        } finally {
            hideLoading(elements.tag);
        }
    }

    async function handleBudgetSubmit(e) {
    e.preventDefault();

    if (!validateForm()) {
        return;
    }

    const budgetId = document.getElementById('budgetId')?.value;
    const isEdit = !!budgetId;

    try {
        showSubmitLoading();
        const formData = new FormData(elements.form);

        // Convert FormData to JSON object
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        const url = isEdit ? `/budgets/api/budgets/${budgetId}` : '/budgets/';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrf_token]').value
            },
            body: JSON.stringify(jsonData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save budget');
        }

        const result = await response.json();
        showSuccess(`Budget ${isEdit ? 'updated' : 'created'} successfully!`);
        setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to save budget');
    } finally {
        hideSubmitLoading();
    }
}

    async function fetchBudgetData(budgetId) {
        try {
            showLoading(elements.form);
            const response = await fetch(`/budgets/api/budgets/${budgetId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch budget data');
            }

            const budget = await response.json();

            document.getElementById('budgetId').value = budget.id;
            elements.category.value = budget.category;
            elements.amount.value = budget.amount.toFixed(2);
            elements.startDate.value = budget.start_date.split('T')[0];
            elements.endDate.value = budget.end_date.split('T')[0];

            await handleCategoryChange.call(elements.category);
            if (budget.tag) {
                elements.tag.value = budget.tag;
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Failed to load budget data');
            closeBudgetModal();
        } finally {
            hideLoading(elements.form);
        }
    }

    // Utility Functions
    function handleAmountInput(e) {
        this.value = this.value.replace(/[^\d.]/g, '').replace(/(\..*)\./g, '$1');
        if (this.value.includes('.')) {
            const parts = this.value.split('.');
            if (parts[1].length > 2) {
                parts[1] = parts[1].slice(0, 2);
                this.value = parts.join('.');
            }
        }
    }

    function formatAmount() {
        const value = parseFloat(this.value);
        if (!isNaN(value)) {
            this.value = value.toFixed(2);
        }
    }

    function updateDateRange() {
        const period = elements.quickPeriod.value;
        const now = new Date();
        let startDate, endDate;

        switch (period) {
            case 'month':
                startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                break;
            case 'quarter':
                const quarter = Math.floor(now.getMonth() / 3);
                startDate = new Date(now.getFullYear(), quarter * 3, 1);
                endDate = new Date(now.getFullYear(), (quarter + 1) * 3, 0);
                break;
            case 'year':
                startDate = new Date(now.getFullYear(), 0, 1);
                endDate = new Date(now.getFullYear(), 11, 31);
                break;
            case 'custom':
                return;
        }

        elements.startDate.value = formatDateForInput(startDate);
        elements.endDate.value = formatDateForInput(endDate);
    }

    function validateForm() {
        let isValid = true;
        const requiredFields = [
            {element: elements.amount, message: 'Please enter an amount'},
            {element: elements.startDate, message: 'Please select a start date'},
            {element: elements.endDate, message: 'Please select an end date'},
            {element: elements.category, message: 'Please select a category'}
        ];

        clearAllErrors();

        requiredFields.forEach(field => {
            if (!field.element?.value) {
                showFieldError(field.element, field.message);
                isValid = false;
            }
        });

        if (elements.amount?.value && parseFloat(elements.amount.value) <= 0) {
            showFieldError(elements.amount, 'Amount must be greater than zero');
            isValid = false;
        }

        if (elements.startDate.value && elements.endDate.value) {
            const startDate = new Date(elements.startDate.value);
            const endDate = new Date(elements.endDate.value);
            if (endDate < startDate) {
                showFieldError(elements.endDate, 'End date must be after start date');
                isValid = false;
            }
        }

        return isValid;
    }

    // Helper Functions
    function formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }

    function showLoading(element) {
        if (element) {
            element.classList.add('loading');
            element.disabled = true;
        }
    }

    function hideLoading(element) {
        if (element) {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    function showSubmitLoading() {
        if (elements.submitButton) {
            elements.submitButton.classList.add('btn-loading');
            elements.submitButton.disabled = true;
        }
    }

    function hideSubmitLoading() {
        if (elements.submitButton) {
            elements.submitButton.classList.remove('btn-loading');
            elements.submitButton.disabled = false;
        }
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
