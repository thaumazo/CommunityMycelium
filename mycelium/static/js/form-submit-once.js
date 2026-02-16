/**
 * Form Submit Once - Prevents duplicate form submissions
 * 
 * Automatically handles all forms with data-submit-once attribute
 * Disables submit buttons and shows loading state after first submission
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all forms that should prevent duplicate submissions
    const forms = document.querySelectorAll('form[data-submit-once]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Find all submit buttons in this form
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            
            // Check if already submitting
            if (form.dataset.submitting === 'true') {
                e.preventDefault();
                return false;
            }
            
            // Mark as submitting
            form.dataset.submitting = 'true';
            
            // Disable and update each submit button
            submitButtons.forEach(function(button) {
                button.disabled = true;
                
                // Store original text
                if (!button.dataset.originalText) {
                    button.dataset.originalText = button.textContent || button.value;
                }
                
                // Update button text/value to show loading state
                const loadingText = button.dataset.loadingText || 'Saving...';
                if (button.tagName === 'BUTTON') {
                    button.textContent = loadingText;
                } else {
                    button.value = loadingText;
                }
                
                // Add loading class for CSS styling
                button.classList.add('submitting');
            });
        });
    });
});
