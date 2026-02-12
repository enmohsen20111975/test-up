/**
 * ================================================
 * Shared Lesson System - JavaScript
 * EngiSuite Analytics Learning Platform
 * ================================================
 */

// Lesson State Management
const LessonState = {
    progress: 0,
    objectivesCompleted: [],
    quizAnswers: {},
    problemsSolved: [],
    bookmarked: false,
    timeSpent: 0,

    // Initialize state
    init(lessonId) {
        const saved = localStorage.getItem(`lesson_${lessonId}`);
        if (saved) {
            const data = JSON.parse(saved);
            this.progress = data.progress || 0;
            this.objectivesCompleted = data.objectivesCompleted || [];
            this.quizAnswers = data.quizAnswers || {};
            this.problemsSolved = data.problemsSolved || [];
            this.bookmarked = data.bookmarked || false;
        }
    },

    // Save state
    save(lessonId) {
        localStorage.setItem(`lesson_${lessonId}`, JSON.stringify({
            progress: this.progress,
            objectivesCompleted: this.objectivesCompleted,
            quizAnswers: this.quizAnswers,
            problemsSolved: this.problemsSolved,
            bookmarked: this.bookmarked
        }));
    },

    // Update progress
    updateProgress(lessonId, newProgress) {
        this.progress = Math.max(this.progress, newProgress);
        this.save(lessonId);
        this.renderProgress();
    },

    // Render progress ring
    renderProgress() {
        const ring = document.getElementById('progress-ring');
        const text = document.getElementById('progress-text');
        if (ring && text) {
            const circumference = 2 * Math.PI * 16;
            const offset = circumference - (this.progress / 100) * circumference;
            ring.style.strokeDashoffset = offset;
            text.textContent = `${Math.round(this.progress)}%`;
        }
    }
};

// Theme Management
const ThemeManager = {
    init() {
        const saved = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
        this.updateIcon();
    },

    toggle() {
        const current = document.documentElement.getAttribute('data-theme');
        const newTheme = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateIcon();
    },

    updateIcon() {
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            const moon = toggle.querySelector('.fa-moon');
            const sun = toggle.querySelector('.fa-sun');
            if (document.documentElement.getAttribute('data-theme') === 'dark') {
                moon?.classList.add('hidden');
                sun?.classList.remove('hidden');
            } else {
                moon?.classList.remove('hidden');
                sun?.classList.add('hidden');
            }
        }
    }
};

// Bookmark Manager
const BookmarkManager = {
    init(lessonId) {
        const btn = document.getElementById('bookmark-btn');
        if (btn) {
            btn.addEventListener('click', () => this.toggle(lessonId));
        }
    },

    toggle(lessonId) {
        LessonState.bookmarked = !LessonState.bookmarked;
        LessonState.save(lessonId);
        this.updateIcon();
    },

    updateIcon() {
        const btn = document.getElementById('bookmark-btn');
        if (btn) {
            const icon = btn.querySelector('i');
            if (LessonState.bookmarked) {
                icon?.classList.remove('far');
                icon?.classList.add('fas');
            } else {
                icon?.classList.remove('fas');
                icon?.classList.add('far');
            }
        }
    }
};

// Objectives Tracker
const ObjectivesTracker = {
    init(lessonId) {
        const checkboxes = document.querySelectorAll('#objectives-list input[type="checkbox"]');
        checkboxes.forEach((checkbox, index) => {
            const id = `obj-${index + 1}`;
            checkbox.checked = LessonState.objectivesCompleted.includes(id);

            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    if (!LessonState.objectivesCompleted.includes(id)) {
                        LessonState.objectivesCompleted.push(id);
                    }
                } else {
                    LessonState.objectivesCompleted = LessonState.objectivesCompleted.filter(obj => obj !== id);
                }
                LessonState.save(lessonId);
                this.updateProgress(lessonId, checkboxes.length);
            });
        });
    },

    updateProgress(lessonId, total) {
        const completed = LessonState.objectivesCompleted.length;
        const progress = (completed / total) * 100;
        LessonState.updateProgress(lessonId, progress);
    }
};

