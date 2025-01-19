document.addEventListener('DOMContentLoaded', function() {
    // Form elements initialization
    const elements = {
        form: document.getElementById('budgetForm'),
        modal: document.getElementById('budgetModal'),
        modalTitle: document.getElementById('modalTitle'),
        category: document.getElementById('category'),
        tag: document.getElementById('tag'),
        amount: document.getElementById('amount'),
        quickPeriod: document.getElementById('quickPeriod'),
        startDate: document.getElementById('startDate'),
        endDate: document.getElementById('endDate'),
        submitButton: document.querySelector('button[type="submit"]'),
        createButtons: document.querySelectorAll('.new-budget-btn, .create-budget-btn')
    };

    // Initialize form and attach event listeners
    initializeForm();
    attachEventListeners();

    // Modal Functions
    function openBudgetModal(budgetId = null) {
        if (!elements.modal) {
            console.error('Modal element not found');
            return;
        }
        elements.modalTitle.textContent = budgetId ? 'Edit Budget' : 'New Budget';
        elements.form.reset();

        if (budgetId) {
            fetchBudgetData(budgetId);
        } else {
            initializeForm();
        }

        elements.modal.style.display = 'block';
    }

    function closeBudgetModal() {
        if (!elements.modal) {
            console.error('Modal element not found');
            return;
        }
        elements.modal.style.display = 'none';
        elements.form.reset();
        clearAllErrors();
    }

    // Make functions available globally with proper scoping
    window.openBudgetModal = openBudgetModal;
    window.closeBudgetModal = closeBudgetModal;
    window.editBudget = function(budgetId) {
        openBudgetModal(budgetId);
    };
    window.deleteBudget = async function(budgetId) {
        if (!confirm('Are you sure you want to delete this budget?')) {
            return;
        }

        try {
            const response = await fetch(`/api/budgets/${budgetId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
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

    // Event Listeners Initialization
    function attachEventListeners() {
        // Direct click handler for new budget buttons
        document.querySelectorAll('.new-budget-btn, .create-budget-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                openBudgetModal();
            });
        });

        // Legacy support for onclick attributes
        elements.createButtons?.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                openBudgetModal();
            });
        });

        if (elements.category && elements.tag) {
            elements.category.addEventListener('change', handleCategoryChange);
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
        window.addEventListener('click', function(event) {
            if (event.target === elements.modal) {
                closeBudgetModal();
            }
        });
    }

    // Form Handling Functions
    function initializeForm() {
        updateDateRange();
        if (elements.category && elements.category.value) {
            handleCategoryChange.call(elements.category);
        }
    }

    async function handleCategoryChange() {
        const category = this.value;
        if (!category) {
            resetTagSelect();
            return;
        }

        try {
            showLoading(elements.tag);
            const response = await fetch(`/api/categories/${encodeURIComponent(category)}/tags`);
            if (!response.ok) throw new Error('Failed to fetch tags');

            const tags = await response.json();
            updateTagSelect(tags);
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

        const budgetId = document.getElementById('budgetId').value;
        const formData = new FormData(elements.form);
        const data = Object.fromEntries(formData.entries());

        try {
            showSubmitLoading();
            const response = await fetch(budgetId ? `/api/budgets/${budgetId}` : '/api/budgets', {
                method: budgetId ? 'PUT' : 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Failed to save budget');
            }

            showSuccess(`Budget ${budgetId ? 'updated' : 'created'} successfully!`);
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
            const response = await fetch(`/api/budgets/${budgetId}`);
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

    // Rest of your existing utility functions...
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
            { element: elements.amount, message: 'Please enter an amount' },
            { element: elements.startDate, message: 'Please select a start date' },
            { element: elements.endDate, message: 'Please select an end date' },
            { element: elements.category, message: 'Please select a category' }
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