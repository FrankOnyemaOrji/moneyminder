document.addEventListener('DOMContentLoaded', function () {
    // Form elements initialization
    const elements = {
        form: document.getElementById('budgetForm'),
        modal: document.getElementById('budgetModal'),
        modalTitle: document.getElementById('modalTitle'),
        category: document.getElementById('category'),
        tag: document.getElementById('tag'),
        amount: document.getElementById('amount'),
        quickPeriod: document.getElementById('quickPeriod'),
        startDate: document.getElementById('start_date'),
        endDate: document.getElementById('end_date'),
        submitButton: document.querySelector('#budgetForm button[type="submit"]'),
        createButtons: document.querySelectorAll('.create-budget-btn')
    };

    // Initialize form and attach event listeners if elements exist
    if (elements.form) {
        initializeForm();
        attachEventListeners();
    }

    // Modal Functions
    function openBudgetModal(budgetId = null) {
        if (!elements.modal) return;

        elements.modalTitle.textContent = budgetId ? 'Edit Budget' : 'New Budget';
        elements.form.reset();

        let budgetIdInput = document.getElementById('budgetId');
        if (!budgetIdInput) {
            budgetIdInput = document.createElement('input');
            budgetIdInput.type = 'hidden';
            budgetIdInput.id = 'budgetId';
            budgetIdInput.name = 'budgetId';
            elements.form.appendChild(budgetIdInput);
        }
        budgetIdInput.value = budgetId || '';

        if (budgetId) {
            fetchBudgetData(budgetId);
        } else {
            initializeForm();
            initializeCategories();
        }

        elements.modal.style.display = 'block';
    }

    function closeBudgetModal() {
        if (!elements.modal) return;
        elements.modal.style.display = 'none';
        if (elements.form) {
            elements.form.reset();
            clearAllErrors();
        }
    }

    // Make functions available globally
    window.openBudgetModal = openBudgetModal;
    window.closeBudgetModal = closeBudgetModal;
    window.editBudget = openBudgetModal;

    // Event Listeners
    function attachEventListeners() {
        elements.createButtons?.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                openBudgetModal();
            });
        });

        elements.category?.addEventListener('change', handleCategoryChange);
        elements.quickPeriod?.addEventListener('change', updateDateRange);
        elements.amount?.addEventListener('input', handleAmountInput);
        elements.amount?.addEventListener('blur', formatAmount);
        elements.form?.addEventListener('submit', handleBudgetSubmit);

        // Modal close handlers
        window.addEventListener('click', (event) => {
            if (event.target === elements.modal) {
                closeBudgetModal();
            }
        });

        window.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && elements.modal?.style.display === 'block') {
                closeBudgetModal();
            }
        });
    }

    // Budget deletion handler
    window.deleteBudget = async function(budgetId) {
        if (!confirm('Are you sure you want to delete this budget?')) {
            return;
        }

        try {
            const response = await fetch(`/budgets/api/budgets/${budgetId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete budget');
            }

            showSuccess('Budget deleted successfully!');
            setTimeout(() => window.location.reload(), 1500);
        } catch (error) {
            console.error('Error:', error);
            showError('Failed to delete budget. Please try again.');
        }
    };

    // Form Handling
    async function handleBudgetSubmit(e) {
        e.preventDefault();
        if (!validateForm()) return;

        const formData = new FormData(e.target);
        const budgetId = formData.get('budgetId');
        const isEdit = !!budgetId;

        try {
            showSubmitLoading();

            const jsonData = Object.fromEntries(formData.entries());
            const url = isEdit ? `/budgets/api/budgets/${budgetId}` : '/budgets/';
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(jsonData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save budget');
            }

            showSuccess(`Budget ${isEdit ? 'updated' : 'created'} successfully!`);
            setTimeout(() => window.location.reload(), 1500);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'Failed to save budget');
        } finally {
            hideSubmitLoading();
        }
    }

    // Form Initialization and Categories
    function initializeForm() {
        if (elements.quickPeriod && elements.startDate && elements.endDate) {
            updateDateRange();
        }

        if (elements.category && elements.category.value) {
            handleCategoryChange();
        }
    }

    function initializeCategories() {
        if (!elements.category) return;

        elements.category.innerHTML = '<option value="">Select Category</option>';

        if (typeof categoryData !== 'undefined') {
            for (const [category, details] of Object.entries(categoryData)) {
                const option = new Option(category, category);
                elements.category.appendChild(option);
            }
        }
    }

    async function handleCategoryChange() {
        const category = elements.category.value;
        if (!category) {
            resetTagSelect();
            return;
        }

        try {
            showLoading(elements.tag);
            if (categoryData && categoryData[category]) {
                updateTags(category);
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

    function updateTags(category) {
        if (!elements.tag) return;

        elements.tag.innerHTML = '<option value="">Select Tag</option>';

        if (category && categoryData?.[category]?.tags) {
            const tags = categoryData[category].tags;
            tags.forEach(tag => {
                const option = new Option(tag, tag);
                elements.tag.appendChild(option);
            });
            elements.tag.disabled = false;
        }
    }

    // Data Fetching
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

            await handleCategoryChange();
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

    // Helper Functions
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
        if (!elements.form) return false;

        let isValid = true;
        clearAllErrors();

        // Required field validation
        const requiredFields = {
            amount: 'Please enter an amount',
            category: 'Please select a category',
            start_date: 'Please select a start date',
            end_date: 'Please select an end date'
        };

        for (const [fieldName, message] of Object.entries(requiredFields)) {
            const field = elements.form.elements[fieldName];
            if (!field?.value) {
                showFieldError(field, message);
                isValid = false;
            }
        }

        // Amount validation
        const amountField = elements.form.elements['amount'];
        if (amountField?.value && parseFloat(amountField.value) <= 0) {
            showFieldError(amountField, 'Amount must be greater than zero');
            isValid = false;
        }

        // Date range validation
        const startDate = elements.form.elements['start_date']?.value;
        const endDate = elements.form.elements['end_date']?.value;
        if (startDate && endDate && new Date(endDate) < new Date(startDate)) {
            showFieldError(elements.form.elements['end_date'], 'End date must be after start date');
            isValid = false;
        }

        return isValid;
    }

    // Utility Functions
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

    function resetTagSelect() {
        if (elements.tag) {
            elements.tag.innerHTML = '<option value="">Select a category first</option>';
            elements.tag.disabled = true;
            elements.tag.value = '';
        }
    }
});