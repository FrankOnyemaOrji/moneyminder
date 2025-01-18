// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize all main functionalities
//     initializeBalanceChart();
//     initializeTransactionFilters();
//     initializeTableSorting();
//     initializeDeleteModal();
//     initializeDateRangeControls();
// });
//
// // Chart functionality
// function initializeBalanceChart() {
//     const chartCanvas = document.getElementById('balanceChart');
//     const timeRangeSelect = document.getElementById('timeRange');
//     const accountId = window.location.pathname.split('/').pop();
//     let balanceChart = null;
//
//     if (!chartCanvas || !timeRangeSelect) return;
//
//     async function loadBalanceHistory(days) {
//         try {
//             const response = await fetch(`/api/${accountId}/balance-history?days=${days}`);
//             if (!response.ok) throw new Error('Network response was not ok');
//
//             const data = await response.json();
//             if (data.success && data.balances) {
//                 updateChart(data.balances);
//             }
//         } catch (error) {
//             console.error('Error loading balance history:', error);
//             showChartError();
//         }
//     }
//
//     function updateChart(balances) {
//         const ctx = chartCanvas.getContext('2d');
//         const currencySymbol = document.querySelector('.balance-info .amount')?.textContent.trim()[0] || '$';
//
//         if (balanceChart) {
//             balanceChart.destroy();
//         }
//
//         balanceChart = new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: balances.map(item => formatDate(item.date)),
//                 datasets: [{
//                     label: 'Balance',
//                     data: balances.map(item => item.balance),
//                     borderColor: '#2563eb',
//                     backgroundColor: 'rgba(37, 99, 235, 0.1)',
//                     fill: true,
//                     tension: 0.4,
//                     pointRadius: 3,
//                     pointHoverRadius: 5
//                 }]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 plugins: {
//                     legend: { display: false },
//                     tooltip: {
//                         mode: 'index',
//                         intersect: false,
//                         callbacks: {
//                             label: context => `Balance: ${currencySymbol}${formatCurrency(context.parsed.y)}`
//                         }
//                     }
//                 },
//                 scales: {
//                     x: {
//                         grid: { display: false },
//                         ticks: { maxTicksLimit: 7 }
//                     },
//                     y: {
//                         beginAtZero: false,
//                         grid: { color: 'rgba(0, 0, 0, 0.1)' },
//                         ticks: {
//                             callback: value => currencySymbol + formatCurrency(value)
//                         }
//                     }
//                 }
//             }
//         });
//     }
//
//     function showChartError() {
//         chartCanvas.innerHTML = `
//             <div class="chart-error">
//                 <i class="fas fa-exclamation-circle"></i>
//                 <p>Error loading chart data</p>
//             </div>
//         `;
//     }
//
//     // Initial load and event listener
//     loadBalanceHistory(timeRangeSelect.value);
//     timeRangeSelect.addEventListener('change', () => loadBalanceHistory(timeRangeSelect.value));
// }
//
// // Transaction filters functionality
// function initializeTransactionFilters() {
//     const searchInput = document.getElementById('searchTransactions');
//     const typeFilter = document.getElementById('filterType');
//     const startDate = document.getElementById('startDate');
//     const endDate = document.getElementById('endDate');
//
//     if (!searchInput || !typeFilter || !startDate || !endDate) return;
//
//     const elements = [searchInput, typeFilter, startDate, endDate];
//     elements.forEach(element => {
//         element.addEventListener('change', filterTransactions);
//     });
//     searchInput.addEventListener('input', filterTransactions);
//
//     function filterTransactions() {
//         const rows = document.querySelectorAll('.transactions-table tbody tr');
//         const searchTerm = searchInput.value.toLowerCase();
//         const selectedType = typeFilter.value;
//         const startDateVal = new Date(startDate.value);
//         const endDateVal = new Date(endDate.value);
//
//         let visibleCount = 0;
//
//         rows.forEach(row => {
//             const description = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
//             const type = row.classList.contains('income') ? 'income' : 'expense';
//             const date = new Date(row.dataset.date);
//
//             const matchesSearch = description.includes(searchTerm);
//             const matchesType = selectedType === 'all' || type === selectedType;
//             const matchesDate = date >= startDateVal && date <= endDateVal;
//
//             const isVisible = matchesSearch && matchesType && matchesDate;
//             row.style.display = isVisible ? '' : 'none';
//             if (isVisible) visibleCount++;
//         });
//
//         updateEmptyState(visibleCount === 0);
//         updateTransactionCount(visibleCount);
//     }
// }
//
// // Date range controls
// function initializeDateRangeControls() {
//     const timeRange = document.getElementById('timeRange');
//     const startDate = document.getElementById('startDate');
//     const endDate = document.getElementById('endDate');
//
//     if (!timeRange || !startDate || !endDate) return;
//
//     timeRange.addEventListener('change', function() {
//         const days = parseInt(this.value);
//         const end = new Date();
//         const start = new Date();
//         start.setDate(start.getDate() - days);
//
//         startDate.value = formatDateForInput(start);
//         endDate.value = formatDateForInput(end);
//
//         // Trigger filter update
//         startDate.dispatchEvent(new Event('change'));
//     });
// }
//
// // Table sorting functionality
// function initializeTableSorting() {
//     const table = document.querySelector('.transactions-table');
//     if (!table) return;
//
//     const headers = table.querySelectorAll('th.sortable');
//     let currentSort = { column: 'date', direction: 'desc' };
//
//     headers.forEach(header => {
//         header.addEventListener('click', () => {
//             const column = header.dataset.sort;
//             const direction = currentSort.column === column &&
//                             currentSort.direction === 'asc' ? 'desc' : 'asc';
//
//             sortTable(table, column, direction);
//             updateSortIcons(headers, header, direction);
//             currentSort = { column, direction };
//         });
//     });
// }
//
// // Delete modal functionality
// function initializeDeleteModal() {
//     const modal = document.getElementById('deleteModal');
//     if (!modal) return;
//
//     let currentTransactionId = null;
//
//     // Setup delete button handlers
//     document.querySelectorAll('.delete-transaction').forEach(button => {
//         button.addEventListener('click', (e) => {
//             e.preventDefault();
//             currentTransactionId = button.dataset.id;
//             openModal(modal);
//         });
//     });
//
//     // Setup modal close handlers
//     modal.querySelectorAll('.modal-close').forEach(button => {
//         button.addEventListener('click', () => closeModal(modal));
//     });
//
//     // Setup delete confirmation
//     const confirmButton = modal.querySelector('#confirmDelete');
//     if (confirmButton) {
//         confirmButton.addEventListener('click', () => {
//             if (currentTransactionId) {
//                 deleteTransaction(currentTransactionId);
//             }
//         });
//     }
//
//     // Close modal on outside click
//     window.addEventListener('click', (e) => {
//         if (e.target === modal) {
//             closeModal(modal);
//         }
//     });
// }
//
// // Helper Functions
// function formatCurrency(value) {
//     return new Intl.NumberFormat('en-US', {
//         minimumFractionDigits: 2,
//         maximumFractionDigits: 2
//     }).format(value);
// }
//
// function formatDate(dateString) {
//     return new Intl.DateTimeFormat('en-US', {
//         month: 'short',
//         day: 'numeric'
//     }).format(new Date(dateString));
// }
//
// function formatDateForInput(date) {
//     return date.toISOString().split('T')[0];
// }
//
// function updateEmptyState(isEmpty) {
//     const container = document.querySelector('.transactions-table-container');
//     const table = document.querySelector('.transactions-table');
//     const existingEmptyState = container.querySelector('.empty-state');
//
//     if (!container || !table) return;
//
//     if (isEmpty) {
//         table.style.display = 'none';
//         if (!existingEmptyState) {
//             container.insertAdjacentHTML('beforeend', `
//                 <div class="empty-state">
//                     <div class="empty-state-icon">
//                         <i class="fas fa-search"></i>
//                     </div>
//                     <h3>No Matching Transactions</h3>
//                     <p>Try adjusting your search criteria</p>
//                 </div>
//             `);
//         }
//     } else {
//         table.style.display = '';
//         if (existingEmptyState) {
//             existingEmptyState.remove();
//         }
//     }
// }
//
// function updateTransactionCount(count) {
//     const subtitle = document.querySelector('.section-subtitle');
//     if (subtitle) {
//         subtitle.textContent = `${count} transactions found`;
//     }
// }
//
// function sortTable(table, column, direction) {
//     const tbody = table.querySelector('tbody');
//     const rows = Array.from(tbody.querySelectorAll('tr'));
//
//     const sortedRows = rows.sort((a, b) => {
//         let aVal = getCellValue(a, column);
//         let bVal = getCellValue(b, column);
//
//         if (column === 'amount') {
//             aVal = parseFloat(aVal.replace(/[^0-9.-]+/g, ''));
//             bVal = parseFloat(bVal.replace(/[^0-9.-]+/g, ''));
//         } else if (column === 'date') {
//             aVal = new Date(a.dataset.date);
//             bVal = new Date(b.dataset.date);
//         }
//
//         if (direction === 'desc') [aVal, bVal] = [bVal, aVal];
//
//         return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
//     });
//
//     sortedRows.forEach(row => tbody.appendChild(row));
// }
//
// function getCellValue(row, column) {
//     const cell = row.querySelector(`td:nth-child(${getColumnIndex(column)})`);
//     return cell ? cell.textContent.trim() : '';
// }
//
// function getColumnIndex(column) {
//     const indices = { 'date': 1, 'description': 2, 'category': 3, 'amount': 4 };
//     return indices[column] || 1;
// }
//
// function updateSortIcons(headers, activeHeader, direction) {
//     headers.forEach(header => {
//         const icon = header.querySelector('i');
//         icon.className = 'fas fa-sort';
//
//         if (header === activeHeader) {
//             icon.className = `fas fa-sort-${direction === 'asc' ? 'up' : 'down'}`;
//         }
//     });
// }
//
// function showNotification(message, type = 'info') {
//     const notification = document.createElement('div');
//     notification.className = `notification ${type}`;
//     notification.innerHTML = `
//         <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
//         <span>${message}</span>
//     `;
//
//     document.body.appendChild(notification);
//     setTimeout(() => notification.classList.add('show'), 10);
//     setTimeout(() => {
//         notification.classList.remove('show');
//         setTimeout(() => notification.remove(), 300);
//     }, 3000);
// }
