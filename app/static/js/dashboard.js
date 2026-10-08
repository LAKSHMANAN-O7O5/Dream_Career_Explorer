// --- Dashboard Analytics & Animations JS ---

document.addEventListener('DOMContentLoaded', () => {
    // 1. Animate SVG Circular Progress Rings
    const rings = document.querySelectorAll('.progress-ring-circle');
    
    rings.forEach(circle => {
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        
        // Set initial dash properties
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;
        
        // Extract progress percentage from parent container
        const pctContainer = circle.closest('.progress-ring-container');
        if (pctContainer) {
            const pct = parseInt(pctContainer.getAttribute('data-pct')) || 0;
            const offset = circumference - (pct / 100) * circumference;
            
            // Animate transition offset
            setTimeout(() => {
                circle.style.strokeDashoffset = offset;
            }, 300);
        }
    });

    // 2. Chart.js Config: Student Dashboard
    
    // Core color theme colors matching styles.css (deep purple/indigo neon)
    const primaryColor = '#6366f1';
    const primaryGlow = 'rgba(99, 102, 241, 0.2)';
    const accentColor = '#10b981';
    const accentGlow = 'rgba(16, 185, 129, 0.2)';
    const warningColor = '#f59e0b';
    const gridColor = 'rgba(255, 255, 255, 0.05)';
    const textColor = '#9ca3af';

    // Skill Profile Radar Chart
    const skillsCanvas = document.getElementById('skillsRadarChart');
    if (skillsCanvas) {
        const labels = JSON.parse(skillsCanvas.getAttribute('data-labels') || '[]');
        const values = JSON.parse(skillsCanvas.getAttribute('data-values') || '[]');
        
        new Chart(skillsCanvas, {
            type: 'radar',
            data: {
                labels: labels.length ? labels : ['Technical', 'Creative', 'Logical', 'Business', 'Communication'],
                datasets: [{
                    label: 'Proficiency Level',
                    data: values.length ? values : [50, 50, 50, 50, 50],
                    backgroundColor: primaryGlow,
                    borderColor: primaryColor,
                    pointBackgroundColor: primaryColor,
                    pointBorderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    r: {
                        grid: { color: gridColor },
                        angleLines: { color: gridColor },
                        pointLabels: { color: textColor, font: { family: 'Outfit', size: 12 } },
                        ticks: { display: false, stepSize: 20 },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    // Career Matches Compatibility Pie Chart
    const matchesCanvas = document.getElementById('careerMatchesPieChart');
    if (matchesCanvas) {
        const labels = JSON.parse(matchesCanvas.getAttribute('data-labels') || '[]');
        const values = JSON.parse(matchesCanvas.getAttribute('data-values') || '[]');
        
        new Chart(matchesCanvas, {
            type: 'polarArea',
            data: {
                labels: labels.length ? labels : ['No Assessment Completed'],
                datasets: [{
                    data: values.length ? values : [100],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',  // Indigo
                        'rgba(16, 185, 129, 0.7)',  // Emerald
                        'rgba(6, 182, 212, 0.7)',   // Cyan
                        'rgba(245, 158, 11, 0.7)',  // Amber
                        'rgba(239, 68, 68, 0.7)'    // Rose
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Outfit' } }
                    }
                },
                scales: {
                    r: {
                        grid: { color: gridColor },
                        ticks: { display: false }
                    }
                }
            }
        });
    }
    
    // Roadmap completion progress bar
    const roadmapProgressBar = document.querySelector('.progress-bar[data-width]');

    if (roadmapProgressBar) {
        const width = roadmapProgressBar.getAttribute('data-width');
        roadmapProgressBar.style.width = width + '%';
    }

});
