document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart.js balance history chart
    let balanceChart = null;

    async function initBalanceChart() {
        const accountId = window.location.pathname.split('/').pop();
        try {
            const response = await fetch(`/api/accounts/${accountId}/balance-history`);
            const data = await response.json();

            const ctx = document.getElementById('balanceChart').getContext('2d');

            if (balanceChart) {
                balanceChart.destroy();
            }

            balanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.balances.map(item => item.date),
                    datasets: [{
                        label: 'Balance',
                        data: data.balances.map(item => item.balance),
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `Balance: $${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 7
                            }
                        },
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error loading balance history:', error);
        }
    }

    // Transaction filtering and search
    const searchInput = document.getElementById('searchTransactions');
    const filterType = document.getElementById('filterType');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const transactionRows = document.querySelectorAll('.transactions-table tbody tr');

    function filterTransactions() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedType = filterType.value;
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);

        transactionRows.forEach(row => {
            const description = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const type = row.className;
            const date = new Date(row.querySelector('td:nth-child(1)').getAttribute('data-date'));

            const matchesSearch = description.includes(searchTerm);
            const matchesType = selectedType === 'all' || type === selectedType;
            const matchesDate = date >= startDate && date <= endDate;

            row.style.display = matchesSearch && matchesType && matchesDate ? '' : 'none';
        });

        updateEmptyState();
    }

    function updateEmptyState() {
        const visibleRows = document.querySelectorAll('.transactions-table tbody tr:not([style*="display: none"])');
        const emptyState = document.querySelector('.empty-state');

        if (visibleRows.length === 0) {
            if (!emptyState) {
                const container = document.querySelector('.transactions-table-container');
                container.insertAdjacentHTML('beforeend', `
                    <div class="empty-state">
                        <div class="empty-state-icon">
                            <i class="fas fa-search"></i>
                        </div>
                        <h3>No Matching Transactions</h3>
                        <p>Try adjusting your search criteria</p>
                    </div>
                `);
            }
            document.querySelector('.transactions-table').style.display = 'none';
        } else {
            if (emptyState) {
                emptyState.remove();
            }
            document.querySelector('.transactions-table').style.display = '';
        }
    }

    // Time range selector for balance chart
    const timeRange = document.getElementById('timeRange');
    timeRange.addEventListener('change', function() {
        const days = parseInt(this.value);
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        startDateInput.value = startDate.toISOString().split('T')[0];
        endDateInput.value = endDate.toISOString().split('T')[0];

        initBalanceChart();
        filterTransactions();
    });

    // Event listeners for filters
    searchInput.addEventListener('input', filterTransactions);
    filterType.addEventListener('change', filterTransactions);
    startDateInput.addEventListener('change', filterTransactions);
    endDateInput.addEventListener('change', filterTransactions);

    // Initialize components
    initBalanceChart();

    // Add date attributes for sorting
    transactionRows.forEach(row => {
        const dateCell = row.querySelector('td:first-child');
        const date = new Date(dateCell.textContent);
        dateCell.setAttribute('data-date', date.toISOString());
    });

    // Table sorting
    const tableHeaders = document.querySelectorAll('.transactions-table th');
    tableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = Array.from(header.parentElement.children).indexOf(header);
            sortTable(column);
        });
    });

    let sortDirection = 1; // 1 for ascending, -1 for descending
    function sortTable(column) {
        const tbody = document.querySelector('.transactions-table tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            let aValue = a.children[column].textContent;
            let bValue = b.children[column].textContent;

            if (column === 0) { // Date column
                aValue = new Date(a.children[column].getAttribute('data-date'));
                bValue = new Date(b.children[column].getAttribute('data-date'));
            } else if (column === 3) { // Amount column
                aValue = parseFloat(aValue.replace(/[^0-9.-]+/g, ''));
                bValue = parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
            }

            if (aValue < bValue) return -1 * sortDirection;
            if (aValue > bValue) return 1 * sortDirection;
            return 0;
        });

        sortDirection *= -1;

        // Update table with sorted rows
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }
});