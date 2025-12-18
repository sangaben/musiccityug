// Custom Admin JavaScript for MusicCityUG

document.addEventListener('DOMContentLoaded', function() {
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size/2;
            const y = e.clientY - rect.top - size/2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.7);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                top: ${y}px;
                left: ${x}px;
                pointer-events: none;
            `;
            
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add animation to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Add tooltips
    const tooltips = document.querySelectorAll('[title]');
    tooltips.forEach(element => {
        element.setAttribute('data-toggle', 'tooltip');
    });
    
    // Initialize tooltips
    if (typeof $ !== 'undefined') {
        $(function () {
            $('[data-toggle="tooltip"]').tooltip();
        });
    }
    
    // Custom confirmation for delete actions
    const deleteLinks = document.querySelectorAll('.deletelink');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Add music note animation to brand
    const brand = document.querySelector('.navbar-brand');
    if (brand) {
        setInterval(() => {
            const notes = ['🎵', '🎶', '🎼', '🎧', '🎤'];
            const randomNote = notes[Math.floor(Math.random() * notes.length)];
            brand.innerHTML = randomNote + ' MusicCityUG';
            
            setTimeout(() => {
                brand.innerHTML = '🎵 MusicCityUG';
            }, 1000);
        }, 10000);
    }
});

// Custom CSS animation for ripple effect
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .btn {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);