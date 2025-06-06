// Main JavaScript for CyberShield SaaS Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Dashboard charts initialization
    initCharts();
    
    // Form validation
    validateForms();
    
    // Initialize data tables if present
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            }
        });
    }
});

// Initialize dashboard charts
function initCharts() {
    // Security Score Gauge Chart
    const securityScoreEl = document.getElementById('securityScoreChart');
    if (securityScoreEl) {
        const score = parseInt(securityScoreEl.getAttribute('data-score'));
        new Chart(securityScoreEl, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [getScoreColor(score), '#e2e8f0'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '75%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        enabled: false
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // Add score text in the center
        const scoreText = document.createElement('div');
        scoreText.classList.add('position-absolute', 'top-50', 'start-50', 'translate-middle', 'text-center');
        scoreText.innerHTML = `<h3 class="mb-0">${score}</h3><small>Score</small>`;
        securityScoreEl.parentNode.style.position = 'relative';
        securityScoreEl.parentNode.appendChild(scoreText);
    }
    
    // Threat Trend Chart
    const threatTrendEl = document.getElementById('threatTrendChart');
    if (threatTrendEl) {
        const dates = JSON.parse(threatTrendEl.getAttribute('data-dates'));
        const counts = JSON.parse(threatTrendEl.getAttribute('data-counts'));
        
        new Chart(threatTrendEl, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Security Events',
                    data: counts,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Vulnerability Severity Chart
    const vulnSeverityEl = document.getElementById('vulnSeverityChart');
    if (vulnSeverityEl) {
        const critical = parseInt(vulnSeverityEl.getAttribute('data-critical'));
        const high = parseInt(vulnSeverityEl.getAttribute('data-high'));
        const medium = parseInt(vulnSeverityEl.getAttribute('data-medium'));
        const low = parseInt(vulnSeverityEl.getAttribute('data-low'));
        
        new Chart(vulnSeverityEl, {
            type: 'pie',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [critical, high, medium, low],
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Compliance Status Chart
    const complianceStatusEl = document.getElementById('complianceStatusChart');
    if (complianceStatusEl) {
        const compliant = parseInt(complianceStatusEl.getAttribute('data-compliant'));
        const nonCompliant = parseInt(complianceStatusEl.getAttribute('data-non-compliant'));
        const partiallyCompliant = parseInt(complianceStatusEl.getAttribute('data-partially-compliant'));
        
        new Chart(complianceStatusEl, {
            type: 'bar',
            data: {
                labels: ['GDPR', 'PCI DSS', 'ISO 27001'],
                datasets: [{
                    label: 'Compliant',
                    data: [compliant, compliant - 2, compliant - 5],
                    backgroundColor: '#10b981'
                }, {
                    label: 'Partially Compliant',
                    data: [partiallyCompliant, partiallyCompliant + 2, partiallyCompliant + 1],
                    backgroundColor: '#f59e0b'
                }, {
                    label: 'Non-Compliant',
                    data: [nonCompliant, nonCompliant + 1, nonCompliant + 3],
                    backgroundColor: '#ef4444'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
}

// Get color based on security score
function getScoreColor(score) {
    if (score >= 90) return '#10b981'; // Green
    if (score >= 70) return '#3b82f6'; // Blue
    if (score >= 50) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
}

// Form validation
function validateForms() {
    // Example validation for password strength
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(function(field) {
        field.addEventListener('input', function() {
            const password = field.value;
            const strengthMeter = field.parentNode.querySelector('.password-strength');
            
            if (strengthMeter) {
                let strength = 0;
                
                // Length check
                if (password.length >= 8) strength += 1;
                
                // Uppercase check
                if (/[A-Z]/.test(password)) strength += 1;
                
                // Lowercase check
                if (/[a-z]/.test(password)) strength += 1;
                
                // Number check
                if (/[0-9]/.test(password)) strength += 1;
                
                // Special character check
                if (/[^A-Za-z0-9]/.test(password)) strength += 1;
                
                // Update strength meter
                strengthMeter.className = 'password-strength';
                if (strength === 0) {
                    strengthMeter.classList.add('bg-secondary');
                    strengthMeter.style.width = '0%';
                } else if (strength <= 2) {
                    strengthMeter.classList.add('bg-danger');
                    strengthMeter.style.width = '33%';
                } else if (strength <= 4) {
                    strengthMeter.classList.add('bg-warning');
                    strengthMeter.style.width = '66%';
                } else {
                    strengthMeter.classList.add('bg-success');
                    strengthMeter.style.width = '100%';
                }
            }
        });
    });
}

// API calls for dashboard data
function fetchDashboardData() {
    // Threat statistics
    fetch('/threats/api/stats')
        .then(response => response.json())
        .then(data => {
            updateThreatStats(data);
        })
        .catch(error => console.error('Error fetching threat stats:', error));
    
    // Vulnerability statistics
    fetch('/vulnerabilities/api/stats')
        .then(response => response.json())
        .then(data => {
            updateVulnerabilityStats(data);
        })
        .catch(error => console.error('Error fetching vulnerability stats:', error));
    
    // Compliance statistics
    fetch('/compliance/api/stats')
        .then(response => response.json())
        .then(data => {
            updateComplianceStats(data);
        })
        .catch(error => console.error('Error fetching compliance stats:', error));
}

// Update threat statistics in the UI
function updateThreatStats(data) {
    // Implementation would update UI elements with the data
    console.log('Threat stats:', data);
}

// Update vulnerability statistics in the UI
function updateVulnerabilityStats(data) {
    // Implementation would update UI elements with the data
    console.log('Vulnerability stats:', data);
}

// Update compliance statistics in the UI
function updateComplianceStats(data) {
    // Implementation would update UI elements with the data
    console.log('Compliance stats:', data);
}

// Simulate phishing attack
function simulatePhishing() {
    const form = document.getElementById('phishingSimulationForm');
    if (form) {
        const formData = new FormData(form);
        
        fetch('/phishing/simulate', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Phishing simulation created successfully', 'success');
            } else {
                showNotification('Error creating phishing simulation', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error creating phishing simulation', 'danger');
        });
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `toast align-items-center text-white bg-${type} border-0`;
    container.setAttribute('role', 'alert');
    container.setAttribute('aria-live', 'assertive');
    container.setAttribute('aria-atomic', 'true');
    
    container.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        toastContainer.appendChild(container);
    } else {
        const newContainer = document.createElement('div');
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        newContainer.appendChild(container);
        document.body.appendChild(newContainer);
    }
    
    const toast = new bootstrap.Toast(container);
    toast.show();
    
    // Remove after hiding
    container.addEventListener('hidden.bs.toast', function() {
        container.remove();
    });
}

