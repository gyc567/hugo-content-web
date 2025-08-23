// SuperCopyCoder - Main JavaScript

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger menu
            const spans = navToggle.querySelectorAll('span');
            spans.forEach((span, index) => {
                if (navMenu.classList.contains('active')) {
                    if (index === 0) span.style.transform = 'rotate(45deg) translate(5px, 5px)';
                    if (index === 1) span.style.opacity = '0';
                    if (index === 2) span.style.transform = 'rotate(-45deg) translate(7px, -6px)';
                } else {
                    span.style.transform = '';
                    span.style.opacity = '';
                }
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                
                const spans = navToggle.querySelectorAll('span');
                spans.forEach(span => {
                    span.style.transform = '';
                    span.style.opacity = '';
                });
            }
        });
    }
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Image lazy loading enhancement
document.addEventListener('DOMContentLoaded', function() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Add fade-in effect
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.3s ease';
                    
                    img.onload = function() {
                        img.style.opacity = '1';
                    };
                    
                    // If image is already loaded
                    if (img.complete) {
                        img.style.opacity = '1';
                    }
                    
                    observer.unobserve(img);
                }
            });
        });
        
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => imageObserver.observe(img));
    }
});

// Reading progress indicator
document.addEventListener('DOMContentLoaded', function() {
    const article = document.querySelector('.post-single .post-content');
    
    if (article) {
        // Create progress bar
        const progressBar = document.createElement('div');
        progressBar.id = 'reading-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: var(--primary-color);
            z-index: 1001;
            transition: width 0.1s ease;
        `;
        document.body.appendChild(progressBar);
        
        // Update progress on scroll
        function updateProgress() {
            const articleTop = article.offsetTop;
            const articleHeight = article.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollTop = window.pageYOffset;
            
            const articleStart = articleTop - windowHeight * 0.2;
            const articleEnd = articleTop + articleHeight;
            
            if (scrollTop >= articleStart && scrollTop <= articleEnd) {
                const progress = ((scrollTop - articleStart) / (articleEnd - articleStart)) * 100;
                progressBar.style.width = Math.min(Math.max(progress, 0), 100) + '%';
            } else if (scrollTop < articleStart) {
                progressBar.style.width = '0%';
            } else {
                progressBar.style.width = '100%';
            }
        }
        
        window.addEventListener('scroll', updateProgress);
        updateProgress(); // Initial call
    }
});

// Copy code blocks functionality
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(codeBlock => {
        const pre = codeBlock.parentElement;
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-code-button';
        copyButton.textContent = 'Copy';
        copyButton.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s ease;
        `;
        
        // Position pre relatively
        pre.style.position = 'relative';
        
        // Show button on hover
        pre.addEventListener('mouseenter', () => {
            copyButton.style.opacity = '1';
        });
        
        pre.addEventListener('mouseleave', () => {
            copyButton.style.opacity = '0';
        });
        
        // Copy functionality
        copyButton.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                copyButton.textContent = 'Copied!';
                copyButton.style.background = 'var(--success-color)';
                copyButton.style.color = 'white';
                
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                    copyButton.style.background = 'rgba(255, 255, 255, 0.9)';
                    copyButton.style.color = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
                copyButton.textContent = 'Failed';
            }
        });
        
        pre.appendChild(copyButton);
    });
});

// External link handling
document.addEventListener('DOMContentLoaded', function() {
    const externalLinks = document.querySelectorAll('a[href^="http"]:not([href*="' + location.hostname + '"])');
    
    externalLinks.forEach(link => {
        // Add external link indicator
        if (!link.querySelector('.external-icon')) {
            const icon = document.createElement('span');
            icon.className = 'external-icon';
            icon.innerHTML = ' ↗';
            icon.style.fontSize = '0.8em';
            link.appendChild(icon);
        }
        
        // Open in new tab
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });
});

// Table of contents generation for long articles
document.addEventListener('DOMContentLoaded', function() {
    const article = document.querySelector('.post-content');
    const headings = article ? article.querySelectorAll('h2, h3, h4') : [];
    
    if (headings.length >= 3) {
        const toc = document.createElement('div');
        toc.className = 'table-of-contents';
        toc.innerHTML = '<h4>Table of Contents</h4>';
        
        const tocList = document.createElement('ul');
        toc.appendChild(tocList);
        
        headings.forEach((heading, index) => {
            // Generate ID if not exists
            if (!heading.id) {
                heading.id = 'heading-' + index;
            }
            
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#' + heading.id;
            a.textContent = heading.textContent;
            a.className = 'toc-link toc-' + heading.tagName.toLowerCase();
            
            li.appendChild(a);
            tocList.appendChild(li);
        });
        
        // Style the TOC
        toc.style.cssText = `
            background: var(--bg-light);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            margin: 2rem 0;
        `;
        
        // Insert TOC after first paragraph
        const firstParagraph = article.querySelector('p');
        if (firstParagraph) {
            firstParagraph.parentNode.insertBefore(toc, firstParagraph.nextSibling);
        }
    }
});

// Performance and analytics
document.addEventListener('DOMContentLoaded', function() {
    // Simple page view tracking
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_view', {
            page_title: document.title,
            page_location: window.location.href
        });
    }
    
    // Track time on page
    let startTime = Date.now();
    
    window.addEventListener('beforeunload', function() {
        const timeOnPage = Math.round((Date.now() - startTime) / 1000);
        
        if (typeof gtag !== 'undefined' && timeOnPage > 10) {
            gtag('event', 'timing_complete', {
                name: 'time_on_page',
                value: timeOnPage
            });
        }
    });
});

// Utility functions
window.HugoContentWeb = {
    // Utility to get all like stats
    getLikeStats: function() {
        if (window.likesManager) {
            return window.likesManager.getStats();
        }
        return null;
    },
    
    // Utility to export user data
    exportUserData: function() {
        const data = {};
        
        if (window.likesManager) {
            data.likes = window.likesManager.exportData();
        }
        
        return data;
    },
    
    // Utility to import user data
    importUserData: function(data) {
        if (data.likes && window.likesManager) {
            window.likesManager.importData(data.likes);
        }
    },
    
    // Theme toggle (for future dark mode implementation)
    toggleTheme: function() {
        document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    }
};