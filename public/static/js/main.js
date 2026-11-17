document.addEventListener('DOMContentLoaded', function () {
    // Flash messages close themselves after 5 seconds. Add .alert-permanent
    // to keep one on screen.
    setTimeout(function () {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach(function (el) {
            bootstrap.Alert.getOrCreateInstance(el).close();
        });
    }, 5000);

    // Mark the nav link for the current page.
    document.querySelectorAll('.nav-link').forEach(function (link) {
        if (link.getAttribute('href') === window.location.pathname) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });

    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            // Stop double submits while the request is in flight.
            var button = form.querySelector('button[type="submit"]');
            if (button) {
                button.dataset.label = button.innerHTML;
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Please wait…';
            }
        });
    });
});

// Re-enable buttons when the browser restores a page from its back/forward cache.
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        document.querySelectorAll('button[type="submit"][disabled]').forEach(function (button) {
            button.disabled = false;
            if (button.dataset.label) button.innerHTML = button.dataset.label;
        });
    }
});
