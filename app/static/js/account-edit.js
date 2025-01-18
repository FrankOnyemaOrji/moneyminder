document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.account-edit-form');
    const descriptionField = document.querySelector('textarea[name="description"]');
    const currencySelect = document.getElementById('currency');
    const deleteBtn = document.querySelector('.btn-danger');
    const characterCounter = document.querySelector('.character-counter');

    if (form) {
        initializeForm();
    }

    // Initialize all form functionality
    function initializeForm() {
        // Add character counter for description
        if (descriptionField && characterCounter) {
            updateCharacterCount();
            descriptionField.addEventListener('input', updateCharacterCount);
        }

        // Handle currency change warning
        if (currencySelect) {
            const originalCurrency = currencySelect.getAttribute('data-current-currency');
            currencySelect.addEventListener('change', function() {
                if (this.value !== originalCurrency) {
                    if (!confirm('Changing the currency may affect your transaction history. Are you sure you want to continue?')) {
                        this.value = originalCurrency;
                    }
                }
            });
        }

        // Handle form submission
        form.addEventListener('submit', handleFormSubmit);

        // Handle delete button
        if (deleteBtn) {
            deleteBtn.addEventListener('click', handleDelete);
        }
    }

    // Update character count for description
    function updateCharacterCount() {
        const maxLength = 500;
        const currentLength = descriptionField.value.length;
        characterCounter.textContent = `${currentLength}/${maxLength}`;

        if (currentLength > maxLength * 0.9) {
            characterCounter.classList.add('warning');
        } else {
            characterCounter.classList.remove('warning');
        }
    }

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');

        try {
            // Show loading state
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                showNotification('Account updated successfully', 'success');
                setTimeout(() => window.location.href = '/accounts', 1000);
            } else {
                throw new Error(data.message || 'Failed to update account');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification(error.message || 'An error occurred while updating the account', 'error');

            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    }

    // Handle delete button click
    function handleDelete(e) {
        e.preventDefault();
        const balance = parseFloat(deleteBtn.getAttribute('data-balance') || '0');

        if (balance !== 0) {
            showNotification('Cannot delete account with non-zero balance', 'error');
            return;
        }

        if (confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
            window.location.href = deleteBtn.href;
        }
    }

    // Show notification helper
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        const container = document.getElementById('notifications') || document.body;
        container.appendChild(notification);

        // Show with animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});