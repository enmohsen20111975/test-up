/**
 * Learning Platform Navigation
 * Handles sidebar navigation and menu interactions
 */

const Navigation = (function () {
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.querySelector('.menu-toggle');

    /**
     * Toggle mobile sidebar
     */
    function toggleMobile() {
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
    }

    /**
     * Update active navigation item
     */
    function updateActive(path) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === path ||
                item.dataset.path === path ||
                path.startsWith(item.getAttribute('href'))) {
                item.classList.add('active');
            }
        });
    }

    /**
     * Expand chapter section
     */
    function expandChapter(chapterId) {
        const chapterNav = document.querySelector(`[data-chapter="${chapterId}"]`);
        if (chapterNav) {
            const submenu = chapterNav.querySelector('.nav-submenu');
            if (submenu) {
                submenu.style.display = 'block';
            }
        }
    }

    /**
     * Scroll to element
     */
    function scrollToElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Initialize navigation events
     */
    function init() {
        // Mobile menu toggle
        if (menuToggle) {
            menuToggle.addEventListener('click', toggleMobile);
        }

        // Close sidebar on outside click (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 1024 &&
                sidebar &&
                sidebar.classList.contains('open') &&
                !sidebar.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    /**
     * Render chapter navigation
     */
    function renderChapterNav(chapterData) {
        const navHTML = `
            <div class="nav-section">
                <div class="nav-section-title">${chapterData.section}</div>
                <a href="${chapterData.path}" class="nav-item" data-path="${chapterData.path}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${chapterData.icon}
                    </svg>
                    <span>${chapterData.title}</span>
                    ${chapterData.badge ? `<span class="nav-badge">${chapterData.badge}</span>` : ''}
                </a>
                ${chapterData.lessons ? `
                    <div class="nav-submenu" style="display: none; padding-left: 2.5rem;">
                        ${chapterData.lessons.map((lesson, idx) => `
                            <a href="${lesson.path}" class="nav-item" data-path="${lesson.path}">
                                <span>${idx + 1}. ${lesson.title}</span>
                            </a>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        return navHTML;
    }

    return {
        init,
        toggleMobile,
        updateActive,
        expandChapter,
        scrollToElement,
        renderChapterNav
    };
})();

// Export
window.Navigation = Navigation;