/**
 * ASSI Warehouse Management System
 * Main JavaScript file
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Language switcher
    document.querySelectorAll('.language-switcher').forEach(function(langBtn) {
        langBtn.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get language code from data attribute
            var langCode = langBtn.getAttribute('data-lang');
            
            // Set RTL for Arabic
            if (langCode === 'ar_SA') {
                setRTL(true);
            } else {
                setRTL(false);
            }
            
            // Send AJAX request to switch language
            fetch('/set_language/' + langCode, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload the page to reflect language change
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error switching language:', error);
            });
        });
    });
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            bootstrap.Alert.getInstance(alert)?.close();
        });
    }, 5000);
    
    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Initialize date pickers
    var datePickers = document.querySelectorAll('.datepicker');
    if (typeof flatpickr !== 'undefined') {
        datePickers.forEach(function(picker) {
            flatpickr(picker, {
                dateFormat: "Y-m-d",
                allowInput: true
            });
        });
    }
    
    // Dynamic table sorting
    document.querySelectorAll('th.sortable').forEach(function(header) {
        header.addEventListener('click', function() {
            var table = header.closest('table');
            var index = Array.from(header.parentNode.children).indexOf(header);
            var rows = Array.from(table.querySelectorAll('tbody tr'));
            var isAsc = header.classList.contains('asc');
            
            // Remove sorting classes from all headers
            table.querySelectorAll('th.sortable').forEach(function(h) {
                h.classList.remove('asc', 'desc');
            });
            
            // Sort direction
            if (isAsc) {
                header.classList.add('desc');
            } else {
                header.classList.add('asc');
            }
            
            // Sort rows
            rows.sort(function(a, b) {
                var aValue = a.children[index].textContent.trim();
                var bValue = b.children[index].textContent.trim();
                
                // Check if numeric
                if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
                    aValue = parseFloat(aValue);
                    bValue = parseFloat(bValue);
                }
                
                if (aValue < bValue) {
                    return isAsc ? 1 : -1;
                }
                if (aValue > bValue) {
                    return isAsc ? -1 : 1;
                }
                return 0;
            });
            
            // Update DOM
            var tbody = table.querySelector('tbody');
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        });
    });
    
    // Handle confirmation dialogs
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(event) {
            if (!confirm(element.getAttribute('data-confirm'))) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
    
    // Handle dynamic form fields (add/remove)
    document.querySelectorAll('.add-field-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var container = document.getElementById(btn.getAttribute('data-container'));
            var template = document.getElementById(btn.getAttribute('data-template'));
            var clone = template.content.cloneNode(true);
            container.appendChild(clone);
            
            // Initialize any components in the new row
            container.querySelector('.row:last-child').querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
                new bootstrap.Tooltip(el);
            });
        });
    });
    
    // Event delegation for dynamically added remove buttons
    document.addEventListener('click', function(event) {
        if (event.target.matches('.remove-field-btn')) {
            event.target.closest('.row').remove();
        }
    });
    
    // Item quantity calculator for invoices
    document.querySelectorAll('.invoice-item-row input').forEach(function(input) {
        input.addEventListener('change', calculateInvoiceTotal);
    });
    
    // Currency formatter
    document.querySelectorAll('.currency-input').forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(input.value.replace(/[^\d.-]/g, ''));
            if (!isNaN(value)) {
                input.value = value.toFixed(2);
            }
        });
    });
});

// Calculate invoice total
function calculateInvoiceTotal() {
    var total = 0;
    document.querySelectorAll('.invoice-item-row').forEach(function(row) {
        var quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
        var price = parseFloat(row.querySelector('.price-input').value) || 0;
        var rowTotal = quantity * price;
        
        row.querySelector('.row-total').textContent = rowTotal.toFixed(2);
        total += rowTotal;
    });
    
    // Update subtotal
    var subtotalElement = document.getElementById('invoice-subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = total.toFixed(2);
    }
    
    // Calculate tax if applicable
    var taxRate = parseFloat(document.getElementById('tax-rate')?.value || 0) / 100;
    var taxAmount = total * taxRate;
    var taxElement = document.getElementById('invoice-tax');
    if (taxElement) {
        taxElement.textContent = taxAmount.toFixed(2);
    }
    
    // Calculate grand total
    var additionalCosts = parseFloat(document.getElementById('additional-costs')?.value || 0);
    var grandTotal = total + taxAmount + additionalCosts;
    var grandTotalElement = document.getElementById('invoice-total');
    if (grandTotalElement) {
        grandTotalElement.textContent = grandTotal.toFixed(2);
    }
}