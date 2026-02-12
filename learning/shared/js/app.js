/**
 * Electrical Engineering Learning Platform - Main Application
 * Initializes all modules and handles global functionality
 */

(function () {
    'use strict';

    /**
     * Course Data - Navigation Structure
     */
    const courseData = {
        chapters: [
            {
                id: '01-fundamentals',
                title: 'Fundamentals of Electricity',
                section: 'Foundation',
                path: 'chapters/01-fundamentals/index.html',
                lessons: [
                    { id: '01-01', title: 'Atomic Structure & Electric Charge', path: 'chapters/01-fundamentals/01-atomic-structure.html', duration: '45 min' },
                    { id: '01-02', title: 'Voltage, Current & Resistance', path: 'chapters/01-fundamentals/02-voltage-current-resistance.html', duration: '60 min' },
                    { id: '01-03', title: 'Ohm\'s Law & Power', path: 'chapters/01-fundamentals/03-ohms-law-power.html', duration: '60 min' },
                    { id: '01-04', title: 'Series Circuits', path: 'chapters/01-fundamentals/04-series-circuits.html', duration: '50 min' },
                    { id: '01-05', title: 'Parallel Circuits', path: 'chapters/01-fundamentals/05-parallel-circuits.html', duration: '50 min' },
                    { id: '01-06', title: 'Series-Parallel Circuits', path: 'chapters/01-fundamentals/06-series-parallel-circuits.html', duration: '60 min' }
                ]
            },
            {
                id: '02-circuit-analysis',
                title: 'Circuit Analysis',
                section: 'Foundation',
                path: 'chapters/02-circuit-analysis/index.html',
                lessons: [
                    { id: '02-01', title: 'Kirchhoff\'s Current Law (KCL)', path: 'chapters/02-circuit-analysis/01-kirchhoffs-current-law.html', duration: '55 min' },
                    { id: '02-02', title: 'Kirchhoff\'s Voltage Law (KVL)', path: 'chapters/02-circuit-analysis/02-kirchhoffs-voltage-law.html', duration: '55 min' },
                    { id: '02-03', title: 'Nodal Analysis', path: 'chapters/02-circuit-analysis/03-nodal-analysis.html', duration: '60 min' },
                    { id: '02-04', title: 'Mesh Analysis', path: 'chapters/02-circuit-analysis/04-mesh-analysis.html', duration: '60 min' },
                    { id: '02-05', title: 'Thevenin\'s Theorem', path: 'chapters/02-circuit-analysis/05-thevenin-theorem.html', duration: '60 min' },
                    { id: '02-06', title: 'Norton\'s Theorem', path: 'chapters/02-circuit-analysis/06-norton-theorem.html', duration: '50 min' }
                ]
            },
            {
                id: '03-power-systems',
                title: 'Power Systems',
                section: 'Core Specialization',
                path: 'chapters/03-power-systems/index.html',
                lessons: [
                    { id: '03-01', title: 'Power Generation Fundamentals', path: 'chapters/03-power-systems/01-power-generation.html', duration: '55 min' },
                    { id: '03-02', title: 'Transmission Systems', path: 'chapters/03-power-systems/02-transmission-systems.html', duration: '60 min' },
                    { id: '03-03', title: 'Distribution Networks', path: 'chapters/03-power-systems/03-distribution-networks.html', duration: '50 min' },
                    { id: '03-04', title: 'Three-Phase Systems', path: 'chapters/03-power-systems/04-three-phase-systems.html', duration: '65 min' },
                    { id: '03-05', title: 'Transformers', path: 'chapters/03-power-systems/05-transformers.html', duration: '60 min' }
                ]
            },
            {
                id: '04-electronics',
                title: 'Electronics',
                section: 'Core Specialization',
                path: 'chapters/04-electronics/index.html',
                lessons: [
                    { id: '04-01', title: 'Semiconductor Physics', path: 'chapters/04-electronics/01-semiconductor-physics.html', duration: '55 min' },
                    { id: '04-02', title: 'Diodes & Applications', path: 'chapters/04-electronics/02-diodes-applications.html', duration: '60 min' },
                    { id: '04-03', title: 'Bipolar Junction Transistors', path: 'chapters/04-electronics/03-bjt.html', duration: '65 min' },
                    { id: '04-04', title: 'MOSFETs', path: 'chapters/04-electronics/04-mosfets.html', duration: '60 min' },
                    { id: '04-05', title: 'Operational Amplifiers', path: 'chapters/04-electronics/05-opamps.html', duration: '65 min' },
                    { id: '04-06', title: 'Oscillators & Timers', path: 'chapters/04-electronics/06-oscillators-timers.html', duration: '55 min' }
                ]
            },
            {
                id: '05-digital-electronics',
                title: 'Digital Electronics',
                section: 'Core Specialization',
                path: 'chapters/05-digital-electronics/index.html',
                lessons: [
                    { id: '05-01', title: 'Number Systems & Binary', path: 'chapters/05-digital-electronics/01-number-systems.html', duration: '50 min' },
                    { id: '05-02', title: 'Logic Gates', path: 'chapters/05-digital-electronics/02-logic-gates.html', duration: '55 min' },
                    { id: '05-03', title: 'Boolean Algebra', path: 'chapters/05-digital-electronics/03-boolean-algebra.html', duration: '60 min' },
                    { id: '05-04', title: 'Combinational Circuits', path: 'chapters/05-digital-electronics/04-combinational-circuits.html', duration: '60 min' },
                    { id: '05-05', title: 'Sequential Circuits', path: 'chapters/05-digital-electronics/05-sequential-circuits.html', duration: '65 min' }
                ]
            },
            {
                id: '06-electrical-machines',
                title: 'Electrical Machines',
                section: 'Core Specialization',
                path: 'chapters/06-electrical-machines/index.html',
                lessons: [
                    { id: '06-01', title: 'DC Motors', path: 'chapters/06-electrical-machines/01-dc-motors.html', duration: '60 min' },
                    { id: '06-02', title: 'DC Generators', path: 'chapters/06-electrical-machines/02-dc-generators.html', duration: '55 min' },
                    { id: '06-03', title: 'AC Motors', path: 'chapters/06-electrical-machines/03-ac-motors.html', duration: '65 min' },
                    { id: '06-04', title: 'Synchronous Machines', path: 'chapters/06-electrical-machines/04-synchronous-machines.html', duration: '60 min' },
                    { id: '06-05', title: 'Induction Motors', path: 'chapters/06-electrical-machines/05-induction-motors.html', duration: '65 min' }
                ]
            },
            {
                id: '07-control-systems',
                title: 'Control Systems',
                section: 'Advanced Topics',
                path: 'chapters/07-control-systems/index.html',
                lessons: [
                    { id: '07-01', title: 'Control Systems Fundamentals', path: 'chapters/07-control-systems/01-fundamentals.html', duration: '55 min' },
                    { id: '07-02', title: 'Block Diagrams', path: 'chapters/07-control-systems/02-block-diagrams.html', duration: '50 min' },
                    { id: '07-03', title: 'PID Controllers', path: 'chapters/07-control-systems/03-pid-controllers.html', duration: '60 min' },
                    { id: '07-04', title: 'Stability Analysis', path: 'chapters/07-control-systems/04-stability-analysis.html', duration: '55 min' }
                ]
            },
            {
                id: '08-renewable-energy',
                title: 'Renewable Energy',
                section: 'Advanced Topics',
                path: 'chapters/08-renewable-energy/index.html',
                lessons: [
                    { id: '08-01', title: 'Solar Energy Systems', path: 'chapters/08-renewable-energy/01-solar-energy.html', duration: '60 min' },
                    { id: '08-02', title: 'Wind Energy Systems', path: 'chapters/08-renewable-energy/02-wind-energy.html', duration: '55 min' },
                    { id: '08-03', title: 'Energy Storage Systems', path: 'chapters/08-renewable-energy/03-energy-storage.html', duration: '50 min' },
                    { id: '08-04', title: 'Grid Integration', path: 'chapters/08-renewable-energy/04-grid-integration.html', duration: '55 min' }
                ]
            },
            {
                id: '09-safety-standards',
                title: 'Safety & Standards',
                section: 'Professional Skills',
                path: 'chapters/09-safety-standards/index.html',
                lessons: [
                    { id: '09-01', title: 'Electrical Hazard Recognition', path: 'chapters/09-safety-standards/01-hazard-recognition.html', duration: '45 min' },
                    { id: '09-02', title: 'Personal Protective Equipment', path: 'chapters/09-safety-standards/02-ppe.html', duration: '40 min' },
                    { id: '09-03', title: 'Lockout/Tagout Procedures', path: 'chapters/09-safety-standards/03-loto.html', duration: '50 min' },
                    { id: '09-04', title: 'Electrical Codes & Standards', path: 'chapters/09-safety-standards/04-codes-standards.html', duration: '55 min' }
                ]
            }
        ]
    };

    /**
     * Render sidebar navigation
     */
    function renderNavigation() {
        const navContainer = document.getElementById('sidebarNav');
        if (!navContainer) return;

        let html = '';
        let currentSection = '';

        courseData.chapters.forEach((chapter, index) => {
            if (chapter.section !== currentSection) {
                currentSection = chapter.section;
                html += `<div class="nav-section-title">${currentSection}</div>`;
            }

            html += `
                <a href="${chapter.path}" class="nav-item" data-path="${chapter.path}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${getChapterIcon(index)}
                    </svg>
                    <span>${chapter.title}</span>
                    ${chapter.lessons ? `<span class="nav-badge">${chapter.lessons.length}</span>` : ''}
                </a>
            `;

            if (chapter.lessons) {
                html += `<div class="nav-submenu" style="display: none; padding-left: 2.5rem;">`;
                chapter.lessons.forEach((lesson, lessonIndex) => {
                    html += `
                        <a href="${lesson.path}" class="nav-item" data-path="${lesson.path}">
                            <span>${lessonIndex + 1}. ${lesson.title}</span>
                        </a>
                    `;
                });
                html += `</div>`;
            }
        });

        navContainer.innerHTML = html;

        // Add click handlers for expanding chapters
        navContainer.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', function (e) {
                const submenu = this.nextElementSibling;
                if (submenu && submenu.classList.contains('nav-submenu')) {
                    submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
                }
            });
        });
    }

    /**
     * Get icon SVG for chapter
     */
    function getChapterIcon(index) {
        const icons = [
            // Fundamentals
            '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
            // Circuit Analysis
            '<rect x="4" y="4" width="16" height="16"/><path d="M9 9h6v6H9z"/>',
            // Power Systems
            '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
            // Electronics
            '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6v6H9z"/>',
            // Digital Electronics
            '<rect x="2" y="3" width="20" height="14" rx="2"/><circle cx="8" cy="14" r="2"/><circle cx="16" cy="14" r="2"/>',
            // Electrical Machines
            '<circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83"/>',
            // Control Systems
            '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
            // Renewable Energy
            '<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42"/>',
            // Safety
            '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        ];
        return icons[index % icons.length];
    }

    /**
     * Update progress display
     */
    function updateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        if (progressFill && progressText) {
            const totalLessons = courseData.chapters.reduce((sum, ch) => sum + (ch.lessons?.length || 0), 0);
            State.setTotalLessons(totalLessons);
            const progress = State.get('progress.totalProgress');
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${progress}% Complete`;
        }
    }

    /**
     * Initialize theme toggle
     */
    function initThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;

        let isDark = true;

        themeToggle.addEventListener('click', () => {
            isDark = !isDark;
            document.body.classList.toggle('dark', isDark);
            State.updatePreference('theme', isDark ? 'dark' : 'light');
        });
    }

    /**
     * Initialize bookmarks
     */
    function initBookmarks() {
        const bookmarksBtn = document.getElementById('bookmarksBtn');
        if (!bookmarksBtn) return;

        bookmarksBtn.addEventListener('click', () => {
            const bookmarks = State.getBookmarks();
            if (bookmarks.length === 0) {
                alert('No bookmarks yet. Navigate to a lesson and bookmark it!');
            } else {
                const list = bookmarks.map(b => `• ${b.title}`).join('\n');
                alert(`Your Bookmarks:\n\n${list}`);
            }
        });
    }

    /**
     * Mobile menu toggle
     */
    function initMobileMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');

        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }
    }

    /**
     * Complete current lesson
     */
    function markLessonComplete(lessonId) {
        State.completeLesson(lessonId);
        updateProgress();
    }

    /**
     * Add lesson completion button
     */
    function addCompletionButton() {
        const contentBody = document.querySelector('.content-body');
        if (!contentBody) return;

        // Check if button already exists
        if (document.getElementById('completeBtn')) return;

        const btn = document.createElement('button');
        btn.id = 'completeBtn';
        btn.className = 'btn btn-primary fixed bottom-6 right-6 z-50 shadow-lg';
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            Mark Complete
        `;

        btn.addEventListener('click', () => {
            const path = window.location.pathname;
            const lessonId = path.split('/').pop().replace('.html', '');
            markLessonComplete(lessonId);
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                Completed!
            `;
            btn.classList.remove('btn-primary');
            btn.classList.add('bg-emerald-600');
        });

        contentBody.appendChild(btn);
    }

    /**
     * Initialize the application
     */
    function init() {
        // Initialize state
        State.init();

        // Render navigation
        renderNavigation();

        // Update progress
        updateProgress();

        // Initialize UI components
        initThemeToggle();
        initBookmarks();
        initMobileMenu();

        // Add completion button on lesson pages
        if (document.querySelector('.article-content')) {
            addCompletionButton();
        }

        console.log('Electrical Engineering Learning Platform initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export for use
    window.courseData = courseData;
    window.markLessonComplete = markLessonComplete;
})();