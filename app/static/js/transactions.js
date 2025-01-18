document.addEventListener('DOMContentLoaded', function() {
    // Category Management
    initializeCategoryManagement();
    initializeCategorySearch();
    restoreExpandedState();

    // Initialize color and icon previews
    updateColorPreview();
    updateIconPreview();

    // Charts Initialization
    initializeCharts();

    // Form Handling
    initializeFormHandling();
});

// Category Management Functions
function initializeCategoryManagement() {
    // Initialize category form event listener
    const categoryForm = document.getElementById('categoryForm');
    if (categoryForm) {
        categoryForm.addEventListener('submit', handleCategorySubmit);
    }

    // Initialize modal close on outside click
    window.onclick = function(event) {
        const modal = document.getElementById('categoryModal');
        if (event.target === modal) {
            hideCategoryModal();
        }
    };

    // Initialize color preview in select
    const colorSelect = document.getElementById('categoryColor');
    if (colorSelect) {
        colorSelect.addEventListener('change', updateColorPreview);
    }

    // Initialize icon preview in select
    const iconSelect = document.getElementById('categoryIcon');
    if (iconSelect) {
        iconSelect.addEventListener('change', updateIconPreview);
    }
}

function updateColorPreview() {
    const select = document.getElementById('categoryColor');
    const selectedOption = select.options[select.selectedIndex];
    const color = window.getComputedStyle(selectedOption).backgroundColor;
    select.style.borderLeft = `4px solid ${color}`;
}

function updateIconPreview() {
    const select = document.getElementById('categoryIcon');
    const selectedIcon = select.value;
    const iconPreview = document.querySelector('.icon-preview');
    if (iconPreview) {
        iconPreview.innerHTML = `<i class="fas fa-${selectedIcon}"></i>`;
    }
}

function toggleSubcategories(button) {
    const categoryItem = button.closest('.category-item');
    const subcategories = categoryItem.querySelector('.subcategories');
    if (subcategories) {
        const isHidden = subcategories.style.display === 'none';
        subcategories.style.display = isHidden ? 'block' : 'none';
        button.classList.toggle('expanded');

        // Save state to localStorage
        const categoryId = categoryItem.dataset.id;
        const expandedCategories = JSON.parse(localStorage.getItem('expandedCategories') || '{}');
        expandedCategories[categoryId] = isHidden;
        localStorage.setItem('expandedCategories', JSON.stringify(expandedCategories));
    }
}

function restoreExpandedState() {
    const expandedCategories = JSON.parse(localStorage.getItem('expandedCategories') || '{}');
    Object.entries(expandedCategories).forEach(([categoryId, isExpanded]) => {
        const categoryItem = document.querySelector(`.category-item[data-id="${categoryId}"]`);
        if (categoryItem && isExpanded) {
            const button = categoryItem.querySelector('.toggle-btn');
            if (button) {
                toggleSubcategories(button);
            }
        }
    });
}

function showCategoryModal(action, categoryId = null) {
    const modal = document.getElementById('categoryModal');
    const form = document.getElementById('categoryForm');
    const title = document.getElementById('modalTitle');

    // Reset form
    form.reset();

    if (action === 'edit' && categoryId) {
        title.textContent = 'Edit Category';
        // Fetch category data and populate form
        fetch(`/api/categories/${categoryId}`)
            .then(response => response.json())
            .then(category => {
                document.getElementById('categoryName').value = category.name;
                document.getElementById('categoryDesc').value = category.description || '';
                document.getElementById('parentCategory').value = category.parent_id || '';
                document.getElementById('categoryIcon').value = category.icon;
                document.getElementById('categoryColor').value = category.color;
                document.getElementById('isActive').checked = category.is_active;
                document.getElementById('isBudgetTracked').checked = category.is_budget_tracked;

                updateColorPreview();
                updateIconPreview();
            })
            .catch(error => {
                console.error('Error fetching category:', error);
                alert('Error loading category data');
            });
        form.action = `/categories/${categoryId}/edit`;
    } else {
        title.textContent = 'Add Category';
        form.action = '/categories/create';
    }

    modal.style.display = 'flex';
}

function deleteCategory(categoryId) {
    if (confirm('Are you sure you want to delete this category? This will also delete all subcategories.')) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

        fetch(`/categories/${categoryId}/delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Error deleting category');
                });
            }
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
    }
}

function handleCategorySubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Add boolean values explicitly
    formData.set('is_active', document.getElementById('isActive').checked);
    formData.set('is_budget_tracked', document.getElementById('isBudgetTracked').checked);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Error saving category');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        } else {
            throw new Error(data.message || 'Error saving category');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
}

function hideCategoryModal() {
    const modal = document.getElementById('categoryModal');
    modal.style.display = 'none';
}

// Category Tree Search and Filter
function initializeCategorySearch() {
    const searchInput = document.getElementById('categorySearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterCategories, 300));
    }
}

function filterCategories(e) {
    const searchTerm = e.target.value.toLowerCase();
    const categoryItems = document.querySelectorAll('.category-item');

    categoryItems.forEach(item => {
        const categoryName = item.querySelector('.category-name').textContent.toLowerCase();
        const isMatch = categoryName.includes(searchTerm);

        if (searchTerm === '') {
            item.style.display = '';
            const subcategories = item.querySelector('.subcategories');
            if (subcategories) {
                subcategories.style.display = 'none';
            }
        } else {
            if (isMatch) {
                item.style.display = '';
                let parent = item.parentElement;
                while (parent && parent.classList.contains('subcategories')) {
                    parent.style.display = 'block';
                    parent = parent.parentElement.parentElement;
                }
            } else {
                const hasMatchingChildren = Array.from(item.querySelectorAll('.category-name'))
                    .some(name => name.textContent.toLowerCase().includes(searchTerm));
                item.style.display = hasMatchingChildren ? '' : 'none';
            }
        }
    });
}

// Chart Initialization Functions
function initializeCharts() {
    const cashFlowCtx = document.getElementById('cashFlowChart');
    const categoryCtx = document.getElementById('categoryChart');

    if (cashFlowCtx) {
        initializeCashFlowChart(cashFlowCtx);
    }

    if (categoryCtx) {
        initializeCategoryChart(categoryCtx);
    }
}

function initializeCashFlowChart(ctx) {
    new Chart(ctx.getContext('2d'), {
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
}

function initializeCategoryChart(ctx) {
    new Chart(ctx.getContext('2d'), {
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
}

// Form Handling Functions
function initializeFormHandling() {
    const filterForm = document.getElementById('filterForm');
    const searchInput = document.querySelector('input[type="search"]');

    if (searchInput && filterForm) {
        searchInput.addEventListener('input', debounce(() => {
            filterForm.submit();
        }, 500));
    }
}

// Utility Functions
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

// Color Utility Functions
function getContrastColor(hexcolor) {
    // Convert hex to RGB
    const r = parseInt(hexcolor.slice(1,3),16);
    const g = parseInt(hexcolor.slice(3,5),16);
    const b = parseInt(hexcolor.slice(5,7),16);

    // Calculate luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    return luminance > 0.5 ? '#000000' : '#FFFFFF';
}
