// Utility Functions
const Utils = {
    formatCurrency: (value, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(value);
    },

    createTooltip: (text) => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        return tooltip;
    },

    positionTooltip: (tooltipEl, targetEl) => {
        const rect = targetEl.getBoundingClientRect();
        tooltipEl.style.top = `${rect.top - tooltipEl.offsetHeight - 5}px`;
        tooltipEl.style.left = `${rect.left + (rect.width - tooltipEl.offsetWidth) / 2}px`;
    },

    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);

        // Add click handler for close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
};

// Account List Page Functionality
const AccountList = {
    init() {
        this.bindElements();
        this.bindEvents();
        this.initializeTooltips();
        this.initializeCardEffects();
        this.formatCurrencyValues();
    },

    bindElements() {
        this.elements = {
            searchInput: document.querySelector('#searchAccounts'),
            typeFilter: document.querySelector('#accountTypeFilter'),
            sortSelect: document.querySelector('#sortAccounts'),
            accountCards: document.querySelectorAll('.account-card'),
            accountStats: document.querySelectorAll('.stat-value'),
            accountsGrid: document.querySelector('.accounts-grid'),
            quickActionToggles: document.querySelectorAll('.quick-action-toggle'),
            deleteButtons: document.querySelectorAll('[data-delete-account]')
        };
    },

    bindEvents() {
        // Search and filter
        if (this.elements.searchInput && this.elements.typeFilter && this.elements.sortSelect) {
            this.elements.searchInput.addEventListener('input', () => this.filterAndSortAccounts());
            this.elements.typeFilter.addEventListener('change', () => this.filterAndSortAccounts());
            this.elements.sortSelect.addEventListener('change', () => this.filterAndSortAccounts());
        }

        // Quick actions
        this.elements.quickActionToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => this.handleQuickActions(e));
        });

        // Delete confirmations
        this.elements.deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleDeleteConfirmation(e));
        });

        // Close quick actions on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.quick-actions')) {
                document.querySelectorAll('.quick-actions-menu.show')
                    .forEach(menu => menu.classList.remove('show'));
            }
        });
    },

    filterAndSortAccounts() {
        const searchTerm = this.elements.searchInput.value.toLowerCase();
        const selectedType = this.elements.typeFilter.value;
        const sortBy = this.elements.sortSelect.value;

        let visibleAccounts = Array.from(this.elements.accountCards)
            .filter(card => this.filterAccount(card, searchTerm, selectedType));

        this.sortAccounts(visibleAccounts, sortBy);
        this.updateDOM(visibleAccounts);
    },

    filterAccount(card, searchTerm, selectedType) {
        const accountName = card.querySelector('.account-name').textContent.toLowerCase();
        const accountType = card.querySelector('.account-type').className.split(' ')[1];
        const matchesSearch = accountName.includes(searchTerm);
        const matchesType = selectedType === 'all' || accountType === selectedType;

        card.style.display = matchesSearch && matchesType ? '' : 'none';
        return matchesSearch && matchesType;
    },

    sortAccounts(accounts, sortBy) {
        accounts.sort((a, b) => {
            const getValue = (element, selector) => {
                const el = element.querySelector(selector);
                return el ? el.textContent.trim() : '';
            };

            switch(sortBy) {
                case 'name':
                    return getValue(a, '.account-name').localeCompare(getValue(b, '.account-name'));
                case 'balance':
                    return this.compareCurrency(getValue(b, '.account-balance'), getValue(a, '.account-balance'));
                case 'activity':
                    return this.compareNumbers(getValue(b, '.transaction-count'), getValue(a, '.transaction-count'));
                default:
                    return 0;
            }
        });
    },

    compareCurrency(a, b) {
        return parseFloat(a.replace(/[^0-9.-]+/g, '')) - parseFloat(b.replace(/[^0-9.-]+/g, ''));
    },

    compareNumbers(a, b) {
        return parseInt(a) - parseInt(b);
    },

    updateDOM(visibleAccounts) {
        visibleAccounts.forEach(account => this.elements.accountsGrid.appendChild(account));
        this.updateEmptyState(visibleAccounts.length === 0);
    },

    updateEmptyState(isEmpty) {
        let emptyState = document.querySelector('.empty-state');

        if (isEmpty && !emptyState) {
            const emptyStateHtml = this.getEmptyStateHTML();
            this.elements.accountsGrid.insertAdjacentHTML('afterend', emptyStateHtml);
            this.elements.accountsGrid.style.display = 'none';
        } else if (!isEmpty && emptyState) {
            emptyState.remove();
            this.elements.accountsGrid.style.display = 'grid';
        }
    },

    getEmptyStateHTML() {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h2>No Accounts Found</h2>
                <p>Try adjusting your search criteria or create a new account.</p>
                <a href="/accounts/create" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Add Account
                </a>
            </div>
        `;
    },

    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', () => this.showTooltip(tooltip));
            tooltip.addEventListener('mouseleave', () => this.hideTooltip());
        });
    },

    showTooltip(element) {
        const tooltipEl = Utils.createTooltip(element.dataset.tooltip);
        document.body.appendChild(tooltipEl);
        Utils.positionTooltip(tooltipEl, element);
    },

    hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) tooltip.remove();
    },

    initializeCardEffects() {
        this.elements.accountCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    },

    formatCurrencyValues() {
        this.elements.accountStats.forEach(stat => {
            if (stat.dataset.value) {
                const value = parseFloat(stat.dataset.value);
                const currency = stat.dataset.currency || 'USD';
                stat.textContent = Utils.formatCurrency(value, currency);
            }
        });
    }
};

// Account Edit Page Functionality
const AccountEdit = {
    init() {
        if (!document.querySelector('.account-edit-form')) return;

        this.bindElements();
        this.bindEvents();
        this.initializeCharacterCounter();
    },

    bindElements() {
        this.elements = {
            form: document.querySelector('.account-edit-form'),
            currencySelect: document.getElementById('currency'),
            deleteButton: document.querySelector('.btn-danger'),
            descriptionField: document.getElementById('description'),
            submitButton: document.querySelector('button[type="submit"]')
        };
    },

    bindEvents() {
        if (this.elements.currencySelect) {
            this.handleCurrencyChange();
        }

        if (this.elements.deleteButton) {
            this.handleDelete();
        }

        if (this.elements.form) {
            this.handleFormSubmit();
        }
    },

    handleCurrencyChange() {
        const currentCurrency = this.elements.currencySelect.dataset.currentCurrency;
        
        this.elements.currencySelect.addEventListener('change', () => {
            const newCurrency = this.elements.currencySelect.value;
            if (newCurrency !== currentCurrency) {
                if (!confirm('Changing the currency may affect your transaction history. Are you sure you want to continue?')) {
                    this.elements.currencySelect.value = currentCurrency;
                }
            }
        });
    },

    handleDelete() {
        this.elements.deleteButton.addEventListener('click', (e) => {
            if (this.elements.deleteButton.classList.contains('disabled')) {
                e.preventDefault();
                Utils.showNotification('Cannot delete account with non-zero balance. Please clear the balance first.', 'warning');
                return;
            }

            if (!confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    },

    handleFormSubmit() {
        this.elements.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                Utils.showNotification('Please check the form for errors.', 'error');
            }
        });
    },

    validateForm() {
        // Add custom validation logic here
        return true;
    },

    initializeCharacterCounter() {
        if (!this.elements.descriptionField) return;

        const maxLength = this.elements.descriptionField.getAttribute('maxlength') || 500;
        const counterDiv = document.createElement('div');
        counterDiv.className = 'description-counter';
        this.elements.descriptionField.parentNode.appendChild(counterDiv);

        const updateCounter = () => {
            const remaining = maxLength - this.elements.descriptionField.value.length;
            counterDiv.textContent = `${remaining} characters remaining`;
            counterDiv.className = `description-counter ${remaining < 50 ? 'warning' : ''}`;
        };

        this.elements.descriptionField.addEventListener('input', updateCounter);
        updateCounter();
    }
};

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    AccountList.init();
    AccountEdit.init();
});