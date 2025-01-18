document.addEventListener('DOMContentLoaded', function() {
    // Chart configuration
    Chart.defaults.global.defaultFontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    Chart.defaults.global.defaultFontSize = 13;
    Chart.defaults.global.defaultFontColor = '#64748b';
    Chart.defaults.global.elements.line.tension = 0.4;

    // Initialize charts
    const cashFlowChart = initializeCashFlowChart();
    const categoryChart = initializeCategoryChart();

    // Handle category filter changes
    const categoryFilter = document.getElementById('category_filter');
    const tagFilter = document.getElementById('tag_filter');
    if (categoryFilter && tagFilter) {
        categoryFilter.addEventListener('change', function() {
            updateTagOptions(this.value);
        });
    }

    // Chart period selector
    const cashflowPeriod = document.getElementById('cashflowPeriod');
    if (cashflowPeriod) {
        cashflowPeriod.addEventListener('change', function() {
            updateCashFlowChart(cashFlowChart, this.value);
        });
    }

    // Chart type selector
    const categoryChartType = document.getElementById('categoryChartType');
    if (categoryChartType) {
        categoryChartType.addEventListener('change', function() {
            updateCategoryChartType(categoryChart, this.value);
        });
    }

    // Initialize tag options based on selected category
    function updateTagOptions(selectedCategory) {
        const tags = categoryTags[selectedCategory]?.Subcategories || [];
        tagFilter.innerHTML = '<option value="">All Tags</option>' +
            tags.map(tag => `<option value="${tag}">${tag}</option>`).join('');

        const tagFilterGroup = document.querySelector('.tag-filter');
        tagFilterGroup.style.display = selectedCategory ? 'block' : 'none';
    }

    // Cash Flow Chart initialization
    function initializeCashFlowChart() {
        const ctx = document.getElementById('cashFlowChart').getContext('2d');
        const gradientIncome = ctx.createLinearGradient(0, 0, 0, 400);
        gradientIncome.addColorStop(0, 'rgba(5, 150, 105, 0.1)');
        gradientIncome.addColorStop(1, 'rgba(5, 150, 105, 0)');

        const gradientExpense = ctx.createLinearGradient(0, 0, 0, 400);
        gradientExpense.addColorStop(0, 'rgba(220, 38, 38, 0.1)');
        gradientExpense.addColorStop(1, 'rgba(220, 38, 38, 0)');

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Income',
                    borderColor: '#059669',
                    backgroundColor: gradientIncome,
                    borderWidth: 2,
                    pointBackgroundColor: '#059669',
                    data: []
                }, {
                    label: 'Expenses',
                    borderColor: '#dc2626',
                    backgroundColor: gradientExpense,
                    borderWidth: 2,
                    pointBackgroundColor: '#dc2626',
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'top',
                    align: 'end'
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            return data.datasets[tooltipItem.datasetIndex].label + ': $' +
                                   Number(tooltipItem.yLabel).toLocaleString(undefined, {
                                       minimumFractionDigits: 2,
                                       maximumFractionDigits: 2
                                   });
                        }
                    }
                },
                scales: {
                    xAxes: [{
                        gridLines: {
                            display: false
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            borderDash: [2],
                            color: '#e2e8f0'
                        },
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
    }

    // Category Chart initialization
    function initializeCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const categoryColors = Object.values(categoryData).map(cat => cat.color);
        const categoryLabels = Object.keys(categorySummary);
        const categoryAmounts = Object.values(categorySummary).map(cat => cat.expense);

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoryLabels,
                datasets: [{
                    data: categoryAmounts,
                    backgroundColor: categoryColors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'right',
                    align: 'center'
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const value = data.datasets[0].data[tooltipItem.index];
                            const percentage = ((value / categoryAmounts.reduce((a, b) => a + b)) * 100).toFixed(1);
                            return `${data.labels[tooltipItem.index]}: $${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                },
                cutoutPercentage: 75
            }
        });
    }

    // Update Cash Flow Chart data
    function updateCashFlowChart(chart, days) {
        // Here you would fetch new data based on the selected period
        // For now, we'll just update with dummy data
        const newData = generateDummyData(days);
        chart.data.labels = newData.labels;
        chart.data.datasets[0].data = newData.income;
        chart.data.datasets[1].data = newData.expenses;
        chart.update();
    }

    // Update Category Chart type
    function updateCategoryChartType(chart, newType) {
        chart.config.type = newType;
        chart.update();
    }

    // Handle delete confirmation
    window.confirmDelete = function(event) {
        return confirm('Are you sure you want to delete this transaction? This action cannot be undone.');
    };

    // Add debounce function for search
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

    // Handle search input
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            document.getElementById('filterForm').submit();
        }, 500));
    }
});
