document.addEventListener('DOMContentLoaded', function() {
    // Handle Account Delete Form
    const deleteForm = document.querySelector('.delete-form');
    const confirmDeleteBtn = document.querySelector('.btn-danger[type="submit"]');
    const cancelBtn = document.querySelector('.btn-secondary');

    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Check if button is disabled due to non-zero balance
            if (confirmDeleteBtn.disabled) {
                showNotification('Cannot delete account with non-zero balance. Please clear the balance first.', 'error');
                return;
            }

            // Show loading state on button
            confirmDeleteBtn.disabled = true;
            const originalText = confirmDeleteBtn.innerHTML;
            confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';

            // Submit the form
            fetch(deleteForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams(new FormData(deleteForm))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Account deleted successfully!', 'success');
                    window.location.href = '/accounts';
                } else {
                    throw new Error(data.message || 'Failed to delete account');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'An error occurred while deleting the account', 'error');
                confirmDeleteBtn.disabled = false;
                confirmDeleteBtn.innerHTML = originalText;
            });
        });

        // Handle cancel button
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function(e) {
                e.preventDefault();
                window.history.back();
            });
        }
    }

    // Handle Account Edit Form
    const editForm = document.querySelector('.account-edit-form');
    if (editForm) {
        const submitBtn = editForm.querySelector('button[type="submit"]');

        editForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Show loading state
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

            // Submit the form
            fetch(editForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams(new FormData(editForm))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Account updated successfully!', 'success');
                    window.location.reload();
                } else {
                    throw new Error(data.message || 'Failed to update account');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'An error occurred while updating the account', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    }

    // Utility function to show notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});
