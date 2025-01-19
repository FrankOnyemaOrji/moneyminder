document.addEventListener('DOMContentLoaded', function() {
    // Format currency helper function
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    // Time-based greeting update
    const updateGreeting = () => {
        const hour = new Date().getHours();
        const welcomeHeader = document.querySelector('.welcome-section h1');
        const username = welcomeHeader.textContent.split(',')[1].trim().replace('!', '');

        let greeting;
        if (hour >= 5 && hour < 12) {
            greeting = 'Good morning';
        } else if (hour >= 12 && hour < 17) {
            greeting = 'Good afternoon';
        } else {
            greeting = 'Good evening';
        }

        welcomeHeader.textContent = `${greeting}, ${username}!`;
    };

    // Update greeting immediately and set interval
    updateGreeting();
    setInterval(updateGreeting, 60000); // Update every minute

    // Update the date
    const updateDate = () => {
        const dateElement = document.querySelector('.welcome-section .date');
        if (dateElement) {
            const now = new Date();
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            dateElement.textContent = now.toLocaleDateString('en-US', options);
        }
    };

    // Update date immediately
    updateDate();

    // Update date every minute along with the greeting
    setInterval(() => {
        updateGreeting();
        updateDate();
    }, 60000);

    // Animate numbers counting up
    const animateValue = (element, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const current = Math.floor(progress * (end - start) + start);
            element.textContent = formatCurrency(current);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // Animate balance and overview numbers
    const balanceElement = document.querySelector('.balance-amount');
    if (balanceElement) {
        const balance = parseFloat(balanceElement.textContent.replace(/[^0-9.-]+/g, ''));
        animateValue(balanceElement, 0, balance, 1000);
    }

    // Initialize and animate progress bars
    const initProgressBars = () => {
        const progressBars = document.querySelectorAll('.progress-bar .progress');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    };

    // Handle transaction list interactions
    const initTransactionList = () => {
        const transactions = document.querySelectorAll('.transaction-item');
        transactions.forEach(transaction => {
            transaction.addEventListener('mouseenter', () => {
                transaction.style.backgroundColor = '#f9fafb';
            });
            transaction.addEventListener('mouseleave', () => {
                transaction.style.backgroundColor = '';
            });
        });
    };

    // Handle budget list interactions
    const initBudgetList = () => {
        const budgetItems = document.querySelectorAll('.budget-item');
        budgetItems.forEach(item => {
            const percentage = parseFloat(item.querySelector('.progress').style.width);
            if (percentage >= 90) {
                item.classList.add('warning');
            }
            if (percentage >= 100) {
                item.classList.add('exceeded');
            }
        });
    };

    // Initialize dashboard features
    initProgressBars();
    initTransactionList();
    initBudgetList();

    // Refresh dashboard data periodically (every 5 minutes)
    const refreshDashboard = async () => {
        try {
            const response = await fetch('/api/dashboard/refresh');
            if (response.ok) {
                const data = await response.json();
                updateDashboardData(data);
            }
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
        }
    };

    // Update dashboard with new data
    const updateDashboardData = (data) => {
        // Update account balances
        if (data.accounts) {
            data.accounts.forEach(account => {
                const accountElement = document.querySelector(`[data-account-id="${account.id}"] .account-balance`);
                if (accountElement) {
                    accountElement.textContent = formatCurrency(account.balance);
                }
            });
        }

        // Update recent transactions
        if (data.recentTransactions) {
            const transactionList = document.querySelector('.transaction-list');
            if (transactionList) {
                // Implementation for updating transactions
            }
        }

        // Update budget progress
        if (data.budgets) {
            data.budgets.forEach(budget => {
                const budgetElement = document.querySelector(`[data-budget-id="${budget.id}"]`);
                if (budgetElement) {
                    const progressBar = budgetElement.querySelector('.progress');
                    if (progressBar) {
                        progressBar.style.width = `${budget.percentage}%`;
                    }
                }
            });
        }
    };

    // Set up periodic refresh
    setInterval(refreshDashboard, 300000); // 5 minutes
});
