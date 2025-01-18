document.addEventListener('DOMContentLoaded', function() {
    // Initialize Charts
    const cashFlowCtx = document.getElementById('cashFlowChart').getContext('2d');
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');

    // Cash Flow Chart
    new Chart(cashFlowCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Income',
                borderColor: '#059669',
                data: [4500, 5000, 4800, 5200, 4900, 5500],
                fill: false
            }, {
                label: 'Expenses',
                borderColor: '#dc2626',
                data: [3000, 3200, 3100, 3400, 3300, 3600],
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }]
            }
        }
    });

    // Category Breakdown Chart
    new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: ['Housing', 'Food', 'Transport', 'Entertainment'],
            datasets: [{
                data: [1200, 800, 400, 300],
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#e74c3c',
                    '#f1c40f'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'right'
            }
        }
    });

    // Handle form submission
    const filterForm = document.getElementById('filterForm');
    const searchInput = document.querySelector('input[type="search"]');

    // Debounce function for search
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Submit form on search input change (debounced)
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            filterForm.submit();
        }, 500));
    }
});
