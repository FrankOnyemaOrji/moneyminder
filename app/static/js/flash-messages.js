document.addEventListener('DOMContentLoaded', function() {
    // Handle flash message closing
    document.querySelectorAll('.close-flash').forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                flashMessage.remove();
            }, 300);
        });
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.flash-message').forEach(message => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
    }, 5000);
});

// Add this to your CSS if not already present
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
