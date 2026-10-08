// --- Main Global JavaScript ---

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark / Light Mode Toggle
    const themeToggle = document.getElementById('theme-toggle-btn');
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            let activeTheme = document.documentElement.getAttribute('data-theme');
            let newTheme = activeTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        const icon = document.querySelector('#theme-toggle-btn i');
        if (icon) {
            if (theme === 'light') {
                icon.className = 'fas fa-moon';
            } else {
                icon.className = 'fas fa-sun';
            }
        }
    }

    // 2. Active Sidebar Highlights
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.side-nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });

    // 3. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }

    // 4. Auto-dismiss Alert Flashes after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Bootstrap fade out animation
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 4000);
    });
});

const slider = document.getElementById("skillSlider");
const value = document.getElementById("skillValue");

if (slider && value) {

    value.textContent = slider.value + "%";

    slider.addEventListener("input", function () {
        value.textContent = this.value + "%";
    });

}