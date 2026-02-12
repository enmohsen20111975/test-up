/**
 * EngiSuite Analytics - Article Loader Module
 * Loads articles and learning content from the database API
 */

const ArticleLoader = (function () {
    'use strict';

    const API_BASE = '/api/learning';
    let currentArticle = null;
    let markdownRenderer = null;

    /**
     * Initialize the article loader
     */
    function init(options = {}) {
        // Initialize markdown renderer if available
        if (typeof marked !== 'undefined') {
            markdownRenderer = marked;
        } else if (typeof Showdown !== 'undefined') {
            markdownRenderer = new Showdown.converter();
        }

        console.log('Article Loader initialized');
    }

    /**
     * Load lesson by ID
     */
    async function loadLessonById(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/lessons/${lessonId}`);
            if (!response.ok) throw new Error('Failed to load lesson');

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Failed to load lesson');

            return data.data;
        } catch (error) {
            console.error('Error loading lesson:', error);
            return null;
        }
    }

    /**
     * Load lesson by slug path
     */
    async function loadLessonBySlug(disciplineKey, chapterSlug, lessonSlug) {
        try {
            const url = `${API_BASE}/lessons/slug/${disciplineKey}/${chapterSlug}/${lessonSlug}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load lesson');

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Failed to load lesson');

            return data.data;
        } catch (error) {
            console.error('Error loading lesson:', error);
            return null;
        }
    }

    /**
     * Load article content for a lesson
     */
    async function loadArticle(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/articles/${lessonId}`);
            if (!response.ok) throw new Error('Failed to load article');

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Failed to load article');

            return data.data;
        } catch (error) {
            console.error('Error loading article:', error);
            return null;
        }
    }

    /**
     * Render markdown content to HTML
     */
    function renderMarkdown(content) {
        if (!content) return '';

        if (markdownRenderer) {
            if (typeof marked !== 'undefined') {
                // Use marked library
                return marked.parse(content);
            } else if (typeof Showdown !== 'undefined') {
                // Use Showdown library
                return markdownRenderer.makeHtml(content);
            }
        }

        // Fallback: basic markdown parsing
        return basicMarkdownParse(content);
    }

    /**
     * Basic markdown parser for simple formatting
     */
    function basicMarkdownParse(text) {
        if (!text) return '';

        let html = text
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
            // Inline code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
            // Unordered lists
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            // Ordered lists
            .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
            // Tables (basic)
            .replace(/\|(.+)\|/g, function (match) {
                const cells = match.split('|').filter(c => c.trim());
                if (cells.every(c => c.match(/^[\-\s]+$/))) {
                    return ''; // Skip separator row
                }
                return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
            })
            // Paragraphs
            .replace(/\n\n/g, '</p><p>')
            // Line breaks
            .replace(/\n/g, '<br>');

        // Wrap in paragraph if not already wrapped
        if (!html.startsWith('<')) {
            html = '<p>' + html + '</p>';
        }

        return html;
    }

    /**
     * Render article to DOM element
     */
    function renderArticle(article, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        let html = '';

        // Title and summary
        if (article.summary) {
            html += `<p class="article-summary">${article.summary}</p>`;
        }

        // Key concepts
        if (article.key_concepts && article.key_concepts.length > 0) {
            html += '<div class="key-concepts mt-4 mb-4">';
            html += '<h4>Key Concepts</h4>';
            html += '<ul>';
            article.key_concepts.forEach(concept => {
                html += `<li>${concept}</li>`;
            });
            html += '</ul></div>';
        }

        // Main content
        const contentHtml = renderMarkdown(article.content);
        html += `<div class="article-content">${contentHtml}</div>`;

        // Related formulas
        if (article.related_formulas && article.related_formulas.length > 0) {
            html += '<div class="related-formulas mt-4">';
            html += '<h4>Related Formulas</h4>';
            html += '<ul>';
            article.related_formulas.forEach(formula => {
                html += `<li><code>${formula}</code></li>`;
            });
            html += '</ul></div>';
        }

        container.innerHTML = html;

        // Re-render MathJax
        if (window.MathJax) {
            MathJax.typesetPromise();
        }
    }

    /**
     * Load simulations for a lesson
     */
    async function loadSimulations(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/simulations/${lessonId}`);
            if (!response.ok) throw new Error('Failed to load simulations');

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Failed to load simulations');

            return data.data;
        } catch (error) {
            console.error('Error loading simulations:', error);
            return [];
        }
    }

    /**
     * Load practice problems for a lesson
     */
    async function loadProblems(lessonId, difficulty = null) {
        try {
            let url = `${API_BASE}/problems/${lessonId}`;
            if (difficulty) {
                url += `?difficulty=${difficulty}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load problems');

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Failed to load problems');

            return data.data;
        } catch (error) {
            console.error('Error loading problems:', error);
            return [];
        }
    }

    /**
     * Check answer for a problem
     */
    async function checkAnswer(problemId, answer) {
        try {
            const response = await fetch(`${API_BASE}/problems/${problemId}/check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answer })
            });

            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error('Error checking answer:', error);
            return null;
        }
    }

    /**
     * Calculate simulation results
     */
    async function calculateSimulation(simulationId, params) {
        try {
            const response = await fetch(`${API_BASE}/simulations/${simulationId}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();
            if (!data.success) throw new Error(data.message || 'Calculation failed');

            return data.data;
        } catch (error) {
            console.error('Error calculating simulation:', error);
            return null;
        }
    }

    /**
     * Update user progress
     */
    async function updateProgress(lessonId, progressData) {
        try {
            const response = await fetch(`${API_BASE}/progress/${lessonId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(progressData)
            });

            const data = await response.json();
            return data.success;
        } catch (error) {
            console.error('Error updating progress:', error);
            return false;
        }
    }

    /**
     * Get user progress for a lesson
     */
    async function getProgress(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/progress/${lessonId}`);
            if (!response.ok) throw new Error('Failed to get progress');

            const data = await response.json();
            if (!data.success) throw new Error(data.message);

            return data.data;
        } catch (error) {
            console.error('Error getting progress:', error);
            return null;
        }
    }

    /**
     * Add bookmark for a lesson
     */
    async function addBookmark(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/bookmarks/${lessonId}`, {
                method: 'POST'
            });

            const data = await response.json();
            return data.success;
        } catch (error) {
            console.error('Error adding bookmark:', error);
            return false;
        }
    }

    /**
     * Remove bookmark for a lesson
     */
    async function removeBookmark(lessonId) {
        try {
            const response = await fetch(`${API_BASE}/bookmarks/${lessonId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            return data.success;
        } catch (error) {
            console.error('Error removing bookmark:', error);
            return false;
        }
    }

    /**
     * Get all disciplines
     */
    async function getDisciplines() {
        try {
            const response = await fetch(`${API_BASE}/disciplines`);
            const data = await response.json();
            return data.success ? data.data : [];
        } catch (error) {
            console.error('Error getting disciplines:', error);
            return [];
        }
    }

    /**
     * Get chapters for a discipline
     */
    async function getChapters(disciplineKey) {
        try {
            const response = await fetch(`${API_BASE}/chapters?discipline_key=${disciplineKey}`);
            const data = await response.json();
            return data.success ? data.data : [];
        } catch (error) {
            console.error('Error getting chapters:', error);
            return [];
        }
    }

    /**
     * Get lessons for a chapter
     */
    async function getLessons(chapterId) {
        try {
            const response = await fetch(`${API_BASE}/lessons?chapter_id=${chapterId}`);
            const data = await response.json();
            return data.success ? data.data : [];
        } catch (error) {
            console.error('Error getting lessons:', error);
            return [];
        }
    }

    /**
     * Render lesson complete
     */
    async function renderLessonComplete(lessonData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Render header info
        updateLessonHeader(lessonData);

        // Render objectives
        renderObjectives(lessonData.objectives);

        // Load and render article
        if (lessonData.article) {
            renderArticle(lessonData.article, 'theory-content');
        }

        // Setup simulation
        if (lessonData.simulations && lessonData.simulations.length > 0) {
            setupSimulation(lessonData.simulations[0], 'simulation-container');
        }

        // Render problems
        if (lessonData.problems && lessonData.problems.length > 0) {
            renderProblems(lessonData.problems, 'problems-container');
        }
    }

    /**
     * Update lesson header elements
     */
    function updateLessonHeader(lessonData) {
        const titleEl = document.getElementById('lesson-title');
        const durationEl = document.getElementById('lesson-duration');
        const levelEl = document.getElementById('lesson-level');

        if (titleEl) titleEl.textContent = lessonData.title;
        if (durationEl) durationEl.textContent = `${lessonData.duration_minutes} min`;
        if (levelEl) levelEl.textContent = lessonData.level;
    }

    /**
     * Render learning objectives
     */
    function renderObjectives(objectives) {
        const container = document.getElementById('objectives-list');
        if (!container) return;

        container.innerHTML = objectives.map((obj, idx) => `
            <li class="flex items-start gap-2">
                <input type="checkbox" id="obj-${idx + 1}" class="mt-1"
                    onchange="ArticleLoader.updateProgressCheckbox(${idx + 1})">
                <label for="obj-${idx + 1}" class="cursor-pointer">${obj}</label>
            </li>
        `).join('');
    }

    /**
     * Update progress when checkbox changes
     */
    function updateProgressCheckbox(objectiveIdx) {
        const checkboxes = document.querySelectorAll('#objectives-list input[type="checkbox"]');
        const completed = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map((cb, idx) => idx + 1);

        const progress = document.querySelector('[data-lesson-id]');
        if (progress) {
            updateProgress(parseInt(progress.dataset.lessonId), {
                objectives_completed: completed
            });
        }
    }

    /**
     * Setup simulation from config
     */
    function setupSimulation(simConfig, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let html = `
            <div class="simulation-canvas bg-gray-100 dark:bg-gray-800 h-64 rounded-lg flex items-center justify-center">
                <canvas id="${simConfig.name.replace(/\\s+/g, '-').toLowerCase()}" 
                    width="800" height="300"></canvas>
            </div>
            <div class="simulation-controls p-4 bg-gray-50 dark:bg-gray-900 rounded-b-lg">
        `;

        // Add controls
        if (simConfig.controls) {
            html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
            simConfig.controls.forEach(control => {
                html += `
                    <div class="control-group">
                        <label class="block text-sm font-medium mb-1">${control.label}</label>
                        <input type="range" id="${control.name}" 
                            min="${control.min}" max="${control.max}" 
                            value="${control.default}" step="${control.step || 1}"
                            class="w-full"
                            oninput="ArticleLoader.updateSimulationValue('${control.name}', this.value)">
                        <span id="${control.name}-value">${control.default} ${control.unit || ''}</span>
                    </div>
                `;
            });
            html += '</div>';
        }

        html += `
                <div class="mt-4 flex gap-2">
                    <button onclick="ArticleLoader.runSimulation()" class="btn btn-primary">
                        <i class="fas fa-play mr-1"></i> Run
                    </button>
                    <button onclick="ArticleLoader.resetSimulation()" class="btn btn-secondary">
                        <i class="fas fa-redo mr-1"></i> Reset
                    </button>
                </div>
            </div>
            <div class="results-display p-4 bg-gray-50 dark:bg-gray-900 mt-4 rounded-lg">
        `;

        // Add results
        if (simConfig.results) {
            html += '<div class="grid grid-cols-2 md:grid-cols-4 gap-4">';
            simConfig.results.forEach(result => {
                html += `
                    <div class="result-card text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <p class="text-sm text-gray-500">${result.label}</p>
                        <p class="text-lg font-mono font-bold text-primary-600" id="result-${result.name}">
                            --
                        </p>
                    </div>
                `;
            });
            html += '</div>';
        }

        html += '</div>';
        container.innerHTML = html;

        // Initialize canvas
        initializeSimulationCanvas(simConfig);
    }

    /**
     * Initialize simulation canvas
     */
    function initializeSimulationCanvas(simConfig) {
        const canvasId = simConfig.name.replace(/\\s+/g, '-').toLowerCase();
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Draw initial state
        drawSimulation(ctx, simConfig, {});
    }

    /**
     * Draw simulation on canvas
     */
    function drawSimulation(ctx, simConfig, values) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;

        ctx.clearRect(0, 0, width, height);

        switch (simConfig.type) {
            case 'ohms-law':
                drawOhmsLaw(ctx, values);
                break;
            case 'series-circuit':
                drawSeriesCircuit(ctx, values);
                break;
            case 'parallel-circuit':
                drawParallelCircuit(ctx, values);
                break;
            default:
                drawGenericCircuit(ctx);
        }
    }

    /**
     * Draw Ohm's Law circuit
     */
    function drawOhmsLaw(ctx, values) {
        const voltage = values.voltage || 12;
        const resistance = values.resistance || 100;
        const current = (voltage / resistance).toFixed(3);

        const height = ctx.canvas.height;

        // Battery
        ctx.fillStyle = '#64748b';
        ctx.fillRect(50, height / 2 - 30, 30, 60);
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(45, height / 2 - 20, 10, 15);

        // Wires
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(80, height / 2);
        ctx.lineTo(700, height / 2);
        ctx.stroke();

        // Resistor
        ctx.fillStyle = '#22c55e';
        ctx.fillRect(350, height / 2 - 25, 80, 50);
        ctx.fillStyle = '#fff';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${resistance}Ω`, 390, height / 2 + 5);

        // Labels
        ctx.fillStyle = '#1e293b';
        ctx.font = '12px sans-serif';
        ctx.fillText(`${voltage}V`, 50, height / 2 - 45);
        ctx.fillText(`${current}A`, 720, height / 2);

        // Update results
        document.getElementById('result-current').textContent = `${current} A`;
    }

    /**
     * Draw series circuit
     */
    function drawSeriesCircuit(ctx, values) {
        const vsource = values.vsource || 12;
        const r1 = values.r1 || 100;
        const r2 = values.r2 || 200;
        const r3 = values.r3 || 300;
        const rTotal = r1 + r2 + r3;
        const current = (vsource / rTotal * 1000).toFixed(1);

        const height = ctx.canvas.height;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;

        // Main loop
        ctx.beginPath();
        ctx.rect(100, height / 2 - 80, 600, 160);
        ctx.stroke();

        // Resistors
        ctx.fillStyle = '#22c55e';
        const positions = [200, 350, 500];
        const values_ = [r1, r2, r3];

        values_.forEach((val, idx) => {
            ctx.fillRect(positions[idx], height / 2 - 25, 50, 50);
            ctx.fillStyle = '#fff';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`R${idx + 1}`, positions[idx] + 25, height / 2 + 5);
            ctx.fillStyle = '#22c55e';
        });

        // Labels
        ctx.fillStyle = '#1e293b';
        ctx.font = '12px sans-serif';
        ctx.fillText(`${vsource}V`, 100, height / 2 - 95);

        // Update results
        document.getElementById('result-r_total').textContent = `${rTotal} Ω`;
        document.getElementById('result-current').textContent = `${current} mA`;
    }

    /**
     * Draw parallel circuit
     */
    function drawParallelCircuit(ctx, values) {
        const vsource = values.vsource || 12;
        const r1 = values.r1 || 100;
        const r2 = values.r2 || 200;
        const r3 = values.r3 || 300;
        const rTotal = (1 / (1 / r1 + 1 / r2 + 1 / r3)).toFixed(1);

        const height = ctx.canvas.height;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;

        // Main bus
        ctx.beginPath();
        ctx.moveTo(100, height / 2);
        ctx.lineTo(700, height / 2);
        ctx.stroke();

        // Branch 1
        ctx.beginPath();
        ctx.moveTo(200, height / 2);
        ctx.lineTo(200, height / 2 + 80);
        ctx.lineTo(350, height / 2 + 80);
        ctx.lineTo(350, height / 2);
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

        // Resistors
        ctx.fillStyle = '#22c55e';
        ctx.fillRect(250, height / 2 + 65, 40, 30);
        ctx.fillRect(380, height / 2 - 95, 40, 30);
        ctx.fillRect(530, height / 2 + 65, 40, 30);

        ctx.fillStyle = '#fff';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('R1', 270, height / 2 + 83);
        ctx.fillText('R2', 400, height / 2 - 77);
        ctx.fillText('R3', 550, height / 2 + 83);

        // Update results
        document.getElementById('result-r_total').textContent = `${rTotal} Ω`;
    }

    /**
     * Draw generic circuit
     */
    function drawGenericCircuit(ctx) {
        const height = ctx.canvas.height;

        ctx.fillStyle = '#64748b';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Interactive Simulation', ctx.canvas.width / 2, height / 2);
    }

    /**
     * Update simulation value display
     */
    function updateSimulationValue(name, value) {
        const displayEl = document.getElementById(`${name}-value`);
        if (displayEl) {
            displayEl.textContent = value;
        }

        // Trigger recalculation
        runSimulation();
    }

    /**
     * Run simulation with current values
     */
    async function runSimulation() {
        const container = document.querySelector('.simulation-container');
        if (!container) return;

        const simConfig = window.currentSimulation;
        if (!simConfig) return;

        // Collect current values
        const values = {};
        simConfig.controls.forEach(control => {
            const el = document.getElementById(control.name);
            if (el) {
                values[control.name] = parseFloat(el.value);
            }
        });

        // Calculate and display results
        const canvasId = simConfig.name.replace(/\\s+/g, '-').toLowerCase();
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            drawSimulation(ctx, simConfig, values);
        }
    }

    /**
     * Reset simulation to defaults
     */
    function resetSimulation() {
        const simConfig = window.currentSimulation;
        if (!simConfig) return;

        simConfig.controls.forEach(control => {
            const el = document.getElementById(control.name);
            if (el) {
                el.value = control.default;
                document.getElementById(`${control.name}-value`).textContent =
                    `${control.default} ${control.unit || ''}`;
            }
        });

        runSimulation();
    }

    /**
     * Render practice problems
     */
    function renderProblems(problems, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = problems.map((problem, idx) => `
            <div class="problem-card border rounded-lg p-4 mb-4" id="problem-${problem.id}">
                <div class="flex items-start justify-between mb-3">
                    <h3 class="font-semibold">${problem.title}</h3>
                    <span class="text-xs px-2 py-1 bg-${problem.difficulty === 'Easy' ? 'green' : problem.difficulty === 'Medium' ? 'yellow' : 'red'}-100 rounded">
                        ${problem.difficulty}
                    </span>
                </div>
                <p class="text-gray-700 dark:text-gray-300 mb-4">${problem.description}</p>
                
                ${problem.problem_type === 'multiple-choice' ? renderMultipleChoice(problem, idx) : renderNumericalInput(problem, idx)}
                
                <div id="feedback-${problem.id}" class="mt-3"></div>
            </div>
        `).join('');
    }

    /**
     * Render multiple choice problem
     */
    function renderMultipleChoice(problem, idx) {
        return `
            <div class="space-y-2 mb-4">
                ${problem.choices.map(choice => `
                    <label class="quiz-option flex items-center gap-3 p-3 border rounded-lg cursor-pointer">
                        <input type="radio" name="problem-${problem.id}" value="${choice.value}">
                        <span>${choice.text}</span>
                    </label>
                `).join('')}
            </div>
            <button onclick="ArticleLoader.submitMultipleChoice(${problem.id})" class="btn btn-primary">
                Submit Answer
            </button>
        `;
    }

    /**
     * Render numerical input problem
     */
    function renderNumericalInput(problem, idx) {
        return `
            <div class="flex gap-2 mb-4">
                <input type="number" id="answer-${problem.id}" 
                    class="flex-1 px-3 py-2 border rounded-lg"
                    placeholder="Enter your answer">
                <button onclick="ArticleLoader.submitNumerical(${problem.id})" class="btn btn-primary">
                    Check
                </button>
            </div>
        `;
    }

    /**
     * Submit multiple choice answer
     */
    async function submitMultipleChoice(problemId) {
        const selected = document.querySelector(`input[name="problem-${problemId}"]:checked`);
        if (!selected) {
            alert('Please select an answer');
            return;
        }

        const result = await checkAnswer(problemId, selected.value);
        showFeedback(problemId, result);
    }

    /**
     * Submit numerical answer
     */
    async function submitNumerical(problemId) {
        const answerEl = document.getElementById(`answer-${problemId}`);
        const answer = answerEl.value;

        if (!answer) {
            alert('Please enter an answer');
            return;
        }

        const result = await checkAnswer(problemId, answer);
        showFeedback(problemId, result);
    }

    /**
     * Show feedback for answer
     */
    function showFeedback(problemId, result) {
        const feedbackEl = document.getElementById(`feedback-${problemId}`);
        if (!feedbackEl) return;

        feedbackEl.innerHTML = result.correct
            ? `<div class="p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-lg">
                <i class="fas fa-check-circle mr-2"></i> Correct!
               </div>`
            : `<div class="p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-lg">
                <i class="fas fa-times-circle mr-2"></i> Incorrect. 
                The correct answer is: ${result.correct_answer}
                ${result.explanation ? `<p class="mt-2">${result.explanation}</p>` : ''}
               </div>`;
    }

    // Public API
    return {
        init,
        loadLessonById,
        loadLessonBySlug,
        loadArticle,
        renderArticle,
        loadSimulations,
        loadProblems,
        checkAnswer,
        calculateSimulation,
        updateProgress,
        getProgress,
        addBookmark,
        removeBookmark,
        getDisciplines,
        getChapters,
        getLessons,
        renderLessonComplete,
        updateSimulationValue,
        runSimulation,
        resetSimulation,
        submitMultipleChoice,
        submitNumerical
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ArticleLoader;
}