document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.getElementById('transaction_type');
    const amountInput = document.getElementById('amount');
    const form = document.querySelector('.transaction-form');

    // Format amount as currency
    amountInput.addEventListener('blur', function() {
        if (this.value) {
            const amount = parseFloat(this.value);
            if (!isNaN(amount)) {
                this.value = amount.toFixed(2);
            }
        }
    });

    // Change form styling based on transaction type
    typeSelect.addEventListener('change', function() {
        form.classList.remove('income', 'expense');
        form.classList.add(this.value);
    });
});

function confirmDelete(deleteUrl) {
    if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = deleteUrl;
        document.body.appendChild(form);
        form.submit();
    }
}
