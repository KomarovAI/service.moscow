/**
 * Service.Moscow - Modern JavaScript
 * Optimized for performance and accessibility
 */

// Utility functions
const Utils = {
    // Debounce function для оптимизации производительности
    debounce: (func, wait, immediate) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },

    // Throttle function
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    },

    // Smooth scroll to element
    scrollTo: (element, offset = 0) => {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    },

    // Format phone number
    formatPhone: (phone) => {
        const cleaned = ('' + phone).replace(/\D/g, '');
        const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})$/);
        if (match) {
            return '+' + match[1] + ' (' + match[2] + ') ' + match[3] + '-' + match[4] + '-' + match[5];
        }
        return phone;
    },

    // Validate email
    isValidEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate phone
    isValidPhone: (phone) => {
        const cleaned = phone.replace(/\D/g, '');
        return cleaned.length >= 10 && cleaned.length <= 11;
    }
};

// Mobile menu functionality
class MobileMenu {
    constructor() {
        this.menuToggle = document.getElementById('nav-toggle');
        this.menu = document.getElementById('nav-menu');
        this.menuLinks = document.querySelectorAll('.nav__link');
        
        this.init();
    }

    init() {
        if (this.menuToggle && this.menu) {
            this.menuToggle.addEventListener('click', () => this.toggleMenu());
            
            // Close menu when clicking on links
            this.menuLinks.forEach(link => {
                link.addEventListener('click', () => this.closeMenu());
            });

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!this.menu.contains(e.target) && !this.menuToggle.contains(e.target)) {
                    this.closeMenu();
                }
            });
        }
    }

    toggleMenu() {
        this.menu.classList.toggle('show-menu');
        this.menuToggle.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = this.menu.classList.contains('show-menu') ? 'hidden' : '';
    }

    closeMenu() {
        this.menu.classList.remove('show-menu');
        this.menuToggle.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Header scroll effect
class HeaderScroll {
    constructor() {
        this.header = document.getElementById('header');
        this.init();
    }

    init() {
        if (this.header) {
            window.addEventListener('scroll', Utils.throttle(() => {
                this.handleScroll();
            }, 100));
        }
    }

    handleScroll() {
        const scrollY = window.scrollY;
        
        if (scrollY > 100) {
            this.header.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
            this.header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
        } else {
            this.header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            this.header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        }
    }
}

// Smooth scrolling for navigation links
class SmoothScroll {
    constructor() {
        this.init();
    }

    init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    Utils.scrollTo(target, 80); // 80px offset for fixed header
                }
            });
        });
    }
}

// Form handling
class FormHandler {
    constructor() {
        this.forms = document.querySelectorAll('form');
        this.init();
    }

    init() {
        this.forms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubmit(e, form));
            
            // Phone number formatting
            const phoneInputs = form.querySelectorAll('input[type="tel"], input[name="phone"]');
            phoneInputs.forEach(input => {
                input.addEventListener('input', (e) => this.formatPhoneInput(e));
                input.addEventListener('keypress', (e) => this.onlyNumbers(e));
            });
        });
    }

    handleSubmit(e, form) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Validation
        if (!this.validateForm(data, form)) {
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправляем...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual API call)
        setTimeout(() => {
            this.showSuccess(form);
            this.resetForm(form);
            
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 2000);
        
        // Track form submission (Google Analytics)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'form_submit', {
                'event_category': 'engagement',
                'event_label': form.id || 'contact_form'
            });
        }
    }

    validateForm(data, form) {
        let isValid = true;
        
        // Remove previous errors
        form.querySelectorAll('.error').forEach(error => error.remove());
        form.querySelectorAll('.form__input.invalid').forEach(input => {
            input.classList.remove('invalid');
        });
        
        // Required fields validation
        if (!data.name || data.name.trim().length < 2) {
            this.showError(form.querySelector('[name="name"]'), 'Введите корректное имя');
            isValid = false;
        }
        
        if (!data.phone || !Utils.isValidPhone(data.phone)) {
            this.showError(form.querySelector('[name="phone"]'), 'Введите корректный номер телефона');
            isValid = false;
        }
        
        if (data.email && !Utils.isValidEmail(data.email)) {
            this.showError(form.querySelector('[name="email"]'), 'Введите корректный email');
            isValid = false;
        }
        
        return isValid;
    }

    showError(input, message) {
        input.classList.add('invalid');
        const error = document.createElement('div');
        error.className = 'error';
        error.textContent = message;
        error.style.cssText = 'color: #e74c3c; font-size: 0.85rem; margin-top: 5px;';
        input.parentNode.appendChild(error);
    }

    showSuccess(form) {
        const success = document.createElement('div');
        success.className = 'success-message';
        success.innerHTML = `
            <div style="background: #27ae60; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center;">
                ✅ Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 5 минут.
            </div>
        `;
        
        form.insertBefore(success, form.firstChild);
        
        setTimeout(() => {
            success.remove();
        }, 5000);
    }

    resetForm(form) {
        form.reset();
        form.querySelectorAll('.form__input.invalid').forEach(input => {
            input.classList.remove('invalid');
        });
    }

    formatPhoneInput(e) {
        let x = e.target.value.replace(/\D/g, '').match(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
        e.target.value = !x[2] ? x[1] : '+' + x[1] + ' (' + x[2] + ') ' + x[3] + (x[4] ? '-' + x[4] : '') + (x[5] ? '-' + x[5] : '');
    }

    onlyNumbers(e) {
        if (!/\d/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'Home', 'End', 'ArrowLeft', 'ArrowRight', 'Clear', 'Copy', 'Paste'].includes(e.key)) {
            e.preventDefault();
        }
    }
}