// Quiz Manager
const QuizManager = {
    init() {
        const quizOptions = document.querySelectorAll('.quiz-option');
        quizOptions.forEach(option => {
            option.addEventListener('click', () => this.handleAnswer(option));
        });
    },

    handleAnswer(option) {
        const questionId = option.dataset.question;
        const isCorrect = option.dataset.correct === 'true';
        const options = option.parentElement.querySelectorAll('.quiz-option');

        // Disable all options
        options.forEach(opt => {
            opt.style.pointerEvents = 'none';
            if (opt.dataset.correct === 'true') {
                opt.classList.add('correct');
            }
        });

        // Mark selected answer
        if (isCorrect) {
            option.classList.add('correct');
        } else {
            option.classList.add('incorrect');
        }

        // Show feedback
        const feedback = option.closest('.quiz-container').querySelector('.quiz-feedback');
        if (feedback) {
            feedback.classList.remove('correct', 'incorrect');
            feedback.classList.add(isCorrect ? 'correct' : 'incorrect');
        }

        // Save answer
        LessonState.quizAnswers[questionId] = isCorrect;
        LessonState.save(this.getLessonId());
    },

    getLessonId() {
        const lessonTitle = document.getElementById('lesson-title');
        return lessonTitle ? lessonTitle.textContent.trim().replace(/\s+/g, '_').toLowerCase() : 'unknown';
    }
};

// Problem Solver
const ProblemSolver = {
    init() {
        const checkButtons = document.querySelectorAll('.problem-card button');
        checkButtons.forEach(btn => {
            if (btn.textContent.includes('Check')) {
                btn.addEventListener('click', () => this.checkAnswer(btn));
            }
        });

        const solutionButtons = document.querySelectorAll('.problem-card button');
        solutionButtons.forEach(btn => {
            if (btn.textContent.includes('Show Solution')) {
                btn.addEventListener('click', () => this.toggleSolution(btn));
            }
        });
    },

    checkAnswer(btn) {
        const card = btn.closest('.problem-card');
        const input = card.querySelector('input[type="text"], input[type="number"]');
        const expectedAnswer = card.dataset.answer;
        const tolerance = parseFloat(card.dataset.tolerance) || 0.01;

        if (input && expectedAnswer) {
            const userAnswer = parseFloat(input.value);
            const expected = parseFloat(expectedAnswer);

            if (Math.abs(userAnswer - expected) <= tolerance) {
                input.classList.add('border-green-500');
                input.classList.remove('border-red-500');
                LessonState.problemsSolved.push(card.id);
            } else {
                input.classList.add('border-red-500');
                input.classList.remove('border-green-500');
            }
        }
    },

    toggleSolution(btn) {
        const card = btn.closest('.problem-card');
        const solution = card.querySelector('.solution-content');
        if (solution) {
            solution.classList.toggle('hidden');
            btn.innerHTML = solution.classList.contains('hidden')
                ? '<i class="fas fa-eye"></i> Show Solution'
                : '<i class="fas fa-eye-slash"></i> Hide Solution';
        }
    }
};

// Navigation Manager
const NavigationManager = {
    init(prevLesson, nextLesson) {
        const prevBtn = document.querySelector('.nav-btn.prev');
        const nextBtn = document.querySelector('.nav-btn.next');

        if (prevBtn) {
            if (prevLesson) {
                prevBtn.href = prevLesson;
                prevBtn.classList.remove('disabled');
            } else {
                prevBtn.classList.add('disabled');
            }
        }

        if (nextBtn) {
            if (nextLesson) {
                nextBtn.href = nextLesson;
                nextBtn.classList.remove('disabled');
            } else {
                nextBtn.classList.add('disabled');
            }
        }
    }
};

