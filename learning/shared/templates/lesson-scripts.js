/**
 * Lesson Template - JavaScript Logic
 * EngiSuite Analytics Learning Platform
 * 
 * Handles:
 * - Data loading from JSON files
 * - Interactive simulations
 * - Practice problem checking
 * - Progress tracking
 * - State management
 */

(function () {
    'use strict';

    // ================================================
    // CONFIGURATION
    // ================================================

    const CONFIG = {
        DATA_PATH: '../data/',
        STORAGE_KEY: 'engisuite_lesson_progress',
        ANIMATION_DURATION: 300,
        SIMULATION_FPS: 60
    };

    // ================================================
    // STATE MANAGEMENT
    // ================================================

    const LessonState = {
        currentLesson: null,
        currentDiscipline: null,
        progress: 0,
        objectivesCompleted: [],
        simulationsState: {},
        answersChecked: {},

        /**
         * Load state from localStorage
         */
        load() {
            try {
                const stored = localStorage.getItem(CONFIG.STORAGE_KEY);
                if (stored) {
                    const data = JSON.parse(stored);
                    this.progress = data.progress || 0;
                    this.objectivesCompleted = data.objectivesCompleted || [];
                    this.answersChecked = data.answersChecked || {};
                }
            } catch (e) {
                console.warn('Failed to load lesson state:', e);
            }
        },

        /**
         * Save state to localStorage
         */
        save() {
            try {
                localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify({
                    progress: this.progress,
                    objectivesCompleted: this.objectivesCompleted,
                    answersChecked: this.answersChecked
                }));
            } catch (e) {
                console.warn('Failed to save lesson state:', e);
            }
        },

        /**
         * Update objective completion status
         */
        setObjectiveCompleted(index, completed) {
            if (completed) {
                if (!this.objectivesCompleted.includes(index)) {
                    this.objectivesCompleted.push(index);
                }
            } else {
                this.objectivesCompleted = this.objectivesCompleted.filter(i => i !== index);
            }
            this.updateProgress();
            this.save();
        },

        /**
         * Calculate and update progress
         */
        updateProgress() {
            if (!this.currentLesson || !this.currentLesson.objectives) return;

            const total = this.currentLesson.objectives.length;
            const completed = this.objectivesCompleted.length;
            this.progress = Math.round((completed / total) * 100);

            this.updateProgressUI();
        },

        /**
         * Update progress ring UI
         */
        updateProgressUI() {
            const progressRing = document.getElementById('progress-ring');
            const progressText = document.getElementById('progress-text');

            if (progressRing) {
                const circumference = 2 * Math.PI * 18; // radius = 18
                const offset = circumference - (this.progress / 100) * circumference;
                progressRing.style.strokeDashoffset = offset;
            }

            if (progressText) {
                progressText.textContent = `${this.progress}%`;
            }
        }
    };

    // ================================================
    // DATA LOADING
    // ================================================

    const DataLoader = {
        /**
         * Load lesson data from JSON file
         */
        async loadLessonData(discipline, lessonId) {
            try {
                const response = await fetch(`${CONFIG.DATA_PATH}${discipline}/courses.json`);
                if (!response.ok) {
                    throw new Error(`Failed to load ${discipline} courses`);
                }

                const data = await response.json();

                // Find the specific lesson
                for (const chapter of data.chapters) {
                    const lesson = chapter.lessons.find(l => l.id === lessonId);
                    if (lesson) {
                        lesson.chapterName = chapter.title;
                        return lesson;
                    }
                }

                throw new Error(`Lesson ${lessonId} not found`);
            } catch (error) {
                console.error('Error loading lesson data:', error);
                showToast('Failed to load lesson content', 'error');
                return null;
            }
        },

        /**
         * Render lesson content
         */
        renderLesson(lesson) {
            LessonState.currentLesson = lesson;

            // Update header
            document.getElementById('lesson-title').textContent = lesson.title;
            document.getElementById('lesson-duration').textContent = lesson.duration;
            document.getElementById('lesson-level').textContent = lesson.level;
            document.getElementById('lesson-type').textContent = lesson.type;
            document.getElementById('breadcrumb-chapter').textContent = lesson.chapterName;
            document.getElementById('breadcrumb-lesson').textContent = lesson.title;

            // Update breadcrumb
            const breadcrumbs = document.querySelectorAll('.breadcrumb-item');

            // Render objectives
            this.renderObjectives(lesson.objectives);

            // Render navigation sections
            this.renderNavigation(lesson);

            // Render content sections
            this.renderContent(lesson);

            // Initialize MathJax if available
            if (window.MathJax) {
                MathJax.typesetPromise();
            }

            // Load saved state
            LessonState.load();
            LessonState.updateProgressUI();
            this.restoreObjectiveStates();
        },

        /**
         * Render learning objectives
         */
        renderObjectives(objectives) {
            const container = document.getElementById('objectives-list');
            if (!container) return;

            container.innerHTML = objectives.map((obj, index) => `
                <li class="flex items-start gap-2">
                    <input type="checkbox" id="obj-${index}"
                        class="mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                        onchange="LessonTemplate.updateObjective(${index}, this.checked)">
                    <label for="obj-${index}" class="text-gray-700 dark:text-gray-300 cursor-pointer">${obj}</label>
                </li>
            `).join('');
        },

        /**
         * Render lesson navigation
         */
        renderNavigation(lesson) {
            const navContainer = document.getElementById('lesson-nav');
            if (!navContainer) return;

            const sections = [];

            if (lesson.content && lesson.content.sections) {
                sections.push({ id: 'theory-section', title: 'Theory', icon: 'fas fa-book-open' });
            }

            if (lesson.simulations && lesson.simulations.length > 0) {
                sections.push({ id: 'simulation-section', title: 'Simulation', icon: 'fas fa-flask' });
            }

            if (lesson.problems && lesson.problems.length > 0) {
                sections.push({ id: 'practice-section', title: 'Practice', icon: 'fas fa-pencil-alt' });
            }

            if (lesson.takeaways) {
                sections.push({ id: 'takeaway-section', title: 'Summary', icon: 'fas fa-star' });
            }

            navContainer.innerHTML = sections.map(section => `
                <a href="#${section.id}"
                    class="nav-link flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
                    data-section="${section.id}">
                    <i class="${section.icon} text-primary-600 w-5"></i>${section.title}
                </a>
            `).join('');
        },

        /**
         * Render main content sections
         */
        renderContent(lesson) {
            // Theory content is rendered by template engine
            // Additional dynamic content can be added here
        },

        /**
         * Restore saved objective states
         */
        restoreObjectiveStates() {
            LessonState.objectivesCompleted.forEach(index => {
                const checkbox = document.getElementById(`obj-${index}`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    };

    // ================================================
    // SIMULATION CONTROLLER
    // ================================================

    const SimulationController = {
        activeSimulations: {},
        animationFrames: {},

        /**
         * Initialize a simulation
         */
        init(simulationType, canvasId, config) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.error(`Canvas ${canvasId} not found`);
                return;
            }

            const ctx = canvas.getContext('2d');

            this.activeSimulations[simulationType] = {
                canvas,
                ctx,
                config,
                running: false,
                paused: false,
                values: {}
            };

            // Initialize default values
            if (config.controls) {
                config.controls.forEach(control => {
                    this.activeSimulations[simulationType].values[control.id] = control.defaultValue;
                });
            }

            // Draw initial state
            this.draw(simulationType);

            // Hide placeholder
            const placeholder = document.getElementById(`${canvasId}-placeholder`);
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        },

        /**
         * Update simulation parameter
         */
        updateParam(simulationType, controlId, value) {
            const sim = this.activeSimulations[simulationType];
            if (!sim) return;

            sim.values[controlId] = parseFloat(value);

            // Update display value
            const valueDisplay = document.getElementById(`${controlId}-val`);
            if (valueDisplay) {
                valueDisplay.textContent = value;
            }

            // Redraw
            this.draw(simulationType);
        },

        /**
         * Start simulation
         */
        start(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim || sim.running) return;

            sim.running = true;
            sim.paused = false;
            this.animate(simulationType);
        },

        /**
         * Pause simulation
         */
        pause(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim) return;

            sim.paused = true;
            if (this.animationFrames[simulationType]) {
                cancelAnimationFrame(this.animationFrames[simulationType]);
            }
        },

        /**
         * Reset simulation
         */
        reset(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim) return;

            sim.running = false;
            sim.paused = false;

            if (this.animationFrames[simulationType]) {
                cancelAnimationFrame(this.animationFrames[simulationType]);
            }

            // Reset to default values
            if (sim.config.controls) {
                sim.config.controls.forEach(control => {
                    sim.values[control.id] = control.defaultValue;

                    const input = document.getElementById(control.id);
                    const valueDisplay = document.getElementById(control.valueId);

                    if (input) input.value = control.defaultValue;
                    if (valueDisplay) valueDisplay.textContent = control.defaultValue;
                });
            }

            this.draw(simulationType);
        },

        /**
         * Animation loop
         */
        animate(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim || !sim.running || sim.paused) return;

            this.draw(simulationType);
            this.updateResults(simulationType);

            this.animationFrames[simulationType] = requestAnimationFrame(() => {
                this.animate(simulationType);
            });
        },

        /**
         * Draw simulation
         */
        draw(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim) return;

            const { canvas, ctx, config, values } = sim;

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw based on simulation type
            switch (simulationType) {
                case 'vector-addition':
                    this.drawVectorAddition(sim);
                    break;
                case 'ohms-law':
                    this.drawOhmsLaw(sim);
                    break;
                case 'series-circuit':
                    this.drawSeriesCircuit(sim);
                    break;
                case 'parallel-circuit':
                    this.drawParallelCircuit(sim);
                    break;
                default:
                    this.drawDefault(sim);
            }
        },

        /**
         * Draw vector addition simulation
         */
        drawVectorAddition(sim) {
            const { ctx, canvas, values } = sim;
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            // Get force values
            const f1Mag = values['f1-mag'] || 50;
            const f1Angle = (values['f1-angle'] || 0) * Math.PI / 180;
            const f2Mag = values['f2-mag'] || 50;
            const f2Angle = (values['f2-angle'] || 90) * Math.PI / 180;

            // Scale factor
            const scale = 1.5;

            // Draw grid
            this.drawGrid(ctx, canvas);

            // Draw vectors
            this.drawArrow(ctx, centerX, centerY,
                centerX + f1Mag * scale * Math.cos(f1Angle),
                centerY - f1Mag * scale * Math.sin(f1Angle),
                '#3b82f6', 'F1');

            this.drawArrow(ctx, centerX, centerY,
                centerX + f2Mag * scale * Math.cos(f2Angle),
                centerY - f2Mag * scale * Math.sin(f2Angle),
                '#22c55e', 'F2');

            // Calculate and draw resultant
            const rx = f1Mag * Math.cos(f1Angle) + f2Mag * Math.cos(f2Angle);
            const ry = -(f1Mag * Math.sin(f1Angle) + f2Mag * Math.sin(f2Angle));
            const rMag = Math.sqrt(rx * rx + ry * ry);
            const rAngle = Math.atan2(-ry, rx) * 180 / Math.PI;

            this.drawArrow(ctx, centerX, centerY,
                centerX + rx * scale,
                centerY + ry * scale,
                '#ef4444', 'R');

            // Update results display
            document.getElementById('rx-result').textContent = `${rx.toFixed(1)} N`;
            document.getElementById('ry-result').textContent = `${ry.toFixed(1)} N`;
            document.getElementById('rmag-result').textContent = `${rMag.toFixed(1)} N`;
            document.getElementById('rangle-result').textContent = `${rAngle.toFixed(1)}°`;
        },

        /**
         * Draw Ohm's law simulation
         */
        drawOhmsLaw(sim) {
            const { ctx, canvas, values } = sim;
            const voltage = values['voltage'] || 12;
            const resistance = values['resistance'] || 100;
            const current = voltage / resistance;

            // Draw circuit
            this.drawGrid(ctx, canvas);

            // Draw battery
            this.drawBattery(ctx, 100, canvas.height / 2, voltage);

            // Draw resistor
            this.drawResistor(ctx, 400, canvas.height / 2, resistance);

            // Draw ammeter
            this.drawAmmeter(ctx, 250, canvas.height / 2 - 80, current);

            // Draw voltmeter
            this.drawVoltmeter(ctx, 400, canvas.height / 2 - 80, voltage);

            // Update results
            document.getElementById('current-result').textContent = `${(current * 1000).toFixed(1)} mA`;
            document.getElementById('voltage-result').textContent = `${voltage.toFixed(1)} V`;
            document.getElementById('resistance-result').textContent = `${resistance.toFixed(0)} Ω`;
            document.getElementById('power-result').textContent = `${(voltage * current).toFixed(2)} W`;
        },

        /**
         * Draw series circuit
         */
        drawSeriesCircuit(sim) {
            const { ctx, canvas, values } = sim;
            const r1 = values['r1'] || 100;
            const r2 = values['r2'] || 200;
            const voltage = values['voltage'] || 12;

            const totalR = r1 + r2;
            const current = voltage / totalR;
            const v1 = current * r1;
            const v2 = current * r2;

            this.drawGrid(ctx, canvas);

            // Draw voltage source
            this.drawBattery(ctx, 100, canvas.height / 2, voltage);

            // Draw resistors in series
            this.drawResistor(ctx, 300, canvas.height / 2, r1);
            this.drawResistor(ctx, 500, canvas.height / 2, r2);

            // Draw ammeters
            this.drawAmmeter(ctx, 200, canvas.height / 2 - 80, current);
            this.drawAmmeter(ctx, 400, canvas.height / 2 - 80, current);

            // Update results
            document.getElementById('total-r').textContent = `${totalR.toFixed(0)} Ω`;
            document.getElementById('circuit-current').textContent = `${(current * 1000).toFixed(1)} mA`;
            document.getElementById('v1-result').textContent = `${v1.toFixed(2)} V`;
            document.getElementById('v2-result').textContent = `${v2.toFixed(2)} V`;
        },

        /**
         * Draw parallel circuit
         */
        drawParallelCircuit(sim) {
            const { ctx, canvas, values } = sim;
            const r1 = values['r1'] || 100;
            const r2 = values['r2'] || 200;
            const voltage = values['voltage'] || 12;

            const i1 = voltage / r1;
            const i2 = voltage / r2;
            const totalI = i1 + i2;
            const totalR = voltage / totalI;

            this.drawGrid(ctx, canvas);

            // Draw voltage source
            this.drawBattery(ctx, 100, canvas.height / 2, voltage);

            // Draw parallel branches
            this.drawResistor(ctx, 400, canvas.height / 2 - 60, r1);
            this.drawResistor(ctx, 400, canvas.height / 2 + 60, r2);

            // Draw ammeters
            this.drawAmmeter(ctx, 250, canvas.height / 2, totalI);
            this.drawAmmeter(ctx, 550, canvas.height / 2 - 60, i1);
            this.drawAmmeter(ctx, 550, canvas.height / 2 + 60, i2);

            // Update results
            document.getElementById('parallel-total-r').textContent = `${totalR.toFixed(1)} Ω`;
            document.getElementById('parallel-current').textContent = `${(totalI * 1000).toFixed(1)} mA`;
            document.getElementById('i1-result').textContent = `${(i1 * 1000).toFixed(1)} mA`;
            document.getElementById('i2-result').textContent = `${(i2 * 1000).toFixed(1)} mA`;
        },

        /**
         * Default draw function
         */
        drawDefault(sim) {
            const { ctx, canvas } = sim;
            this.drawGrid(ctx, canvas);
        },

        /**
         * Draw helper methods
         */
        drawGrid(ctx, canvas) {
            ctx.strokeStyle = '#e5e7eb';
            ctx.lineWidth = 0.5;

            for (let x = 0; x < canvas.width; x += 40) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }

            for (let y = 0; y < canvas.height; y += 40) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        },

        drawArrow(ctx, fromX, fromY, toX, toY, color, label) {
            const headLen = 15;
            const angle = Math.atan2(toY - fromY, toX - fromX);

            ctx.strokeStyle = color;
            ctx.fillStyle = color;
            ctx.lineWidth = 3;

            // Draw line
            ctx.beginPath();
            ctx.moveTo(fromX, fromY);
            ctx.lineTo(toX, toY);
            ctx.stroke();

            // Draw arrowhead
            ctx.beginPath();
            ctx.moveTo(toX, toY);
            ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6));
            ctx.closePath();
            ctx.fill();

            // Draw label
            if (label) {
                ctx.font = 'bold 14px Inter, sans-serif';
                ctx.fillStyle = color;
                ctx.fillText(label, toX + 10, toY);
            }
        },

        drawBattery(ctx, x, y, voltage) {
            ctx.strokeStyle = '#374151';
            ctx.lineWidth = 2;

            // Draw battery symbol
            ctx.strokeRect(x - 15, y - 20, 30, 40);

            // Draw positive terminal
            ctx.beginPath();
            ctx.moveTo(x + 15, y - 10);
            ctx.lineTo(x + 25, y - 10);
            ctx.lineTo(x + 25, y + 10);
            ctx.lineTo(x + 15, y + 10);
            ctx.stroke();

            // Label
            ctx.font = '14px Inter, sans-serif';
            ctx.fillStyle = '#374151';
            ctx.fillText(`${voltage}V`, x - 10, y + 40);
        },

        drawResistor(ctx, x, y, resistance) {
            ctx.strokeStyle = '#374151';
            ctx.lineWidth = 2;

            // Draw zigzag resistor
            ctx.beginPath();
            ctx.moveTo(x - 40, y);
            ctx.lineTo(x - 30, y - 15);
            ctx.lineTo(x - 10, y + 15);
            ctx.lineTo(x + 10, y - 15);
            ctx.lineTo(x + 30, y + 15);
            ctx.lineTo(x + 40, y);
            ctx.stroke();

            // Label
            ctx.font = '14px Inter, sans-serif';
            ctx.fillStyle = '#374151';
            ctx.fillText(`${Math.round(resistance)}Ω`, x - 10, y + 35);
        },

        drawAmmeter(ctx, x, y, current) {
            ctx.strokeStyle = '#22c55e';
            ctx.lineWidth = 2;

            // Draw circle
            ctx.beginPath();
            ctx.arc(x, y, 25, 0, Math.PI * 2);
            ctx.stroke();

            // Draw A
            ctx.font = 'bold 16px Inter, sans-serif';
            ctx.fillStyle = '#22c55e';
            ctx.textAlign = 'center';
            ctx.fillText('A', x, y + 6);

            // Value
            ctx.font = '12px Inter, sans-serif';
            ctx.fillStyle = '#374151';
            ctx.fillText(`${(current * 1000).toFixed(1)}mA`, x, y + 45);
        },

        drawVoltmeter(ctx, x, y, voltage) {
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;

            // Draw circle with V
            ctx.beginPath();
            ctx.arc(x, y, 25, 0, Math.PI * 2);
            ctx.stroke();

            // Draw V
            ctx.font = 'bold 16px Inter, sans-serif';
            ctx.fillStyle = '#3b82f6';
            ctx.textAlign = 'center';
            ctx.fillText('V', x, y + 6);

            // Value
            ctx.font = '12px Inter, sans-serif';
            ctx.fillStyle = '#374151';
            ctx.fillText(`${voltage.toFixed(1)}V`, x, y + 45);
        },

        /**
         * Update simulation results display
         */
        updateResults(simulationType) {
            const sim = this.activeSimulations[simulationType];
            if (!sim || !sim.config.results) return;

            sim.config.results.forEach(result => {
                const element = document.getElementById(result.id);
                if (element) {
                    // Update with calculated value if needed
                }
            });
        }
    };

    // ================================================
    // PRACTICE PROBLEM CONTROLLER
    // ================================================

    const ProblemController = {
        /**
         * Select a multiple choice answer
         */
        selectChoice(problemId, choiceValue) {
            const container = document.getElementById(`choices-${problemId}`);
            if (!container) return;

            // Remove previous selection
            container.querySelectorAll('.quiz-option').forEach(opt => {
                opt.classList.remove('selected');
                opt.querySelector('input').checked = false;
            });

            // Select new choice
            const selected = container.querySelector(`input[value="${choiceValue}"]`);
            if (selected) {
                selected.checked = true;
                selected.closest('.quiz-option').classList.add('selected');
            }
        },

        /**
         * Check answer for a problem
         */
        checkAnswer(problemId, correctAnswer) {
            const container = document.getElementById(`choices-${problemId}`);
            if (!container) return;

            const selected = container.querySelector('input:checked');
            if (!selected) {
                showToast('Please select an answer', 'warning');
                return;
            }

            const userAnswer = selected.value;
            const feedbackEl = document.getElementById(`feedback-${problemId}`);

            // Disable further changes
            container.querySelectorAll('input').forEach(input => {
                input.disabled = true;
            });

            // Mark correct/incorrect
            container.querySelectorAll('.quiz-option').forEach(opt => {
                const value = opt.querySelector('input').value;
                opt.classList.remove('selected');
                if (value === correctAnswer) {
                    opt.classList.add('correct');
                } else if (value === userAnswer && userAnswer !== correctAnswer) {
                    opt.classList.add('incorrect');
                }
            });

            // Show feedback
            if (feedbackEl) {
                const isCorrect = userAnswer === correctAnswer;
                feedbackEl.className = `feedback ${isCorrect ? 'correct' : 'incorrect'}`;
                feedbackEl.innerHTML = isCorrect
                    ? '<i class="fas fa-check-circle"></i> Correct! Well done.'
                    : '<i class="fas fa-times-circle"></i> Incorrect. Try reviewing the theory section.';
                feedbackEl.classList.remove('hidden');
            }

            // Mark as checked
            LessonState.answersChecked[problemId] = true;
            LessonState.save();

            // Show solution
            const solutionEl = document.getElementById(`solution-${problemId}`);
            if (solutionEl && !isCorrect) {
                solutionEl.classList.remove('hidden');
            }
        }
    };

    // ================================================
    // UI HELPERS
    // ================================================

    /**
     * Show toast notification
     */
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type} flex items-center gap-2`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-times-circle' : type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'toastIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Toggle solution visibility
     */
    function toggleSolution(solutionId) {
        const solution = document.getElementById(solutionId);
        if (solution) {
            solution.classList.toggle('hidden');
        }
    }

    /**
     * Open help modal
     */
    function openHelpModal(content) {
        const modal = document.getElementById('help-modal');
        const contentEl = document.getElementById('help-modal-content');

        if (modal && contentEl) {
            contentEl.innerHTML = content;
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    /**
     * Close help modal
     */
    function closeHelpModal() {
        const modal = document.getElementById('help-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    // ================================================
    // NAVIGATION
    // ================================================

    /**
     * Update navigation links
     */
    function updateNavigation(lesson, prevLesson, nextLesson) {
        const prevLink = document.getElementById('prev-link');
        const prevTitle = document.getElementById('prev-title');
        const nextLink = document.getElementById('next-link');
        const nextTitle = document.getElementById('next-title');

        if (prevLesson && prevLink && prevTitle) {
            prevLink.href = prevLesson.slug ? `${prevLesson.slug}.html` : '#';
            prevTitle.textContent = prevLesson.title;
            prevLink.classList.remove('disabled');
        } else if (prevLink) {
            prevLink.classList.add('disabled');
            prevLink.href = '#';
        }

        if (nextLesson && nextLink && nextTitle) {
            nextLink.href = nextLesson.slug ? `${nextLesson.slug}.html` : '#';
            nextTitle.textContent = nextLesson.title;
            nextLink.classList.remove('disabled');
        } else if (nextLink) {
            nextLink.classList.add('disabled');
            nextLink.href = '#';
        }
    }

    // ================================================
    // THEME TOGGLE
    // ================================================

    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;

        // Check for saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // ================================================
    // SCROLL SPY
    // ================================================

    function initScrollSpy() {
        const navLinks = document.querySelectorAll('.nav-link[data-section]');
        const sections = Array.from(navLinks).map(link => {
            const id = link.getAttribute('data-section');
            const element = document.getElementById(id);
            return { link, element };
        }).filter(item => item.element);

        if (sections.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navLinks.forEach(link => {
                        link.classList.toggle('active', link.getAttribute('data-section') === id);
                    });
                }
            });
        }, { rootMargin: '-20% 0px -80% 0px' });

        sections.forEach(({ element }) => observer.observe(element));
    }

    // ================================================
    // INITIALIZATION
    // ================================================

    /**
     * Initialize the lesson template
     */
    async function init() {
        // Get lesson parameters from URL or data attributes
        const container = document.querySelector('.lesson-container');
        const discipline = container?.dataset.discipline || 'electrical';
        const lessonId = container?.dataset.lesson || '01-introduction';

        // Load lesson data
        const lesson = await DataLoader.loadLessonData(discipline, lessonId);

        if (lesson) {
            DataLoader.renderLesson(lesson);

            // Initialize simulations if present
            if (lesson.simulations) {
                lesson.simulations.forEach(sim => {
                    SimulationController.init(sim.type, sim.canvasId, sim);
                });
            }
        }

        // Initialize UI components
        initThemeToggle();
        initScrollSpy();

        // Close modal on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeHelpModal();
            }
        });

        // Close modal on backdrop click
        const helpModal = document.getElementById('help-modal');
        if (helpModal) {
            helpModal.addEventListener('click', (e) => {
                if (e.target === helpModal) {
                    closeHelpModal();
                }
            });
        }

        // Help button
        const helpBtn = document.getElementById('help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => {
                openHelpModal(`
                    <h4>How to Use This Lesson</h4>
                    <ol>
                        <li>Read through the theory section to understand the concepts</li>
                        <li>Use the interactive simulations to visualize the concepts</li>
                        <li>Practice with the problems to test your understanding</li>
                        <li>Check your answers and review any mistakes</li>
                        <li>Mark objectives as complete as you finish them</li>
                    </ol>
                `);
            });
        }

        // Bookmark button
        const bookmarkBtn = document.getElementById('bookmark-btn');
        if (bookmarkBtn) {
            bookmarkBtn.addEventListener('click', () => {
                const icon = bookmarkBtn.querySelector('i');
                if (icon.classList.contains('far')) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    showToast('Lesson bookmarked', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    showToast('Bookmark removed', 'info');
                }
            });
        }
    }

    // ================================================
    // PUBLIC API
    // ================================================

    window.LessonTemplate = {
        updateObjective: (index, completed) => {
            LessonState.setObjectiveCompleted(index, completed);
            showToast(completed ? 'Objective completed!' : 'Objective unchecked', 'info');
        },
        updateSimulationParam: (type, controlId, value) => {
            SimulationController.updateParam(type, controlId, value);
        },
        startSimulation: (type) => {
            SimulationController.start(type);
        },
        pauseSimulation: (type) => {
            SimulationController.pause(type);
        },
        resetSimulation: (type) => {
            SimulationController.reset(type);
        },
        checkAnswer: (problemId, correctAnswer) => {
            ProblemController.checkAnswer(problemId, correctAnswer);
        },
        selectChoice: (problemId, choiceValue) => {
            ProblemController.selectChoice(problemId, choiceValue);
        },
        toggleSolution,
        openHelpModal,
        closeHelpModal
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();