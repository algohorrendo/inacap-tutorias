// INACAP Tutorías - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // CSRF Token for AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add CSRF token to all AJAX requests
    const csrftoken = getCookie('csrftoken');
    
    // Configure fetch to include CSRF token
    window.fetchWithCSRF = function(url, options = {}) {
        options.headers = options.headers || {};
        options.headers['X-CSRFToken'] = csrftoken;
        return fetch(url, options);
    };

    console.log('INACAP Tutorías - Loaded');
});