// Floating call button animation
class FloatingButton {
    constructor() {
        this.button = document.getElementById('floating-call');
        this.init();
    }

    init() {
        if (this.button) {
            // Hide button initially
            this.button.style.transform = 'scale(0)';
            
            // Show button when scrolled down
            window.addEventListener('scroll', Utils.throttle(() => {
                if (window.scrollY > 500) {
                    this.button.style.transform = 'scale(1)';
                } else {
                    this.button.style.transform = 'scale(0)';
                }
            }, 100));
            
            // Track clicks
            this.button.addEventListener('click', () => {
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'click', {
                        'event_category': 'engagement',
                        'event_label': 'floating_call_button'
                    });
                }
            });
        }
    }
}

// Intersection Observer for animations
class ScrollAnimations {
    constructor() {
        this.observer = null;
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        // Stop observing this element
                        this.observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // Observe elements for animation
            document.querySelectorAll('.service-card, .advantage, .review, .stat').forEach(el => {
                this.observer.observe(el);
            });
        }
    }
}

// Counter animation for statistics
class CounterAnimation {
    constructor() {
        this.init();
    }

    init() {
        const counters = document.querySelectorAll('.stat__number');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            counters.forEach(counter => observer.observe(counter));
        }
    }

    animateCounter(element) {
        const target = parseInt(element.textContent.replace(/\D/g, ''));
        const increment = target / 50; // Animation duration control
        let current = 0;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.ceil(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = element.textContent; // Keep original formatting
            }
        };

        updateCounter();
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.init();
    }

    init() {
        // Monitor Core Web Vitals
        if ('web-vital' in window) {
            this.trackWebVitals();
        }

        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => this.trackPerformanceMetrics(), 0);
        });
    }

    trackWebVitals() {
        // This would integrate with web-vitals library
        // For now, we'll use Performance Observer API
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        console.log(`${entry.name}: ${entry.startTime}`);
                    });
                });
                observer.observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint'] });
            } catch (e) {
                console.log('Performance Observer not supported');
            }
        }
    }

    trackPerformanceMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        
        if (navigation) {
            const metrics = {
                pageLoadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                timeToFirstByte: navigation.responseStart - navigation.requestStart
            };

            // Send to analytics (replace with your analytics service)
            console.log('Performance metrics:', metrics);
            
            if (typeof gtag !== 'undefined') {
                gtag('event', 'timing_complete', {
                    'name': 'page_load_time',
                    'value': Math.round(metrics.pageLoadTime)
                });
            }
        }
    }
}

// Error handling
class ErrorHandler {
    constructor() {
        this.init();
    }

    init() {
        window.addEventListener('error', (e) => {
            console.error('JavaScript error:', e.error);
            
            // Send error to analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'exception', {
                    'description': e.error.toString(),
                    'fatal': false
                });
            }
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components
    new MobileMenu();
    new HeaderScroll();
    new SmoothScroll();
    new FormHandler();
    new FloatingButton();
    new ScrollAnimations();
    new CounterAnimation();
    new PerformanceMonitor();
    new ErrorHandler();

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        .service-card, .advantage, .review, .stat {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .service-card.animate-in, .advantage.animate-in, .review.animate-in, .stat.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .form__input.invalid {
            border-color: #e74c3c !important;
            box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important;
        }
        
        .nav__toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .nav__toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .nav__toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    `;
    document.head.appendChild(style);

    // Track page view
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_TRACKING_ID', {
            page_title: document.title,
            page_location: window.location.href
        });
    }

    console.log('🚀 Service.Moscow website initialized successfully!');
});

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}