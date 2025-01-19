document.addEventListener('DOMContentLoaded', function () {
    const typeSelect = document.getElementById('transaction_type');
    const amountInput = document.getElementById('amount');
    const form = document.querySelector('.transaction-form');

    // Format amount as currency
    amountInput.addEventListener('blur', function () {
        if (this.value) {
            const amount = parseFloat(this.value);
            if (!isNaN(amount)) {
                this.value = amount.toFixed(2);
            }
        }
    });

    // Change form styling based on transaction type
    typeSelect.addEventListener('change', function () {
        form.classList.remove('income', 'expense');
        form.classList.add(this.value);
    });
});

async function confirmDelete(deleteUrl) {
    if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
        try {
            const response = await fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.message || 'Failed to delete transaction');
                }
                if (data.success) {
                    window.location.href = '/transactions';
                }
            } else {
                throw new Error('Unexpected response format');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'An error occurred while deleting the transaction');
        }
    }
}
