document.addEventListener('DOMContentLoaded', function() {
    // Chart configuration
    Chart.defaults.global.defaultFontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    Chart.defaults.global.defaultFontSize = 13;
    Chart.defaults.global.defaultFontColor = '#64748b';
    Chart.defaults.global.elements.line.tension = 0.4;

    // Initialize charts
    initializeCashFlowChart();
    initializeCategoryChart();

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
            updateCashFlowChart(this.value);
        });
    }

    // Chart type selector
    const categoryChartType = document.getElementById('categoryChartType');
    if (categoryChartType) {
        categoryChartType.addEventListener('change', function() {
            updateCategoryChartType(this.value);
        });
    }

    // Initialize tag options based on selected category
    function updateTagOptions(selectedCategory) {
        if (!selectedCategory) {
            tagFilter.innerHTML = '<option value="">All Tags</option>';
            tagFilter.closest('.tag-filter').style.display = 'none';
            return;
        }

        const categoryData = categorySummary[selectedCategory];
        if (!categoryData || (!categoryData.income && !categoryData.expense)) {
            tagFilter.innerHTML = '<option value="">No transactions in this category</option>';
            tagFilter.closest('.tag-filter').style.display = 'none';
            return;
        }

        const tags = categoryTags[selectedCategory]?.Subcategories || [];
        const usedTags = tags.filter(tag => {
            const tagData = categoryData.tags[tag];
            return tagData && (tagData.income > 0 || tagData.expense > 0);
        });

        tagFilter.innerHTML = '<option value="">All Tags</option>' +
            usedTags.map(tag => `<option value="${tag}">${tag}</option>`).join('');
        tagFilter.closest('.tag-filter').style.display = 'block';
    }

    async function initializeCashFlowChart() {
        const ctx = document.getElementById('cashFlowChart').getContext('2d');
        const gradientIncome = ctx.createLinearGradient(0, 0, 0, 400);
        gradientIncome.addColorStop(0, 'rgba(5, 150, 105, 0.2)');
        gradientIncome.addColorStop(1, 'rgba(5, 150, 105, 0.05)');

        const gradientExpense = ctx.createLinearGradient(0, 0, 0, 400);
        gradientExpense.addColorStop(0, 'rgba(220, 38, 38, 0.2)');
        gradientExpense.addColorStop(1, 'rgba(220, 38, 38, 0.05)');

        // Fetch initial data for the past 30 days
        const data = await fetchCashFlowData(30);

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Income',
                    borderColor: '#059669',
                    backgroundColor: gradientIncome,
                    borderWidth: 2,
                    pointBackgroundColor: '#059669',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    data: data.income,
                    fill: true
                }, {
                    label: 'Expenses',
                    borderColor: '#dc2626',
                    backgroundColor: gradientExpense,
                    borderWidth: 2,
                    pointBackgroundColor: '#dc2626',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    data: data.expenses,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        padding: 20,
                        boxWidth: 30
                    }
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleFontColor: '#1a202c',
                    bodyFontColor: '#1a202c',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
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
                        },
                        ticks: {
                            padding: 10,
                            fontColor: '#64748b'
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            borderDash: [2],
                            color: '#e2e8f0',
                            drawBorder: false
                        },
                        ticks: {
                            beginAtZero: true,
                            max: 100000,
                            stepSize: 20000,
                            padding: 10,
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }]
                }
            }
        });

        window.cashFlowChart = chart;
    }

    function initializeCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');

        const categoryColors = {
            'Transport': '#f48fb1',
            'Salary': '#f472b6',
            'Food': '#f59e0b',
            'Shopping': '#fb7185',
            'Investment': '#818cf8',
            'Healthcare': '#10b981',
            'Education': '#6366f1',
            'Entertainment': '#ec4899',
            'Gift': '#8b5cf6',
            'Travel': '#14b8a6',
            'Savings': '#06b6d4',
            'Home': '#8b5cf6'
        };

        // Get categories that actually have transactions
        const usedCategories = Object.entries(categorySummary)
            .filter(([_, summary]) => summary.income > 0 || summary.expense > 0)
            .map(([category, summary]) => ({
                category,
                total: summary.income + summary.expense,
                income: summary.income,
                expense: summary.expense,
                color: categoryColors[category] || '#64748b'
            }))
            .sort((a, b) => b.total - a.total);

        const chart = new Chart(ctx, {
            type: document.getElementById('categoryChartType').value || 'doughnut',
            data: {
                labels: usedCategories.map(item => item.category),
                datasets: [{
                    data: usedCategories.map(item => item.total),
                    backgroundColor: usedCategories.map(item => item.color),
                    borderWidth: 0,
                    categoryData: usedCategories // Store category data for tooltips
                }]
            },
            options: getChartOptions(document.getElementById('categoryChartType').value || 'doughnut')
        });

        window.categoryChart = chart;
    }

    async function fetchCashFlowData(days) {
        try {
            const response = await fetch(`/api/transactions/stats?days=${days}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            console.log('API Response:', data); // Debug log

            const sortedDates = Object.keys(data.daily_stats).sort();
            const chartData = {
                labels: sortedDates.map(date => new Date(date).toLocaleDateString()),
                income: sortedDates.map(date => data.daily_stats[date].income || 0),
                expenses: sortedDates.map(date => data.daily_stats[date].expense || 0)
            };

            console.log('Processed Chart Data:', chartData); // Debug log
            return chartData;

        } catch (error) {
            console.error('Error in fetchCashFlowData:', error);
            // Return some sample data for development
            const dates = Array.from({length: days}, (_, i) => {
                const date = new Date();
                date.setDate(date.getDate() - (days - 1 - i));
                return date.toLocaleDateString();
            });

            return {
                labels: dates,
                income: dates.map(() => Math.random() * 50000 + 30000),
                expenses: dates.map(() => Math.random() * 40000 + 20000)
            };
        }
    }

    async function updateCashFlowChart(days) {
        try {
            const data = await fetchCashFlowData(days);
            if (window.cashFlowChart) {
                // Update data
                window.cashFlowChart.data.labels = data.labels;
                window.cashFlowChart.data.datasets[0].data = data.income;
                window.cashFlowChart.data.datasets[1].data = data.expenses;

                // Force chart update
                window.cashFlowChart.update('active');

                // Log success for debugging
                console.log('Cash flow chart updated with data:', {
                    labels: data.labels.length,
                    income: data.income.length,
                    expenses: data.expenses.length
                });
            } else {
                console.warn('Cash flow chart not initialized');
                initializeCashFlowChart();
            }
        } catch (error) {
            console.error('Error updating cash flow chart:', error);
        }
    }

    function updateCategoryChartType(newType) {
        if (window.categoryChart) {
            const currentData = window.categoryChart.data;
            window.categoryChart.destroy();
            const ctx = document.getElementById('categoryChart').getContext('2d');

            window.categoryChart = new Chart(ctx, {
                type: newType,
                data: currentData,
                options: getChartOptions(newType)
            });
        }
    }

    function getChartOptions(chartType) {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: chartType === 'bar' ? 'top' : 'right',
                align: 'center'
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        const value = data.datasets[0].data[tooltipItem.index];
                        const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        const categoryData = data.datasets[0].categoryData[tooltipItem.index];
                        return [
                            `${data.labels[tooltipItem.index]}`,
                            `Total: $${value.toLocaleString()} (${percentage}%)`,
                            `Income: $${categoryData.income.toLocaleString()}`,
                            `Expenses: $${categoryData.expense.toLocaleString()}`
                        ];
                    }
                }
            }
        };

        if (chartType === 'bar') {
            return {
                ...baseOptions,
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
            };
        }

        return {
            ...baseOptions,
            cutoutPercentage: chartType === 'doughnut' ? 75 : 0
        };
    }

    // Handle search input with debounce
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            document.getElementById('filterForm').submit();
        }, 500));
    }

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

    // Handle delete confirmation
    window.confirmDelete = function(event) {
        return confirm('Are you sure you want to delete this transaction? This action cannot be undone.');
    };
});