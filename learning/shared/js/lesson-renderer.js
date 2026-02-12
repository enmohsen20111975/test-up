/**
 * EngiSuite Analytics - Lesson Renderer Module
 * Loads and renders lessons dynamically from JSON data sources
 */

const LessonRenderer = (function () {
    'use strict';

    // Current state
    let currentLesson = null;
    let currentChapter = null;
    let currentDiscipline = null;
    let simulationStates = {};

    // Default lesson data
    const defaultLesson = {
        id: 'default',
        title: 'Welcome to EngiSuite Analytics',
        duration: '15 min',
        level: 'Beginner',
        objectives: [
            'Understand the platform navigation',
            'Explore available courses',
            'Start your learning journey'
        ],
        content: {
            introduction: 'Welcome to your comprehensive engineering learning platform.',
            sections: []
        }
    };

    /**
     * Initialize the lesson renderer
     */
    function init(options = {}) {
        const { lessonId, chapterId, disciplineKey } = options;

        loadDiscipline(disciplineKey || 'electrical')
            .then(() => {
                if (chapterId && lessonId) {
                    loadLesson(chapterId, lessonId);
                } else {
                    loadDefaultLesson();
                }
            })
            .catch(handleError);

        initializeEventListeners();
        initializeTheme();
    }

    /**
     * Load discipline data
     */
    async function loadDiscipline(key) {
        try {
            const response = await fetch(`../data/${key}/courses.json`);
            if (!response.ok) throw new Error(`Failed to load ${key} courses`);

            currentDiscipline = await response.json();
            renderCourseNavigation();
            return currentDiscipline;
        } catch (error) {
            console.error('Error loading discipline:', error);
            return null;
        }
    }

    /**
     * Load specific lesson
     */
    async function loadLesson(chapterId, lessonId) {
        try {
            showLoadingState();

            // Find the lesson in current discipline
            const chapter = currentDiscipline.chapters.find(c => c.id === chapterId);
            if (!chapter) throw new Error(`Chapter ${chapterId} not found`);

            const lesson = chapter.lessons.find(l => l.id === lessonId);
            if (!lesson) throw new Error(`Lesson ${lessonId} not found`);

            currentChapter = chapter;
            currentLesson = lesson;

            renderLesson();
            saveProgress();
        } catch (error) {
            handleError(error);
        }
    }

    /**
     * Load default welcome lesson
     */
    function loadDefaultLesson() {
        currentLesson = { ...defaultLesson };
        renderLesson();
    }

    /**
     * Render the complete lesson
     */
    function renderLesson() {
        const container = document.getElementById('lesson-content');
        if (!container) {
            console.error('Lesson content container not found');
            return;
        }

        updateBreadcrumb();
        updateHeader();
        updateObjectives();
        renderTheorySection();
        renderSimulationSection();
        renderPracticeSection();
        updateProgress();

        // Re-render MathJax
        if (window.MathJax) {
            MathJax.typesetPromise();
        }

        hideLoadingState();
    }

    /**
     * Update breadcrumb navigation
     */
    function updateBreadcrumb() {
        const chapterEl = document.getElementById('breadcrumb-chapter');
        const lessonEl = document.getElementById('breadcrumb-lesson');

        if (chapterEl && currentChapter) {
            chapterEl.textContent = currentChapter.title;
        }
        if (lessonEl && currentLesson) {
            lessonEl.textContent = currentLesson.title;
        }
    }

    /**
     * Update lesson header
     */
    function updateHeader() {
        const titleEl = document.getElementById('lesson-title');
        const durationEl = document.getElementById('lesson-duration');
        const levelEl = document.getElementById('lesson-level');

        if (titleEl && currentLesson) titleEl.textContent = currentLesson.title;
        if (durationEl && currentLesson) durationEl.textContent = currentLesson.duration;
        if (levelEl && currentLesson) levelEl.textContent = currentLesson.level;
    }

    /**
     * Update learning objectives
     */
    function updateObjectives() {
        const listEl = document.getElementById('objectives-list');
        if (!listEl || !currentLesson) return;

        listEl.innerHTML = currentLesson.objectives.map((obj, idx) => `
            <li class="flex items-start gap-2">
                <input type="checkbox" id="obj-${idx + 1}"
                    class="mt-1 w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    onchange="LessonRenderer.updateProgress()">
                <label for="obj-${idx + 1}" class="text-gray-700 dark:text-gray-300 cursor-pointer">
                    ${obj}
                </label>
            </li>
        `).join('');
    }

    /**
     * Render theory section
     */
    function renderTheorySection() {
        const container = document.getElementById('theory-content');
        if (!container || !currentLesson) return;

        let html = `
            <h3>${currentLesson.content.introduction ? 'Introduction' : ''}</h3>
            <p>${currentLesson.content.introduction || ''}</p>
        `;

        if (currentLesson.content.sections) {
            currentLesson.content.sections.forEach(section => {
                html += `<h3>${section.title}</h3><p>${section.content}</p>`;
            });
        }

        if (currentLesson.formulas) {
            html += '<h3>Key Formulas</h3>';
            currentLesson.formulas.forEach(formula => {
                html += `
                    <div class="math-formula bg-gray-50 dark:bg-gray-800 rounded-lg p-4 my-4">
                        $$ ${formula.formula} $$
                        ${formula.description ? `<p class="text-sm text-gray-500 mt-2">${formula.description}</p>` : ''}
                    </div>
                `;
            });
        }

        container.innerHTML = html;
    }

    /**
     * Render simulation section
     */
    function renderSimulationSection() {
        const container = document.getElementById('simulation-container');
        if (!container || !currentLesson || !currentLesson.simulations) return;

        const sim = currentLesson.simulations[0];
        if (!sim) return;

        let controlsHtml = '';
        if (sim.controls) {
            controlsHtml = sim.controls.map(control => `
                <div class="control-group">
                    <label for="${control.id}" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        ${control.label}: <span id="${control.valueId}">${control.defaultValue}</span>${control.unit || ''}
                    </label>
                    <input type="${control.type}" id="${control.id}" 
                        min="${control.min}" max="${control.max}" 
                        value="${control.defaultValue}" step="${control.step || 1}"
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                        oninput="LessonRenderer.updateSimulation('${sim.type}', '${control.id}', this.value)">
                </div>
            `).join('');
        }

        let resultsHtml = '';
        if (sim.results) {
            resultsHtml = sim.results.map(result => `
                <div class="result-card text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                    <p class="text-sm text-gray-500">${result.label}</p>
                    <p class="text-lg font-mono font-bold text-primary-600" id="${result.id}">${result.value}</p>
                </div>
            `).join('');
        }

        container.innerHTML = `
            <div class="simulation-canvas bg-gray-100 dark:bg-gray-800 h-64 flex items-center justify-center rounded-lg">
                <canvas id="${sim.canvasId}" width="800" height="300"></canvas>
            </div>
            <div class="simulation-controls p-4 bg-gray-50 dark:bg-gray-900 rounded-b-lg">
                <div class="grid grid-cols-1 md:grid-cols-${sim.controls?.length || 2} gap-4">
                    ${controlsHtml}
                </div>
                <div class="mt-4 flex gap-2">
                    <button onclick="LessonRenderer.startSimulation('${sim.type}')" 
                        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                        <i class="fas fa-play mr-1"></i> Start
                    </button>
                    <button onclick="LessonRenderer.resetSimulation('${sim.type}')" 
                        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                        <i class="fas fa-redo mr-1"></i> Reset
                    </button>
                </div>
            </div>
            <div class="results-display p-4 bg-gray-50 dark:bg-gray-900 grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 rounded-lg">
                ${resultsHtml}
            </div>
        `;

        initializeSimulationCanvas(sim);
    }

    /**
     * Render practice problems section
     */
    function renderPracticeSection() {
        const container = document.getElementById('problems-container');
        if (!container || !currentLesson) return;

        if (!currentLesson.problems || currentLesson.problems.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No practice problems available for this lesson.</p>';
            return;
        }

        container.innerHTML = currentLesson.problems.map((problem, idx) => {
            let inputHtml = '';
            if (problem.hasInput) {
                inputHtml = `
                    <div class="flex gap-2 mb-4">
                        <input type="${problem.inputType || 'text'}" placeholder="${problem.inputPlaceholder || 'Enter your answer'}"
                            class="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600"
                            id="answer-${problem.id}">
                        <button onclick="LessonRenderer.checkAnswer('${problem.id}', '${problem.correctAnswer}', '${problem.answerType}')"
                            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                            Check
                        </button>
                    </div>
                `;
            }

            if (problem.hasChoices) {
                inputHtml = `
                    <div class="space-y-2 mb-4">
                        ${problem.choices.map(choice => `
                            <label class="quiz-option flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                                <input type="radio" name="problem-${problem.id}" value="${choice.value}">
                                <span>${choice.text}</span>
                            </label>
                        `).join('')}
                    </div>
                    <button onclick="LessonRenderer.checkMultipleChoice('${problem.id}', '${problem.correctAnswer}')"
                        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                        Submit Answer
                    </button>
                `;
            }

            return `
                <div class="problem-card border rounded-lg p-4" id="problem-${problem.id}">
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="font-semibold">${problem.title}</h3>
                        <span class="text-xs px-2 py-1 bg-${problem.difficultyColor}-100 dark:bg-${problem.difficultyColor}-900 rounded">
                            ${problem.difficulty}
                        </span>
                    </div>
                    <p class="text-gray-700 dark:text-gray-300 mb-4">${problem.description}</p>
                    ${inputHtml}
                    <button onclick="LessonRenderer.toggleSolution('solution-${problem.id}')"
                        class="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1 mt-3">
                        <i class="fas fa-eye"></i> Show Solution
                    </button>
                    <div id="solution-${problem.id}" class="solution-content mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hidden">
                        <h4 class="font-medium text-green-800 dark:text-green-300 mb-2">
                            <i class="fas fa-check-circle mr-1"></i>Solution
                        </h4>
                        ${problem.formula ? `<div class="math-formula">$$ ${problem.formula} $$</div>` : ''}
                        <ol class="list-decimal list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1 mt-2">
                            ${problem.steps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                        <p class="mt-2 text-sm font-medium text-green-800 dark:text-green-300">
                            Final Answer: <span class="font-mono">${problem.finalAnswer}</span>
                        </p>
                    </div>
                </div>
            `;
        }).join('');

        if (window.MathJax) {
            MathJax.typesetPromise();
        }
    }

    /**
     * Initialize simulation canvas
     */
    function initializeSimulationCanvas(sim) {
        const canvas = document.getElementById(sim.canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const state = {
            type: sim.type,
            controls: sim.controls || [],
            results: sim.results || []
        };
        simulationStates[sim.type] = state;

        drawSimulation(sim.type, ctx);
    }

    /**
     * Draw simulation on canvas
     */
    function drawSimulation(type, ctx) {
        const state = simulationStates[type];
        if (!state) return;

        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Draw based on simulation type
        switch (type) {
            case 'ohms-law':
                drawOhmsLawSimulation(ctx, state);
                break;
            case 'series-circuit':
                drawSeriesCircuit(ctx, state);
                break;
            case 'parallel-circuit':
                drawParallelCircuit(ctx, state);
                break;
            case 'beam-analysis':
                drawBeamSimulation(ctx, state);
                break;
            default:
                drawGenericSimulation(ctx, state);
        }
    }

    /**
     * Draw Ohm's Law simulation
     */
    function drawOhmsLawSimulation(ctx, state) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        // Get current values
        const voltage = parseFloat(document.getElementById('sim-voltage')?.value) || 12;
        const resistance = parseFloat(document.getElementById('sim-resistance')?.value) || 100;
        const current = (voltage / resistance).toFixed(3);

        // Draw circuit
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;

        // Battery
        ctx.fillStyle = '#64748b';
        ctx.fillRect(100, height / 2 - 30, 20, 60);
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(95, height / 2 - 20, 10, 15);
        ctx.fillStyle = '#64748b';
        ctx.fillRect(115, height / 2 + 5, 10, 15);

        // Wires
        ctx.beginPath();
        ctx.moveTo(120, height / 2);
        ctx.lineTo(200, height / 2);
        ctx.lineTo(200, height / 2 - 50);
        ctx.lineTo(400, height / 2 - 50);
        ctx.lineTo(400, height / 2);
        ctx.lineTo(500, height / 2);
        ctx.lineTo(500, height / 2 + 50);
        ctx.lineTo(200, height / 2 + 50);
        ctx.lineTo(200, height / 2);
        ctx.lineTo(120, height / 2);
        ctx.stroke();

        // Resistor
        ctx.fillStyle = '#22c55e';
        ctx.fillRect(300, height / 2 - 25, 60, 50);
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${resistance}Ω`, 330, height / 2 + 5);

        // Labels
        ctx.fillStyle = '#1e293b';
        ctx.font = '12px sans-serif';
        ctx.fillText(`${voltage}V`, 100, height / 2 - 45);
        ctx.fillText(`${current}A`, 530, height / 2);
    }

    /**
     * Draw series circuit simulation
     */
    function drawSeriesCircuit(ctx, state) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;

        // Draw complete circuit loop
        ctx.beginPath();
        ctx.moveTo(100, height / 2);
        ctx.lineTo(700, height / 2);
        ctx.lineTo(700, height / 2 - 100);
        ctx.lineTo(100, height / 2 - 100);
        ctx.closePath();
        ctx.stroke();

        // Draw resistors
        const resistors = ['R1', 'R2', 'R3'];
        const positions = [250, 400, 550];

        ctx.fillStyle = '#22c55e';
        resistors.forEach((label, idx) => {
            const x = positions[idx];
            ctx.fillRect(x, height / 2 - 30, 50, 60);
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(label, x + 25, height / 2 + 5);
            ctx.fillStyle = '#22c55e';
        });
    }

    /**
     * Draw parallel circuit simulation
     */
    function drawParallelCircuit(ctx, state) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;

        // Main wire
        ctx.beginPath();
        ctx.moveTo(100, height / 2);
        ctx.lineTo(700, height / 2);
        ctx.stroke();

        // Branch 1
        ctx.beginPath();
        ctx.moveTo(200, height / 2);
        ctx.lineTo(200, height / 2 + 80);
        ctx.lineTo(400, height / 2 + 80);
        ctx.lineTo(400, height / 2);
        ctx.stroke();

        // Branch 2
        ctx.beginPath();
        ctx.moveTo(350, height / 2);
        ctx.lineTo(350, height / 2 - 80);
        ctx.lineTo(450, height / 2 - 80);
        ctx.lineTo(450, height / 2);
        ctx.stroke();

        // Branch 3
        ctx.beginPath();
        ctx.moveTo(500, height / 2);
        ctx.lineTo(500, height / 2 + 80);
        ctx.lineTo(600, height / 2 + 80);
        ctx.lineTo(600, height / 2);
        ctx.stroke();

        // Draw resistors
        ctx.fillStyle = '#22c55e';
        const resistorData = [
            { x: 300, y: 80, label: 'R1' },
            { x: 400, y: -80, label: 'R2' },
            { x: 550, y: 80, label: 'R3' }
        ];

        resistorData.forEach(r => {
            ctx.fillRect(r.x, height / 2 + r.y - 25, 50, 50);
            ctx.fillStyle = '#ffffff';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(r.label, r.x + 25, height / 2 + r.y + 5);
            ctx.fillStyle = '#22c55e';
        });
    }

    /**
     * Draw beam simulation
     */
    function drawBeamSimulation(ctx, state) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        const span = parseFloat(document.getElementById('span')?.value) || 6;
        const load = parseFloat(document.getElementById('load-mag')?.value) || 10;

        // Scale factor
        const scale = 80;

        // Draw beam
        ctx.fillStyle = '#64748b';
        ctx.fillRect(100, height / 2, span * scale, 20);

        // Draw supports
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.moveTo(100, height / 2 + 20);
        ctx.lineTo(90, height / 2 + 40);
        ctx.lineTo(110, height / 2 + 40);
        ctx.closePath();
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(100 + span * scale, height / 2 + 20);
        ctx.lineTo(100 + span * scale - 10, height / 2 + 40);
        ctx.lineTo(100 + span * scale + 10, height / 2 + 40);
        ctx.closePath();
        ctx.fill();

        // Draw distributed load
        ctx.fillStyle = '#ef4444';
        for (let x = 100; x < 100 + span * scale; x += 20) {
            ctx.beginPath();
            ctx.moveTo(x, height / 2 - 20);
            ctx.lineTo(x - 5, height / 2 - 40);
            ctx.lineTo(x + 5, height / 2 - 40);
            ctx.closePath();
            ctx.fill();
        }

        // Labels
        ctx.fillStyle = '#1e293b';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`Span: ${span}m`, 100 + span * scale / 2, height / 2 + 60);
        ctx.fillText(`Load: ${load} kN/m`, 100 + span * scale / 2, height / 2 - 50);
    }

    /**
     * Draw generic simulation
     */
    function drawGenericSimulation(ctx, state) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        ctx.fillStyle = '#64748b';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Interactive Simulation', width / 2, height / 2 - 20);
        ctx.font = '12px sans-serif';
        ctx.fillText('Configure parameters using the controls below', width / 2, height / 2 + 10);
    }

    /**
     * Update simulation
     */
    function updateSimulation(simType, controlId, value) {
        const state = simulationStates[simType];
        if (!state) return;

        // Update value display
        const valueEl = document.getElementById(state.controls.find(c => c.id === controlId)?.valueId);
        if (valueEl) valueEl.textContent = value;

        // Calculate and update results
        calculateSimulationResults(simType);

        // Redraw canvas
        const canvas = document.getElementById(state.canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            drawSimulation(simType, ctx);
        }
    }

    /**
     * Calculate simulation results
     */
    function calculateSimulationResults(simType) {
        const state = simulationStates[simType];
        if (!state) return;

        switch (simType) {
            case 'ohms-law':
                const v = parseFloat(document.getElementById('sim-voltage')?.value) || 12;
                const r = parseFloat(document.getElementById('sim-resistance')?.value) || 100;
                const i = (v / r).toFixed(3);
                updateResult('current-result', `${i} A`);
                break;
        }
    }

    /**
     * Update result display
     */
    function updateResult(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) el.textContent = value;
    }

    /**
     * Start simulation
     */
    function startSimulation(simType) {
        const state = simulationStates[simType];
        if (!state) return;

        console.log(`Starting ${simType} simulation`);

        // Show feedback
        const feedback = document.getElementById('simulation-feedback');
        if (feedback) feedback.classList.remove('hidden');
    }

    /**
     * Reset simulation
     */
    function resetSimulation(simType) {
        const state = simulationStates[simType];
        if (!state) return;

        // Reset controls to default values
        state.controls.forEach(control => {
            const el = document.getElementById(control.id);
            if (el) {
                el.value = control.defaultValue;
                document.getElementById(control.valueId).textContent = control.defaultValue;
            }
        });

        // Redraw
        const canvas = document.getElementById(state.canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            drawSimulation(simType, ctx);
        }

        // Hide feedback
        const feedback = document.getElementById('simulation-feedback');
        if (feedback) feedback.classList.add('hidden');
    }

    /**
     * Check answer
     */
    function checkAnswer(problemId, correctAnswer, answerType) {
        const inputEl = document.getElementById(`answer-${problemId}`);
        if (!inputEl) return;

        const userAnswer = parseFloat(inputEl.value);
        const correct = parseFloat(correctAnswer);
        const tolerance = 0.01; // 1% tolerance

        const isCorrect = Math.abs(userAnswer - correct) <= tolerance;

        const feedback = document.createElement('div');
        feedback.className = isCorrect
            ? 'mt-3 p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg'
            : 'mt-3 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg';
        feedback.innerHTML = isCorrect
            ? '<i class="fas fa-check-circle mr-2"></i>Correct!'
            : `<i class="fas fa-times-circle mr-2"></i>Incorrect. The correct answer is ${correctAnswer}`;

        const existingFeedback = document.getElementById(`feedback-${problemId}`);
        if (existingFeedback) existingFeedback.remove();

        feedback.id = `feedback-${problemId}`;
        inputEl.parentNode.after(feedback);
    }

    /**
     * Check multiple choice answer
     */
    function checkMultipleChoice(problemId, correctAnswer) {
        const selected = document.querySelector(`input[name="problem-${problemId}"]:checked`);
        if (!selected) {
            alert('Please select an answer');
            return;
        }

        const isCorrect = selected.value === correctAnswer;

        // Update visual feedback
        const options = document.querySelectorAll(`input[name="problem-${problemId}"]`);
        options.forEach(opt => {
            const label = opt.parentElement;
            if (opt.value === correctAnswer) {
                label.classList.add('bg-green-100', 'dark:bg-green-900');
                label.classList.remove('hover:bg-gray-50');
            } else if (opt.checked && !isCorrect) {
                label.classList.add('bg-red-100', 'dark:bg-red-900');
            }
        });
    }

    /**
     * Toggle solution visibility
     */
    function toggleSolution(solutionId) {
        const el = document.getElementById(solutionId);
        if (el) {
            el.classList.toggle('hidden');
        }
    }

    /**
     * Update progress
     */
    function updateProgress() {
        const checkboxes = document.querySelectorAll('#objectives-list input[type="checkbox"]');
        const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
        const total = checkboxes.length;
        const percentage = total > 0 ? Math.round((checked / total) * 100) : 0;

        // Update progress ring
        const progressRing = document.getElementById('progress-ring');
        const progressText = document.getElementById('progress-text');

        if (progressRing) {
            const circumference = 2 * Math.PI * 16;
            const offset = circumference - (percentage / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
        }

        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }

        // Save to localStorage
        saveProgress();
    }

    /**
     * Save progress
     */
    function saveProgress() {
        if (!currentLesson) return;

        const progress = {
            lessonId: currentLesson.id,
            chapterId: currentChapter?.id,
            discipline: currentDiscipline?.disciplineKey,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem('engisuite_lesson_progress', JSON.stringify(progress));
    }

    /**
     * Render course navigation
     */
    function renderCourseNavigation() {
        const navEl = document.getElementById('course-navigation');
        if (!navEl || !currentDiscipline) return;

        navEl.innerHTML = currentDiscipline.chapters.map(chapter => `
            <div class="chapter-section mb-4">
                <h3 class="font-semibold text-gray-800 dark:text-white mb-2">
                    <i class="${chapter.icon} mr-2 text-primary-600"></i>
                    ${chapter.title}
                </h3>
                <ul class="space-y-1 ml-4">
                    ${chapter.lessons.map(lesson => `
                        <li>
                            <a href="#lesson-${lesson.id}" 
                                class="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 block py-1"
                                onclick="LessonRenderer.loadLesson('${chapter.id}', '${lesson.id}')">
                                ${lesson.title}
                            </a>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `).join('');
    }

    /**
     * Initialize event listeners
     */
    function initializeEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }

        // Objectives toggle
        const objectivesToggle = document.getElementById('objectives-toggle');
        const objectivesIcon = document.getElementById('objectives-icon');
        if (objectivesToggle) {
            objectivesToggle.addEventListener('click', () => {
                const panel = document.getElementById('objectives-panel');
                if (panel) {
                    panel.classList.toggle('hidden');
                    if (objectivesIcon) {
                        objectivesIcon.classList.toggle('fa-chevron-up');
                        objectivesIcon.classList.toggle('fa-chevron-down');
                    }
                }
            });
        }

        // Bookmark button
        const bookmarkBtn = document.getElementById('bookmark-btn');
        if (bookmarkBtn) {
            bookmarkBtn.addEventListener('click', toggleBookmark);
        }
    }

    /**
     * Initialize theme
     */
    function initializeTheme() {
        const savedTheme = localStorage.getItem('engisuite_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    /**
     * Toggle theme
     */
    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('engisuite_theme', newTheme);
    }

    /**
     * Toggle bookmark
     */
    function toggleBookmark() {
        const btn = document.getElementById('bookmark-btn');
        if (!btn || !currentLesson) return;

        const icon = btn.querySelector('i');
        if (icon) {
            const isBookmarked = icon.classList.contains('fas');

            if (isBookmarked) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }

            // Save bookmark
            const bookmarks = JSON.parse(localStorage.getItem('engisuite_bookmarks') || '[]');
            if (isBookmarked) {
                const idx = bookmarks.findIndex(b => b.id === currentLesson.id);
                if (idx > -1) bookmarks.splice(idx, 1);
            } else {
                bookmarks.push({
                    id: currentLesson.id,
                    title: currentLesson.title,
                    chapter: currentChapter?.title,
                    timestamp: new Date().toISOString()
                });
            }
            localStorage.setItem('engisuite_bookmarks', JSON.stringify(bookmarks));
        }
    }

    /**
     * Show loading state
     */
    function showLoadingState() {
        const content = document.getElementById('main-content');
        if (content) {
            content.classList.add('opacity-50', 'pointer-events-none');
        }
    }

    /**
     * Hide loading state
     */
    function hideLoadingState() {
        const content = document.getElementById('main-content');
        if (content) {
            content.classList.remove('opacity-50', 'pointer-events-none');
        }
    }

    /**
     * Handle errors
     */
    function handleError(error) {
        console.error('Lesson Renderer Error:', error);

        const errorEl = document.createElement('div');
        errorEl.className = 'p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg';
        errorEl.innerHTML = `
            <i class="fas fa-exclamation-circle mr-2"></i>
            Error: ${error.message}
        `;

        const container = document.getElementById('lesson-content');
        if (container) {
            container.innerHTML = '';
            container.appendChild(errorEl);
        }

        hideLoadingState();
    }

    // Public API
    return {
        init,
        loadDiscipline,
        loadLesson,
        updateSimulation,
        startSimulation,
        resetSimulation,
        checkAnswer,
        checkMultipleChoice,
        toggleSolution,
        updateProgress,
        toggleTheme,
        toggleBookmark
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LessonRenderer;
}