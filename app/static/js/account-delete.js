document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.querySelector('.delete-form');
    const submitButton = deleteForm?.querySelector('button[type="submit"]');
    const cancelButton = deleteForm?.querySelector('.btn-secondary');

    if (deleteForm) {
        initializeDeleteForm();
        initializeCancelButton();
    }

    function initializeDeleteForm() {
        deleteForm.addEventListener('submit', handleDelete);
    }

    function handleDelete(e) {
        e.preventDefault();

        // Check if delete is disabled due to non-zero balance
        if (submitButton.disabled) {
            showNotification('Cannot delete account with non-zero balance. Please clear the balance first.', 'error');
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';

        // Submit the delete request
        fetch(deleteForm.action, {
            method: 'POST',
            body: new FormData(deleteForm),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showNotification('Account deleted successfully', 'success');
                // Redirect after a short delay to show the success message
                setTimeout(() => {
                    window.location.href = '/accounts';
                }, 1000);
            } else {
                throw new Error(data.message || 'Failed to delete account');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification(error.message || 'An error occurred while deleting the account', 'error');
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        });
    }

    function initializeCancelButton() {
        if (cancelButton) {
            cancelButton.addEventListener('click', function(e) {
                e.preventDefault();
                window.history.back();
            });
        }
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">×</button>
        `;

        document.body.appendChild(notification);

        // Add close button functionality
        const closeButton = notification.querySelector('.notification-close');
        closeButton.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

        // Show notification with animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
});