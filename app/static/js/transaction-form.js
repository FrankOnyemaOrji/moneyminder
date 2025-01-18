document.addEventListener('DOMContentLoaded', function() {
    const isRecurringCheckbox = document.getElementById('is_recurring');
    const recurrenceOptions = document.getElementById('recurrenceOptions');
    const typeSelect = document.getElementById('transaction_type');
    const amountInput = document.getElementById('amount');
    const form = document.querySelector('.transaction-form');

    // Set initial form class
    if (typeSelect.value) {
        form.classList.add(typeSelect.value);
    }

    // Toggle recurrence options
    if (isRecurringCheckbox) {
        isRecurringCheckbox.addEventListener('change', function() {
            recurrenceOptions.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Format amount as currency
    if (amountInput) {
        amountInput.addEventListener('blur', function() {
            if (this.value) {
                const amount = parseFloat(this.value);
                if (!isNaN(amount)) {
                    this.value = amount.toFixed(2);
                }
            }
        });
    }

    // Change form styling based on transaction type
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            form.classList.remove('income', 'expense');
            form.classList.add(this.value);
        });
    }

    // Set today's date if date field is empty
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        dateInput.valueAsDate = new Date();
    }
});
