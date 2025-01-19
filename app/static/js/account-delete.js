document.addEventListener('DOMContentLoaded', function () {
    const deleteForm = document.querySelector('.delete-form');
    const confirmDeleteBtn = document.querySelector('.btn-danger[type="submit"]');
    const goBackBtn = document.querySelector('.btn-secondary');

    if (deleteForm) {
        initializeDeleteForm();
    }

    function initializeDeleteForm() {
        // Handle form submission
        deleteForm.addEventListener('submit', handleDelete);

        // Handle go back button
        if (goBackBtn) {
            goBackBtn.addEventListener('click', function (e) {
                e.preventDefault();
                window.history.back();
            });
        }
    }

    async function handleDelete(e) {
        e.preventDefault();

        // Check if delete is disabled due to non-zero balance
        if (confirmDeleteBtn.disabled) {
            showNotification('Cannot delete account with non-zero balance. Please clear the balance first.', 'error');
            return;
        }

        try {
            // Show loading state
            confirmDeleteBtn.disabled = true;
            const originalText = confirmDeleteBtn.innerHTML;
            confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';

            const response = await fetch(deleteForm.action, {
                method: 'POST',
                body: new FormData(deleteForm),
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.redirected) {
                showNotification('Account deleted successfully', 'success');
                setTimeout(() => window.location.href = response.url, 1000);
                return;
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.message || 'Failed to delete account');
                }
                if (data.success) {
                    showNotification('Account deleted successfully', 'success');
                    setTimeout(() => window.location.href = '/accounts', 1000);
                }
            } else {
                throw new Error('Unexpected response format');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification(error.message || 'An error occurred while deleting the account', 'error');

            // Reset button state
            confirmDeleteBtn.disabled = false;
            confirmDeleteBtn.innerHTML = originalText;
        }
    }

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
