document.addEventListener('DOMContentLoaded', function() {
    initializeTransactionFilters();
    initializeTableSorting();
    initializeDeleteButtons();
});

// Initialize transaction filters
function initializeTransactionFilters() {
    const timeRange = document.getElementById('timeRange');
    if (!timeRange) return;

    timeRange.addEventListener('change', function() {
        const days = this.value;
        const accountId = getAccountIdFromUrl();
        
        // Update URL with new date range
        const searchParams = new URLSearchParams(window.location.search);
        searchParams.set('days', days);
        const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
        window.location.href = newUrl;
    });
}

// Initialize table sorting
function initializeTableSorting() {
    const table = document.querySelector('.transactions-table');
    if (!table) return;

    const headers = table.querySelectorAll('th.sortable');
    let currentSort = { column: 'date', direction: 'desc' };

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            const direction = currentSort.column === column && 
                            currentSort.direction === 'asc' ? 'desc' : 'asc';

            sortTable(table, column, direction);
            updateSortIcons(headers, header, direction);
            currentSort = { column, direction };
        });
    });
}

// Initialize delete buttons
function initializeDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-transaction');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const transactionId = button.dataset.id;

            if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/transactions/${transactionId}/delete`, {
                        method: 'POST',
                    });

                    const data = await response.json();

                    if (data.success) {
                        showNotification('Transaction deleted successfully', 'success');
                        // Remove the row from the table
                        button.closest('tr').remove();
                        // Check if table is empty
                        checkTableEmpty();
                    } else {
                        throw new Error(data.message || 'Failed to delete transaction');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showNotification(error.message || 'An error occurred while deleting the transaction', 'error');
                }
            }
        });
    });
}

// Helper Functions
function getAccountIdFromUrl() {
    return window.location.pathname.split('/').pop();
}

function sortTable(table, column, direction) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    const sortedRows = rows.sort((a, b) => {
        let aVal = getCellValue(a, column);
        let bVal = getCellValue(b, column);

        if (column === 'amount') {
            aVal = parseFloat(aVal.replace(/[^0-9.-]+/g, ''));
            bVal = parseFloat(bVal.replace(/[^0-9.-]+/g, ''));
        } else if (column === 'date') {
            aVal = new Date(a.dataset.date);
            bVal = new Date(b.dataset.date);
        }

        if (direction === 'desc') [aVal, bVal] = [bVal, aVal];

        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    });

    sortedRows.forEach(row => tbody.appendChild(row));
}

function getCellValue(row, column) {
    const indices = {
        'date': 0,
        'description': 1,
        'category': 2,
        'amount': 3
    };
    const cell = row.querySelector(`td:nth-child(${indices[column] + 1})`);
    return cell ? cell.textContent.trim() : '';
}

function updateSortIcons(headers, activeHeader, direction) {
    headers.forEach(header => {
        // Remove all sort classes
        header.classList.remove('asc', 'desc');
        
        // Add appropriate class to active header
        if (header === activeHeader) {
            header.classList.add(direction);
        }
    });
}

function checkTableEmpty() {
    const table = document.querySelector('.transactions-table');
    const container = document.querySelector('.transactions-table-container');
    const rows = table.querySelectorAll('tbody tr');

    if (rows.length === 0) {
        // Hide table
        table.style.display = 'none';
        
        // Show empty state
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
            <i class="fas fa-receipt"></i>
            <h3>No Transactions Found</h3>
            <p>There are no transactions for the selected period.</p>
            <a href="/transactions/create" class="btn btn-primary">
                <i class="fas fa-plus"></i> Add Transaction
            </a>
        `;
        container.appendChild(emptyState);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    // Add to container if it exists, otherwise add to body
    const container = document.querySelector('.notifications-container') || document.body;
    container.appendChild(notification);

    // Show notification with animation
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Export functions for potential reuse
window.AccountView = {
    initializeTransactionFilters,
    initializeTableSorting,
    initializeDeleteButtons,
    showNotification
};