// Simulation Controller
const SimulationController = {
    canvas: null,
    ctx: null,
    animationId: null,
    electrons: [],
    isRunning: false,

    init(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.resizeCanvas();
            this.drawCircuit();

            window.addEventListener('resize', () => this.resizeCanvas());
        }

        // Control buttons
        const startBtn = document.getElementById('sim-start');
        const pauseBtn = document.getElementById('sim-pause');
        const resetBtn = document.getElementById('sim-reset');

        startBtn?.addEventListener('click', () => this.start());
        pauseBtn?.addEventListener('click', () => this.pause());
        resetBtn?.addEventListener('click', () => this.reset());
    },

    resizeCanvas() {
        if (this.canvas) {
            const container = this.canvas.parentElement;
            this.canvas.width = container.clientWidth;
            this.canvas.height = container.clientHeight || 200;
            if (!this.isRunning) {
                this.drawCircuit();
            }
        }
    },

    drawCircuit() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.clearRect(0, 0, w, h);

        // Draw circuit components
        const componentY = h / 2;
        const padding = 50;
        const componentWidth = 100;

        // Battery/Source
        this.drawBattery(ctx, padding, componentY, 30);

        // Wire from battery to first resistor
        ctx.beginPath();
        ctx.moveTo(padding + 30, componentY);
        ctx.lineTo(padding + 80, componentY);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Resistor 1
        this.drawResistor(ctx, padding + 80, componentY, componentWidth);

        // Wire between resistors
        ctx.beginPath();
        ctx.moveTo(padding + 80 + componentWidth, componentY);
        ctx.lineTo(padding + 80 + componentWidth + 40, componentY);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Resistor 2
        this.drawResistor(ctx, padding + 80 + componentWidth + 40, componentY, componentWidth);

        // Wire back to battery
        ctx.beginPath();
        ctx.moveTo(padding + 80 + (componentWidth * 2) + 40, componentY);
        ctx.lineTo(w - padding - 30, componentY);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw electrons
        this.drawElectrons();
    },

    drawBattery(ctx, x, y, size) {
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(x - 15, y - size / 2, 30, size);

        // Positive terminal
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(x - 5, y - size / 2 - 8, 10, 8);

        // Negative terminal
        ctx.fillStyle = '#94a3b8';
        ctx.fillRect(x - 5, y + size / 2, 10, 8);

        // Labels
        ctx.fillStyle = '#1e293b';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('+', x, y - size / 2 - 12);
        ctx.fillText('−', x, y + size / 2 + 20);
    },

    drawResistor(ctx, x, y, width) {
        ctx.beginPath();
        ctx.moveTo(x, y);

        // Zigzag pattern
        const zigzags = 6;
        const step = width / zigzags;
        const amplitude = 15;

        for (let i = 0; i <= zigzags; i++) {
            const px = x + i * step;
            const py = y + (i % 2 === 0 ? 0 : (i % 4 === 1 ? -amplitude : amplitude));
            if (i === zigzags) {
                ctx.lineTo(x + width, y);
            } else {
                ctx.lineTo(px, py);
            }
        }

        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();
    },

    drawElectrons() {
        const ctx = this.ctx;
        if (!ctx) return;

        this.electrons.forEach(electron => {
            ctx.beginPath();
            ctx.arc(electron.x, electron.y, 5, 0, Math.PI * 2);
            ctx.fillStyle = '#fbbf24';
            ctx.fill();
            ctx.shadowColor = '#fbbf24';
            ctx.shadowBlur = 8;
        });

        ctx.shadowBlur = 0;
    },

    initElectrons(count = 5) {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const y = h / 2;

        this.electrons = [];
        for (let i = 0; i < count; i++) {
            this.electrons.push({
                x: (w / count) * i + 50,
                y: y,
                speed: 2
            });
        }
    },

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.initElectrons(5);
        this.animate();
    },

    pause() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    },

    reset() {
        this.pause();
        this.drawCircuit();
    },

    animate() {
        if (!this.isRunning) return;

        const w = this.canvas.width;
        const h = this.canvas.height;

        // Update electron positions
        this.electrons.forEach(electron => {
            electron.x += electron.speed;
            if (electron.x > w - 50) {
                electron.x = 50;
            }
        });

        this.drawCircuit();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
};

// Time Tracker
const TimeTracker = {
    interval: null,

    start() {
        this.interval = setInterval(() => {
            LessonState.timeSpent++;
            localStorage.setItem('lesson_time', LessonState.timeSpent);
        }, 60000); // Update every minute
    },

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
};

// Initialize Lesson
function initLesson(lessonId, prevLesson = null, nextLesson = null) {
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize state
        LessonState.init(lessonId);

        // Initialize managers
        ThemeManager.init();
        BookmarkManager.init(lessonId);
        ObjectivesTracker.init(lessonId);
        QuizManager.init();
        ProblemSolver.init();
        NavigationManager.init(prevLesson, nextLesson);

        // Initialize simulation if present
        if (document.getElementById('circuit-canvas')) {
            SimulationController.init('circuit-canvas');
        }

        // Render progress
        LessonState.renderProgress();

        // Start time tracker
        TimeTracker.start();

        // Theme toggle event
        document.getElementById('theme-toggle')?.addEventListener('click', () => {
            ThemeManager.toggle();
        });

        // Objectives panel toggle
        document.getElementById('objectives-toggle')?.addEventListener('click', () => {
            const panel = document.getElementById('objectives-panel');
            const icon = document.getElementById('objectives-icon');
            panel?.classList.toggle('hidden');
            icon?.classList.toggle('rotate-180');
        });

        console.log(`Lesson "${lessonId}" initialized successfully`);
    });
}

// Export for use in lesson files
window.LessonSystem = {
    state: LessonState,
    theme: ThemeManager,
    bookmark: BookmarkManager,
    objectives: ObjectivesTracker,
    quiz: QuizManager,
    problems: ProblemSolver,
    navigation: NavigationManager,
    simulation: SimulationController,
    time: TimeTracker,
    init: initLesson
};