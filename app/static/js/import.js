document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('fileDropzone');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const previewContent = preview.querySelector('.preview-content');
    const importButton = document.getElementById('importButton');
    const downloadSampleBtn = document.getElementById('downloadSample');

    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        });
    });

    // Handle file drop
    dropzone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Handle click to upload
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (!file) return;

        if (file.type !== 'text/csv') {
            showError('Please select a CSV file');
            return;
        }

        // Update dropzone UI
        const dropzoneText = dropzone.querySelector('.dropzone-text .primary');
        dropzoneText.textContent = file.name;

        // Enable import button
        importButton.disabled = false;

        // Generate preview
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const text = e.target.result;
                generatePreview(text);
            } catch (error) {
                showError('Error reading file: ' + error.message);
            }
        };
        reader.onerror = function() {
            showError('Error reading file');
        };
        reader.readAsText(file);
    }

    function generatePreview(csvContent) {
        const lines = csvContent.split('\n');
        if (lines.length === 0) {
            showError('File is empty');
            return;
        }

        // Create preview table
        const table = document.createElement('table');
        table.className = 'preview-table';

        // Add header row
        const headerRow = document.createElement('tr');
        const headers = lines[0].split(',');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header.trim();
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        // Add preview rows (up to 5)
        for (let i = 1; i < Math.min(lines.length, 6); i++) {
            if (lines[i].trim()) {
                const row = document.createElement('tr');
                const cells = lines[i].split(',');
                cells.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell.trim();
                    row.appendChild(td);
                });
                table.appendChild(row);
            }
        }

        // Show preview
        previewContent.innerHTML = '';
        previewContent.appendChild(table);
        preview.classList.remove('hidden');
    }

    function showError(message) {
        // Create error element if it doesn't exist
        let errorElement = dropzone.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-message')) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            dropzone.parentNode.insertBefore(errorElement, dropzone.nextSibling);
        }
        errorElement.textContent = message;

        // Reset UI
        importButton.disabled = true;
        preview.classList.add('hidden');
        const dropzoneText = dropzone.querySelector('.dropzone-text .primary');
        dropzoneText.textContent = 'Drag and drop your CSV file here';
    }

    // Handle sample CSV download
    downloadSampleBtn.addEventListener('click', (e) => {
        e.preventDefault();

        const sampleData = `Date,Description,Amount,Type,Category
2024-01-15,Grocery Shopping,150.00,expense,Food
2024-01-16,Salary Payment,5000.00,income,Salary
2024-01-17,Gas Station,45.00,expense,Transport`;

        const blob = new Blob([sampleData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'sample_transactions.csv';

        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });

    // Validate form before submission
    const form = document.querySelector('form');
    form.addEventListener('submit', (e) => {
        const accountSelect = document.getElementById('account_id');
        if (!accountSelect.value) {
            e.preventDefault();
            showError('Please select an account');
            return;
        }

        if (!fileInput.files[0]) {
            e.preventDefault();
            showError('Please select a file to import');
            return;
        }
    });
});
