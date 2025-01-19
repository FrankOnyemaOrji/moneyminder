// static/js/generate.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reportForm');
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');

    // Initialize form
    initializeDateFields();

    form.addEventListener('submit', handleFormSubmit);

    function initializeDateFields() {
        // Set min date to 1 year ago
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

        // Set max date to today
        const today = new Date();

        startDate.max = today.toISOString().split('T')[0];
        endDate.max = today.toISOString().split('T')[0];

        // Default to last 30 days if no dates selected
        if (!startDate.value) {
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            startDate.value = thirtyDaysAgo.toISOString().split('T')[0];
        }

        if (!endDate.value) {
            endDate.value = today.toISOString().split('T')[0];
        }
    }

    function validateDates() {
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);

        if (end < start) {
            showError('End date must be after start date');
            return false;
        }

        return true;
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        // Remove any existing error
        const existingError = form.querySelector('.error');
        if (existingError) {
            existingError.remove();
        }

        // Insert error before form actions
        const formActions = form.querySelector('.form-actions');
        form.insertBefore(errorDiv, formActions);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    async function handleFormSubmit(e) {
        e.preventDefault();

        if (!validateDates()) {
            return;
        }

        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');

        try {
            // Update button state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to generate report');
            }

            const blob = await response.blob();

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;

            // Get the proper file extension
            const format = formData.get('format');
            const timestamp = formatDate(new Date());
            let filename = `spending_report_${timestamp}`;

            // Set proper extension based on format
            if (format === 'xlsx') {
                filename += '.xlsx';
                a.setAttribute('download', filename); // Explicitly set download attribute
            } else {
                filename += '.pdf';
                a.setAttribute('download', filename);
            }

            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Error:', error);
            showError('Failed to generate report. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-file-export"></i> Generate Report';
        }
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0].replace(/-/g, '');
    }
});
