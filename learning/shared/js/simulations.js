/**
 * Interactive Electrical Circuit Simulation Module
 * Learning Platform - EngiSuite Analytics
 * 
 * Features:
 * - Ohm's Law Calculator
 * - Series Circuit Simulator
 * - Parallel Circuit Simulator
 * - Phasor Diagram (AC)
 * - Logic Gate Simulator
 * 
 * @version 1.0.0
 * @author EngiSuite Analytics Team
 */

(function (global) {
    'use strict';

    // ============================================
    // SIMULATION CONTROLLER (MVC Controller)
    // ============================================
    const SimulationController = {
        activeSimulation: null,
        simulations: {},
        shortcuts: {
            'o': 'ohmsLaw',
            's': 'seriesCircuit',
            'p': 'parallelCircuit',
            'a': 'phasorDiagram',
            'l': 'logicGates',
            '?': 'toggleHelp',
            'e': 'exportData',
            'r': 'reset'
        },

        init() {
            this.simulations = {
                ohmsLaw: new OhmsLawSimulation(),
                seriesCircuit: new SeriesCircuitSimulation(),
                parallelCircuit: new ParallelCircuitSimulation(),
                phasorDiagram: new PhasorDiagramSimulation(),
                logicGates: new LogicGateSimulation()
            };
            this.bindGlobalEvents();
            this.initHelpSystem();
        },

        bindGlobalEvents() {
            document.addEventListener('keydown', (e) => {
                if (e.key === '?' || (e.key === '/' && e.shiftKey)) {
                    e.preventDefault();
                    this.toggleHelp();
                }
                if (e.key === 'e' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    this.exportActiveData();
                }
                if (e.key === 'r' && this.activeSimulation) {
                    this.simulations[this.activeSimulation].reset();
                }
            });
        },

        initHelpSystem() {
            this.helpData = {
                general: {
                    title: 'Keyboard Shortcuts',
                    shortcuts: [
                        { key: '?', toggle: 'Show/Hide this help' },
                        { key: '1-5', action: 'Switch simulations' },
                        { key: 'E', action: 'Export simulation data' },
                        { key: 'R', action: 'Reset current simulation' },
                        { key: '↑/↓', action: 'Increase/Decrease values' }
                    ]
                }
            };
        },

        toggleHelp() {
            const helpPanel = document.getElementById('simulation-help-panel');
            if (helpPanel) {
                helpPanel.classList.toggle('hidden');
            } else {
                this.showHelp();
            }
        },

        showHelp() {
            const existing = document.getElementById('simulation-help-panel');
            if (existing) existing.remove();

            const panel = document.createElement('div');
            panel.id = 'simulation-help-panel';
            panel.className = 'simulation-help-panel';
            panel.innerHTML = this.generateHelpHTML();
            document.body.appendChild(panel);

            setTimeout(() => panel.classList.add('visible'), 10);
        },

        generateHelpHTML() {
            let html = `
                <div class="help-content">
                    <div class="help-header">
                        <h3>📚 Simulation Help</h3>
                        <button class="help-close" onclick="SimulationController.hideHelp()">×</button>
                    </div>
                    <div class="help-tabs">
                        <button class="help-tab active" data-tab="general">General</button>
                        <button class="help-tab" data-tab="${this.activeSimulation || 'general'}">Current Sim</button>
                    </div>
                    <div class="help-body">
            `;

            // General shortcuts
            html += '<div class="help-section" id="help-general">';
            html += '<h4>Keyboard Shortcuts</h4><ul>';
            this.helpData.general.shortcuts.forEach(s => {
                html += `<li><kbd>${s.key}</kbd> - ${s.action}</li>`;
            });
            html += '</ul></div>';

            // Simulation specific help
            if (this.activeSimulation && this.simulations[this.activeSimulation]) {
                html += `<div class="help-section" id="help-${this.activeSimulation}">`;
                html += this.simulations[this.activeSimulation].getHelpContent();
                html += '</div>';
            }

            html += '</div></div>';
            return html;
        },

        hideHelp() {
            const panel = document.getElementById('simulation-help-panel');
            if (panel) {
                panel.classList.remove('visible');
                setTimeout(() => panel.remove(), 300);
            }
        },

        exportActiveData() {
            if (this.activeSimulation && this.simulations[this.activeSimulation]) {
                this.simulations[this.activeSimulation].exportData();
            }
        },

        setActiveSimulation(name) {
            this.activeSimulation = name;
            Object.keys(this.simulations).forEach(key => {
                const container = document.getElementById(`${key}-container`);
                if (container) {
                    container.style.display = key === name ? 'block' : 'none';
                }
            });
            this.hideHelp();
        }
    };

    // ============================================
    // BASE SIMULATION CLASS
    // ============================================
    class BaseSimulation {
        constructor(config = {}) {
            this.canvas = null;
            this.ctx = null;
            this.container = null;
            this.isRunning = false;
            this.animationFrame = null;
            this.data = {};
            this.listeners = {};
            this.config = Object.assign({
                canvasId: null,
                containerId: null,
                width: 800,
                height: 500
            }, config);
        }

        init(container) {
            this.container = container || document.getElementById(this.config.containerId);
            if (!this.container) return false;

            this.createCanvas();
            this.createControls();
            this.bindEvents();
            this.reset();
            return true;
        }

        createCanvas() {
            this.canvas = document.createElement('canvas');
            this.canvas.id = this.config.canvasId || `${this.name}-canvas`;
            this.canvas.width = this.config.width;
            this.canvas.height = this.config.height;
            this.canvas.className = 'simulation-canvas';
            this.container.appendChild(this.canvas);
            this.ctx = this.canvas.getContext('2d');
        }

        createControls() {
            // Override in subclasses
        }

        bindEvents() {
            // Override in subclasses
        }

        start() {
            if (!this.isRunning) {
                this.isRunning = true;
                this.animate();
            }
        }

        stop() {
            this.isRunning = false;
            if (this.animationFrame) {
                cancelAnimationFrame(this.animationFrame);
            }
        }

        animate() {
            if (!this.isRunning) return;
            this.update();
            this.draw();
            this.animationFrame = requestAnimationFrame(() => this.animate());
        }

        update() {
            // Override in subclasses
        }

        draw() {
            // Override in subclasses
        }

        reset() {
            this.stop();
            this.data = this.getInitialData();
            this.createControls();
            this.draw();
        }

        getInitialData() {
            return {};
        }

        getHelpContent() {
            return '<p>No specific help available for this simulation.</p>';
        }

        exportData() {
            const exportObj = {
                simulation: this.name,
                timestamp: new Date().toISOString(),
                data: this.data
            };
            const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.name}-simulation-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            this.showNotification('Data exported successfully!');
        }

        showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'simulation-notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => notification.remove(), 300);
            }, 2000);
        }

        createSlider(name, label, min, max, value, step = 1, unit = '') {
            const wrapper = document.createElement('div');
            wrapper.className = 'control-slider';
            wrapper.innerHTML = `
                <label for="${name}">${label}: <span class="value" id="${name}-value">${value}${unit}</span></label>
                <input type="range" id="${name}" name="${name}" 
                       min="${min}" max="${max}" value="${value}" step="${step}">
            `;
            return wrapper;
        }

        createButton(label, action, className = '') {
            const btn = document.createElement('button');
            btn.className = `simulation-btn ${className}`;
            btn.textContent = label;
            btn.addEventListener('click', action);
            return btn;
        }

        addDragDropTarget(container) {
            container.addEventListener('dragover', (e) => e.preventDefault());
            container.addEventListener('drop', (e) => {
                e.preventDefault();
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                this.handleDrop(data);
            });
        }

        handleDrop(data) {
            // Override in subclasses
        }
    }

    // ============================================
    // OHM'S LAW SIMULATION
    // ============================================
    class OhmsLawSimulation extends BaseSimulation {
        constructor() {
            super({
                canvasId: 'ohmslaw-canvas',
                containerId: 'ohmslaw-container',
                width: 800,
                height: 450
            });
            this.name = 'ohmsLaw';
            this.formula = 'V = I × R';
        }

        getInitialData() {
            return {
                voltage: 12,
                current: 0.5,
                resistance: 24,
                power: 6,
                mode: 'voltage' // which value is being edited
            };
        }

        createControls() {
            const controls = document.createElement('div');
            controls.className = 'ohmslaw-controls';
            controls.innerHTML = `
                <div class="formula-display">${this.formula}</div>
                <div class="sliders-container">
                    ${this.createSlider('voltage', 'Voltage (V)', 0, 240, 12, 0.1, 'V').outerHTML}
                    ${this.createSlider('current', 'Current (I)', 0, 10, 0.5, 0.01, 'A').outerHTML}
                    ${this.createSlider('resistance', 'Resistance (R)', 1, 10000, 24, 1, 'Ω').outerHTML}
                </div>
                <div class="mode-selector">
                    <label>Calculate: </label>
                    <select id="ohmslaw-mode">
                        <option value="voltage">Voltage</option>
                        <option value="current">Current</option>
                        <option value="resistance">Resistance</option>
                    </select>
                </div>
                <div class="results-display">
                    <div class="result-item">
                        <span class="label">Voltage:</span>
                        <span class="value" id="result-voltage">12.00 V</span>
                    </div>
                    <div class="result-item">
                        <span class="label">Current:</span>
                        <span class="value" id="result-current">0.50 A</span>
                    </div>
                    <div class="result-item">
                        <span class="label">Resistance:</span>
                        <span class="value" id="result-resistance">24.00 Ω</span>
                    </div>
                    <div class="result-item highlight">
                        <span class="label">Power:</span>
                        <span class="value" id="result-power">6.00 W</span>
                    </div>
                </div>
            `;
            this.container.appendChild(controls);
        }

        bindEvents() {
            const voltageSlider = document.getElementById('voltage');
            const currentSlider = document.getElementById('current');
            const resistanceSlider = document.getElementById('resistance');
            const modeSelect = document.getElementById('ohmslaw-mode');

            const updateFromSlider = (source) => {
                const mode = modeSelect.value;
                if (mode === 'voltage') {
                    this.data.voltage = parseFloat(voltageSlider.value);
                    this.data.current = this.data.voltage / this.data.resistance;
                    this.data.power = this.data.voltage * this.data.current;
                } else if (mode === 'current') {
                    this.data.current = parseFloat(currentSlider.value);
                    this.data.voltage = this.data.current * this.data.resistance;
                    this.data.power = this.data.voltage * this.data.current;
                } else {
                    this.data.resistance = parseFloat(resistanceSlider.value);
                    this.data.voltage = this.data.current * this.data.resistance;
                    this.data.power = this.data.voltage * this.data.current;
                }
                this.updateDisplay();
                this.draw();
            };

            voltageSlider.addEventListener('input', () => updateFromSlider('voltage'));
            currentSlider.addEventListener('input', () => updateFromSlider('current'));
            resistanceSlider.addEventListener('input', () => updateFromSlider('resistance'));
            modeSelect.addEventListener('change', () => {
                const mode = modeSelect.value;
                if (mode === 'voltage') {
                    voltageSlider.disabled = false;
                    currentSlider.disabled = true;
                    resistanceSlider.disabled = true;
                } else if (mode === 'current') {
                    voltageSlider.disabled = true;
                    currentSlider.disabled = false;
                    resistanceSlider.disabled = true;
                } else {
                    voltageSlider.disabled = true;
                    currentSlider.disabled = true;
                    resistanceSlider.disabled = false;
                }
            });

            // Initial state
            modeSelect.dispatchEvent(new Event('change'));
        }

        updateDisplay() {
            document.getElementById('voltage-value').textContent = this.data.voltage.toFixed(1) + 'V';
            document.getElementById('current-value').textContent = this.data.current.toFixed(2) + 'A';
            document.getElementById('resistance-value').textContent = this.formatResistance(this.data.resistance) + 'Ω';

            document.getElementById('result-voltage').textContent = this.data.voltage.toFixed(2) + ' V';
            document.getElementById('result-current').textContent = this.data.current.toFixed(2) + ' A';
            document.getElementById('result-resistance').textContent = this.formatResistance(this.data.resistance) + ' Ω';
            document.getElementById('result-power').textContent = this.data.power.toFixed(2) + ' W';
        }

        formatResistance(ohms) {
            if (ohms >= 1000) {
                return (ohms / 1000).toFixed(1) + 'k';
            }
            return ohms.toFixed(0);
        }

        draw() {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;

            // Clear canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, w, h);

            // Draw circuit diagram
            this.drawCircuit(w, h);

            // Draw animated resistor
            this.drawResistor(w / 2, h / 2);

            // Draw electron flow
            this.drawElectronFlow();
        }

        drawCircuit(w, h) {
            const ctx = this.ctx;
            const margin = 60;
            const circuitY = h / 2 + 80;

            ctx.strokeStyle = '#4a9eff';
            ctx.lineWidth = 3;
            ctx.setLineDash([]);

            // Battery
            ctx.beginPath();
            ctx.rect(margin, circuitY - 20, 40, 40);
            ctx.stroke();

            // Positive terminal
            ctx.beginPath();
            ctx.moveTo(margin + 8, circuitY - 5);
            ctx.lineTo(margin + 32, circuitY - 5);
            ctx.stroke();

            // Negative terminal
            ctx.fillStyle = '#ff6b6b';
            ctx.fillRect(margin + 10, circuitY + 5, 24, 3);

            // Wires
            ctx.strokeStyle = '#4a9eff';
            ctx.beginPath();
            // Top wire
            ctx.moveTo(margin + 40, circuitY);
            ctx.lineTo(w - margin - 80, circuitY);
            ctx.stroke();

            // Bottom wire
            ctx.beginPath();
            ctx.moveTo(margin, circuitY + 20);
            ctx.lineTo(w - margin - 80, circuitY + 20);
            ctx.stroke();

            // Right connection to resistor
            ctx.beginPath();
            ctx.moveTo(w - margin - 80, circuitY);
            ctx.lineTo(w - margin - 80, circuitY + 10);
            ctx.stroke();

            // Ammeter circle
            const ammeterX = margin + 30;
            ctx.beginPath();
            ctx.arc(ammeterX, circuitY + 10, 15, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillStyle = '#1a1a2e';
            ctx.fill();
            ctx.fillStyle = '#fff';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('A', ammeterX, circuitY + 14);

            // Voltmeter connection point
            ctx.beginPath();
            ctx.arc(w - margin - 80, circuitY + 10, 8, 0, Math.PI * 2);
            ctx.stroke();
        }

        drawResistor(x, y) {
            const ctx = this.ctx;
            const width = 120;
            const height = 40;
            const powerRatio = Math.min(this.data.power / 100, 1);

            // Glow effect based on power
            const glowIntensity = 20 + powerRatio * 50;
            ctx.shadowBlur = glowIntensity;
            ctx.shadowColor = `rgba(255, ${150 - powerRatio * 100}, 50, 1)`;

            // Resistor body
            ctx.fillStyle = `rgb(${150 + powerRatio * 50}, ${150 - powerRatio * 50}, ${150 - powerRatio * 50})`;
            ctx.beginPath();
            ctx.roundRect(x - width / 2, y - height / 2, width, height, 5);
            ctx.fill();

            // Resistor bands
            const bandColors = ['#8B4513', '#8B4513', '#FF0000', '#DAA520']; // 24k ohm
            const bandStart = x - width / 2 + 15;
            const bandWidth = 8;
            const bandGap = 8;

            ctx.shadowBlur = 0;
            bandColors.forEach((color, i) => {
                ctx.fillStyle = color;
                ctx.fillRect(bandStart + i * (bandWidth + bandGap), y - height / 2 + 5, bandWidth, height - 10);
            });

            // Terminals
            ctx.strokeStyle = '#888';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x - width / 2 - 20, y);
            ctx.lineTo(x - width / 2, y);
            ctx.moveTo(x + width / 2, y);
            ctx.lineTo(x + width / 2 + 20, y);
            ctx.stroke();
        }

        drawElectronFlow() {
            const ctx = this.ctx;
            const speed = this.data.current * 10;
            const time = Date.now() / 1000;
            const w = this.canvas.width;
            const h = this.canvas.height;
            const circuitY = h / 2 + 80;
            const margin = 60;

            ctx.fillStyle = '#00ff88';

            // Draw electrons on top wire (moving right)
            for (let i = 0; i < 8; i++) {
                const x = margin + 50 + ((i * 80 + time * speed * 30) % (w - margin * 2 - 100));
                if (x < w - margin - 80) {
                    ctx.beginPath();
                    ctx.arc(x, circuitY, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // Draw electrons on bottom wire (moving left)
            for (let i = 0; i < 8; i++) {
                const x = w - margin - 10 - ((i * 80 + time * speed * 30) % (w - margin * 2 - 100));
                if (x > margin) {
                    ctx.beginPath();
                    ctx.arc(x, circuitY + 20, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }

        getHelpContent() {
            return `
                <h4>Ohm's Law Calculator</h4>
                <p>The fundamental relationship: V = I × R</p>
                <ul>
                    <li><strong>Voltage (V)</strong>: Electrical potential difference, measured in Volts</li>
                    <li><strong>Current (I)</strong>: Flow of electrons, measured in Amperes</li>
                    <li><strong>Resistance (R)</strong>: Opposition to current flow, measured in Ohms</li>
                    <li><strong>Power (P)</strong>: P = V × I, measured in Watts</li>
                </ul>
                <p><strong>Tips:</strong> Adjust any slider to see real-time updates. The resistor glows brighter with more power dissipation.</p>
            `;
        }
    }

    // ============================================
    // SERIES CIRCUIT SIMULATION
    // ============================================
    class SeriesCircuitSimulation extends BaseSimulation {
        constructor() {
            super({
                canvasId: 'series-canvas',
                containerId: 'series-container',
                width: 800,
                height: 500
            });
            this.name = 'seriesCircuit';
            this.resistors = [];
            this.draggedResistor = null;
            this.totalResistance = 0;
            this.totalCurrent = 0;
            this.sourceVoltage = 12;
        }

        getInitialData() {
            return {
                voltage: 12,
                resistors: [
                    { id: 1, value: 100, x: 300, y: 200 },
                    { id: 2, value: 200, x: 300, y: 300 },
                    { id: 3, value: 300, x: 300, y: 400 }
                ]
            };
        }

        createControls() {
            const controls = document.createElement('div');
            controls.className = 'series-controls';
            controls.innerHTML = `
                <div class="circuit-tools">
                    <button class="tool-btn" data-tool="add-resistor" title="Add Resistor">
                        <span>+R</span> Add Resistor
                    </button>
                    <button class="tool-btn" data-tool="remove-resistor" title="Remove Selected">
                        <span>-R</span> Remove Resistor
                    </button>
                    <button class="tool-btn" data-tool="select" title="Select Resistor">
                        <span>↖</span> Select/Move
                    </button>
                </div>
                ${this.createSlider('source-voltage', 'Source Voltage', 0, 240, 12, 0.5, 'V').outerHTML}
                <div class="circuit-stats">
                    <div class="stat">
                        <span class="stat-label">Total R:</span>
                        <span class="stat-value" id="series-total-r">600 Ω</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Current:</span>
                        <span class="stat-value" id="series-current">20.00 mA</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Power:</span>
                        <span class="stat-value" id="series-power">0.24 W</span>
                    </div>
                </div>
                <div class="kvl-feedback" id="kvl-feedback">
                    KVL Check: ∑V = 0V (Input - Drops = 0V)
                </div>
                <div class="resistor-list" id="resistor-list"></div>
            `;
            this.container.appendChild(controls);
            this.updateResistorList();
        }

        bindEvents() {
            // Tool buttons
            document.querySelectorAll('[data-tool]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const tool = e.currentTarget.dataset.tool;
                    this.handleTool(tool);
                });
            });

            // Voltage slider
            const voltageSlider = document.getElementById('source-voltage');
            voltageSlider.addEventListener('input', (e) => {
                this.data.voltage = parseFloat(e.target.value);
                this.updateCalculations();
                this.draw();
            });

            // Canvas drag events
            this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
            this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
            this.canvas.addEventListener('mouseleave', (e) => this.handleMouseUp(e));
        }

        handleTool(tool) {
            if (tool === 'add-resistor') {
                const newId = Date.now();
                this.data.resistors.push({
                    id: newId,
                    value: 100,
                    x: 100 + Math.random() * 200,
                    y: 150 + this.data.resistors.length * 80
                });
                this.updateResistorList();
                this.updateCalculations();
                this.draw();
            } else if (tool === 'remove-resistor' && this.selectedResistor) {
                this.data.resistors = this.data.resistors.filter(r => r.id !== this.selectedResistor.id);
                this.selectedResistor = null;
                this.updateResistorList();
                this.updateCalculations();
                this.draw();
            }
        }

        handleMouseDown(e) {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Check if clicking on a resistor
            for (const resistor of this.data.resistors) {
                if (x >= resistor.x - 30 && x <= resistor.x + 30 &&
                    y >= resistor.y - 15 && y <= resistor.y + 15) {
                    this.draggedResistor = resistor;
                    this.selectedResistor = resistor;
                    break;
                }
            }
        }

        handleMouseMove(e) {
            if (!this.draggedResistor) return;
            const rect = this.canvas.getBoundingClientRect();
            this.draggedResistor.x = e.clientX - rect.left;
            this.draggedResistor.y = e.clientY - rect.top;
            this.draw();
        }

        handleMouseUp() {
            this.draggedResistor = null;
        }

        updateResistorList() {
            const list = document.getElementById('resistor-list');
            if (!list) return;

            list.innerHTML = '<h4>Resistors:</h4>';
            this.data.resistors.forEach((r, i) => {
                const item = document.createElement('div');
                item.className = 'resistor-item';
                item.innerHTML = `
                    <span>R${i + 1}:</span>
                    <input type="number" value="${r.value}" min="1" max="100000" step="10">
                    <span>Ω</span>
                    <button class="remove-btn" data-id="${r.id}">×</button>
                `;
                item.querySelector('input').addEventListener('change', (e) => {
                    r.value = parseFloat(e.target.value) || 100;
                    this.updateCalculations();
                    this.draw();
                });
                item.querySelector('.remove-btn').addEventListener('click', () => {
                    this.data.resistors = this.data.resistors.filter(res => res.id !== r.id);
                    this.updateResistorList();
                    this.updateCalculations();
                    this.draw();
                });
                list.appendChild(item);
            });
        }

        updateCalculations() {
            // Calculate total resistance (series)
            this.totalResistance = this.data.resistors.reduce((sum, r) => sum + r.value, 0);

            // Calculate current (I = V / R)
            this.totalCurrent = this.totalResistance > 0 ? this.data.voltage / this.totalResistance : 0;

            // Calculate total power (P = V² / R)
            const totalPower = this.totalResistance > 0 ? Math.pow(this.data.voltage, 2) / this.totalResistance : 0;

            // Update display
            document.getElementById('series-total-r').textContent = this.formatResistance(this.totalResistance);
            document.getElementById('series-current').textContent = (this.totalCurrent * 1000).toFixed(2) + ' mA';
            document.getElementById('series-power').textContent = totalPower.toFixed(3) + ' W';

            // KVL validation
            let voltageDrops = 0;
            this.data.resistors.forEach(r => {
                voltageDrops += this.totalCurrent * r.value;
            });
            const kvlRemainder = this.data.voltage - voltageDrops;
            const kvlEl = document.getElementById('kvl-feedback');
            kvlEl.textContent = `KVL Check: ∑V = ${kvlRemainder.toFixed(3)}V (Input ${this.data.voltage}V - Drops ${voltageDrops.toFixed(3)}V = ${kvlRemainder.toFixed(3)}V)`;
            kvlEl.className = `kvl-feedback ${Math.abs(kvlRemainder) < 0.01 ? 'valid' : 'invalid'}`;
        }

        formatResistance(ohms) {
            if (ohms >= 1000000) return (ohms / 1000000).toFixed(2) + 'M';
            if (ohms >= 1000) return (ohms / 1000).toFixed(1) + 'k';
            return ohms.toFixed(0) + 'Ω';
        }

        draw() {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;

            // Clear canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, w, h);

            // Draw circuit wires
            this.drawCircuitWires(w, h);

            // Draw resistors
            this.data.resistors.forEach((r, i) => {
                this.drawResistor(r.x, r.y, r.value, i + 1, r === this.selectedResistor);
            });

            // Draw ammeter
            this.drawAmmeter(100, h / 2, this.totalCurrent);

            // Draw voltmeter
            this.drawVoltmeter(600, h / 2, this.data.voltage);

            // Draw electron flow
            this.drawElectronFlow();
        }

        drawCircuitWires(w, h) {
            const ctx = this.ctx;
            const y = h / 2;

            ctx.strokeStyle = '#4a9eff';
            ctx.lineWidth = 3;
            ctx.setLineDash([]);

            // Main circuit loop
            ctx.beginPath();
            ctx.moveTo(100, y - 50);
            ctx.lineTo(100, 50);
            ctx.lineTo(650, 50);
            ctx.lineTo(650, y + 50);
            ctx.lineTo(100, y + 50);
            ctx.stroke();

            // Source symbol
            ctx.strokeStyle = '#ffcc00';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.rect(90, y - 65, 20, 30);
            ctx.stroke();
            ctx.fillStyle = '#ffcc00';
            ctx.font = 'bold 12px Arial';
            ctx.fillText('+', 100, y - 45);
            ctx.fillText('-', 100, y + 10);
        }

        drawResistor(x, y, value, number, isSelected) {
            const ctx = this.ctx;
            const w = 60;
            const h = 24;

            if (isSelected) {
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#00ff88';
            } else {
                ctx.shadowBlur = 0;
            }

            // Resistor body
            ctx.fillStyle = '#d4a574';
            ctx.beginPath();
            ctx.roundRect(x - w / 2, y - h / 2, w, h, 3);
            ctx.fill();

            // Color bands
            const bands = this.getBandColors(value);
            const bandWidth = 6;
            const bandStart = x - w / 2 + 10;
            bands.forEach((color, i) => {
                ctx.fillStyle = color;
                ctx.fillRect(bandStart + i * (bandWidth + 4), y - h / 2 + 4, bandWidth, h - 8);
            });

            ctx.shadowBlur = 0;

            // Resistor label
            ctx.fillStyle = '#fff';
            ctx.font = '11px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`R${number}`, x, y - 18);
            ctx.fillText(this.formatResistance(value), x, y + h / 2 + 14);
        }

        getBandColors(value) {
            const firstDigit = String(value).charAt(0);
            const secondDigit = String(value).charAt(1) || 0;
            const multiplier = Math.round(Math.log10(value / (firstDigit * 10 + secondDigit)));

            const colors = {
                '0': '#000', '1': '#8B4513', '2': '#FF0000', '3': '#FFA500',
                '4': '#FFFF00', '5': '#00FF00', '6': '#0000FF', '7': '#8B008B',
                '8': '#808080', '9': '#FFFFFF'
            };

            return [colors[firstDigit] || '#000', colors[secondDigit] || '#000', '#DAA520'];
        }

        drawAmmeter(x, y, current) {
            const ctx = this.ctx;

            ctx.beginPath();
            ctx.arc(x, y, 30, 0, Math.PI * 2);
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 3;
            ctx.stroke();
            ctx.fillStyle = '#1a1a2e';
            ctx.fill();

            ctx.fillStyle = '#fff';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('A', x, y + 5);
            ctx.font = '10px Arial';
            ctx.fillText(`${(current * 1000).toFixed(1)}mA`, x, y + 18);
        }

        drawVoltmeter(x, y, voltage) {
            const ctx = this.ctx;

            ctx.beginPath();
            ctx.arc(x, y, 30, 0, Math.PI * 2);
            ctx.strokeStyle = '#ff6b6b';
            ctx.lineWidth = 3;
            ctx.stroke();
            ctx.fillStyle = '#1a1a2e';
            ctx.fill();

            ctx.fillStyle = '#fff';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('V', x, y + 5);
            ctx.font = '10px Arial';
            ctx.fillText(`${voltage.toFixed(1)}V`, x, y + 18);
        }

        drawElectronFlow() {
            const ctx = this.ctx;
            const speed = this.totalCurrent * 5000;
            const time = Date.now() / 1000;
            const y = this.canvas.height / 2;
            const positions = [100, 250, 400, 550];

            ctx.fillStyle = '#00ff88';

            positions.forEach((baseX, colIndex) => {
                const count = colIndex === 0 || colIndex === 3 ? 3 : 1;
                for (let i = 0; i < count; i++) {
                    let x, direction;
                    if (colIndex === 0) {
                        x = baseX + ((time * speed + i * 30) % 100);
                        direction = 1;
                    } else if (colIndex === 1) {
                        x = baseX - 20;
                        direction = -1;
                    } else if (colIndex === 2) {
                        x = baseX + 20;
                        direction = 1;
                    } else {
                        x = baseX - ((time * speed + i * 30) % 100);
                        direction = -1;
                    }

                    const yOffset = (colIndex % 2 === 0) ? -25 : 25;
                    ctx.beginPath();
                    ctx.arc(x, y + yOffset, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            });
        }

        getHelpContent() {
            return `
                <h4>Series Circuit Simulator</h4>
                <p>In series circuits, components are connected end-to-end.</p>
                <ul>
                    <li><strong>Total Resistance</strong>: R_total = R₁ + R₂ + ... + Rₙ</li>
                    <li><strong>Current</strong>: Same through all components (I = V/R_total)</li>
                    <li><strong>Voltage Drop</strong>: V_drop = I × R (Kirchhoff's Voltage Law)</li>
                    <li><strong>KVL</strong>: Sum of all voltages = 0</li>
                </ul>
                <p><strong>Controls:</strong> Click "Add Resistor" to add components. Drag to reposition. Use the list to edit values.</p>
            `;
        }
    }

    // ============================================
    // PARALLEL CIRCUIT SIMULATION
    // ============================================
    class ParallelCircuitSimulation extends BaseSimulation {
        constructor() {
            super({
                canvasId: 'parallel-canvas',
                containerId: 'parallel-container',
                width: 800,
                height: 500
            });
            this.name = 'parallelCircuit';
            this.branches = [];
            this.sourceVoltage = 12;
            this.electronParticles = [];
        }

        getInitialData() {
            return {
                voltage: 12,
                branches: [
                    { id: 1, resistance: 100, current: 0 },
                    { id: 2, resistance: 200, current: 0 },
                    { id: 3, resistance: 300, current: 0 }
                ]
            };
        }

        createControls() {
            const controls = document.createElement('div');
            controls.className = 'parallel-controls';
            controls.innerHTML = `
                <div class="parallel-tools">
                    <button class="tool-btn" id="add-branch">
                        <span>+B</span> Add Branch
                    </button>
                    <button class="tool-btn" id="remove-branch">
                        <span>-B</span> Remove Branch
                    </button>
                </div>
                ${this.createSlider('parallel-voltage', 'Source Voltage', 0, 240, 12, 0.5, 'V').outerHTML}
                <div class="parallel-stats">
                    <div class="stat">
                        <span class="stat-label">Eq. Resistance:</span>
                        <span class="stat-value" id="parallel-eq-r">54.55 Ω</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Current:</span>
                        <span class="stat-value" id="parallel-total-i">220.00 mA</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Source Power:</span>
                        <span class="stat-value" id="parallel-power">2.64 W</span>
                    </div>
                </div>
                <div class="branch-list" id="branch-list"></div>
            `;
            this.container.appendChild(controls);
            this.updateBranchList();
        }

        bindEvents() {
            document.getElementById('add-branch').addEventListener('click', () => {
                const newId = Date.now();
                this.data.branches.push({
                    id: newId,
                    resistance: 100,
                    current: 0
                });
                this.updateBranchList();
                this.updateCalculations();
                this.draw();
            });

            document.getElementById('remove-branch').addEventListener('click', () => {
                if (this.data.branches.length > 1) {
                    this.data.branches.pop();
                    this.updateBranchList();
                    this.updateCalculations();
                    this.draw();
                }
            });

            const voltageSlider = document.getElementById('parallel-voltage');
            voltageSlider.addEventListener('input', (e) => {
                this.data.voltage = parseFloat(e.target.value);
                this.updateCalculations();
                this.draw();
            });
        }

        updateBranchList() {
            const list = document.getElementById('branch-list');
            if (!list) return;

            list.innerHTML = '<h4>Branches:</h4>';
            this.data.branches.forEach((b, i) => {
                const item = document.createElement('div');
                item.className = 'branch-item';
                item.innerHTML = `
                    <span>B${i + 1}:</span>
                    <input type="number" value="${b.resistance}" min="1" max="100000" step="10">
                    <span>Ω</span>
                    <span class="branch-current">I: ${(b.current * 1000).toFixed(1)}mA</span>
                `;
                item.querySelector('input').addEventListener('change', (e) => {
                    b.resistance = parseFloat(e.target.value) || 100;
                    this.updateCalculations();
                    this.draw();
                });
                list.appendChild(item);
            });
        }

        updateCalculations() {
            const { voltage, branches } = this.data;

            // Calculate equivalent resistance: 1/Req = 1/R1 + 1/R2 + ...
            let conductanceSum = 0;
            let totalCurrent = 0;

            branches.forEach(b => {
                b.current = voltage / b.resistance; // I = V/R
                conductanceSum += 1 / b.resistance;
                totalCurrent += b.current;
            });

            const equivalentResistance = conductanceSum > 0 ? 1 / conductanceSum : 0;
            const totalPower = voltage * totalCurrent;

            document.getElementById('parallel-eq-r').textContent = this.formatResistance(equivalentResistance);
            document.getElementById('parallel-total-i').textContent = (totalCurrent * 1000).toFixed(2) + ' mA';
            document.getElementById('parallel-power').textContent = totalPower.toFixed(2) + ' W';

            // Update branch list
            this.updateBranchList();
        }

        formatResistance(ohms) {
            if (ohms >= 1000) return (ohms / 1000).toFixed(2) + 'kΩ';
            return ohms.toFixed(2) + 'Ω';
        }

        draw() {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;

            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, w, h);

            this.drawMainBus(w, h);
            this.drawBranches(w, h);
            this.drawSource(w, h);
            this.drawElectronFlow();
        }

        drawMainBus(w, h) {
            const ctx = this.ctx;
            const busY = h / 2;
            const margin = 80;

            ctx.strokeStyle = '#4a9eff';
            ctx.lineWidth = 4;

            // Top bus (positive)
            ctx.beginPath();
            ctx.moveTo(margin, busY - 100);
            ctx.lineTo(w - margin, busY - 100);
            ctx.stroke();

            // Bottom bus (negative)
            ctx.beginPath();
            ctx.moveTo(margin, busY + 100);
            ctx.lineTo(w - margin, busY + 100);
            ctx.stroke();

            // End terminators
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.arc(margin, busY - 100, 8, 0, Math.PI * 2);
            ctx.arc(margin, busY + 100, 8, 0, Math.PI * 2);
            ctx.fill();
        }

        drawBranches(w, h) {
            const { branches, voltage } = this.data;
            const margin = 100;
            const spacing = (w - margin * 2) / (branches.length + 1);
            const busY = h / 2;

            branches.forEach((branch, i) => {
                const x = margin + spacing * (i + 1);
                const branchCurrent = branch.current;
                const brightness = Math.min(branchCurrent * 200, 255);

                // Branch wires
                ctx.strokeStyle = '#4a9eff';
                ctx.lineWidth = 2;

                // Connection to top bus
                ctx.beginPath();
                ctx.moveTo(x, busY - 100);
                ctx.lineTo(x, busY - 40);
                ctx.stroke();

                // Connection to bottom bus
                ctx.beginPath();
                ctx.moveTo(x, busY + 40);
                ctx.lineTo(x, busY + 100);
                ctx.stroke();

                // Resistor in branch
                ctx.fillStyle = `rgb(${180}, ${150}, ${100})`;
                ctx.shadowBlur = brightness * 0.3;
                ctx.shadowColor = `rgba(255, ${150}, 50, 0.5)`;
                ctx.beginPath();
                ctx.roundRect(x - 25, busY - 30, 50, 60, 5);
                ctx.fill();
                ctx.shadowBlur = 0;

                // Resistor bands
                const bands = this.getBandColors(branch.resistance);
                const bandWidth = 5;
                bands.forEach((color, j) => {
                    ctx.fillStyle = color;
                    ctx.fillRect(x - 15 + j * (bandWidth + 3), busY - 15, bandWidth, 30);
                });

                // Current indicator
                ctx.fillStyle = '#00ff88';
                ctx.font = '11px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(`R${i + 1}`, x, busY - 35);
                ctx.fillText(`${this.formatResistance(branch.resistance)}`, x, busY + 45);

                // Current arrow
                this.drawCurrentArrow(x, busY, branchCurrent);
            });
        }

        drawCurrentArrow(x, y, current) {
            const ctx = this.ctx;
            const arrowLength = Math.min(Math.abs(current) * 30, 30);
            const direction = current > 0 ? 1 : -1;

            if (arrowLength < 2) return;

            ctx.strokeStyle = '#ff6b6b';
            ctx.fillStyle = '#ff6b6b';
            ctx.lineWidth = 2;

            // Draw arrow line
            ctx.beginPath();
            ctx.moveTo(x - arrowLength * direction, y - 60);
            ctx.lineTo(x, y - 60);
            ctx.stroke();

            // Draw arrow head
            ctx.beginPath();
            ctx.moveTo(x, y - 60);
            ctx.lineTo(x - 6 * direction, y - 65);
            ctx.lineTo(x - 6 * direction, y - 55);
            ctx.closePath();
            ctx.fill();
        }

        drawSource(w, h) {
            const ctx = this.ctx;
            const x = 50;
            const y = h / 2;

            // Battery symbol
            ctx.strokeStyle = '#ffcc00';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.rect(x - 15, y - 40, 30, 80);
            ctx.stroke();

            // Long line (positive)
            ctx.beginPath();
            ctx.moveTo(x - 15, y - 30);
            ctx.lineTo(x + 15, y - 30);
            ctx.stroke();

            // Short line (negative)
            ctx.strokeStyle = '#ff6b6b';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x - 5, y + 20);
            ctx.lineTo(x + 5, y + 20);
            ctx.stroke();

            // Labels
            ctx.fillStyle = '#ffcc00';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('+', x, y - 10);
            ctx.fillStyle = '#ff6b6b';
            ctx.fillText('-', x, y + 25);

            // Source info
            ctx.fillStyle = '#fff';
            ctx.font = '12px Arial';
            ctx.fillText(`${this.data.voltage}V`, x, y - 50);
        }

        drawElectronFlow() {
            const ctx = this.ctx;
            const time = Date.now() / 1000;
            const h = this.canvas.height;
            const busY = h / 2;
            const margin = 100;
            const spacing = (this.canvas.width - margin * 2) / (this.data.branches.length + 1);

            // Top bus electrons (moving right to junctions)
            ctx.fillStyle = '#00ff88';
            this.data.branches.forEach((branch, i) => {
                const x = margin + spacing * (i + 1);
                const speed = branch.current * 5000;

                // Before junction
                for (let j = 0; j < 5; j++) {
                    const px = margin + ((time * speed + j * 20) % (x - margin));
                    ctx.beginPath();
                    ctx.arc(px, busY - 70, 3, 0, Math.PI * 2);
                    ctx.fill();
                }

                // After junction (current division - fewer electrons per branch)
                const branchElectrons = 3;
                const offset = ((time * speed) % (h - 140)) / (h - 140);
                for (let j = 0; j < branchElectrons; j++) {
                    const py = busY - 40 - 60 * ((j + offset) / branchElectrons);
                    ctx.beginPath();
                    ctx.arc(x + 15, py, 3, 0, Math.PI * 2);
                    ctx.fill();
                }
            });
        }

        getBandColors(value) {
            const firstDigit = String(value).charAt(0);
            const secondDigit = String(value).charAt(1) || 0;

            const colors = {
                '0': '#000', '1': '#8B4513', '2': '#FF0000', '3': '#FFA500',
                '4': '#FFFF00', '5': '#00FF00', '6': '#0000FF', '7': '#8B008B',
                '8': '#808080', '9': '#FFFFFF'
            };

            return [colors[firstDigit] || '#000', colors[secondDigit] || '#000', '#DAA520'];
        }

        getHelpContent() {
            return `
                <h4>Parallel Circuit Simulator</h4>
                <p>In parallel circuits, components share the same voltage.</p>
                <ul>
                    <li><strong>Voltage</strong>: Same across all branches (V = V₁ = V₂ = ...)</li>
                    <li><strong>Current Division</strong>: I_total = I₁ + I₂ + ...</li>
                    <li><strong>Equivalent Resistance</strong>: 1/Req = 1/R₁ + 1/R₂ + ...</li>
                    <li><strong>KCL</strong>: Sum of currents entering = Sum leaving</li>
                </ul>
                <p><strong>Tip:</strong> Adding more parallel branches decreases total resistance and increases total current.</p>
            `;
        }
    }

    // ============================================
    // PHASOR DIAGRAM (AC) SIMULATION
    // ============================================
    class PhasorDiagramSimulation extends BaseSimulation {
        constructor() {
            super({
                canvasId: 'phasor-canvas',
                containerId: 'phasor-container',
                width: 800,
                height: 500
            });
            this.name = 'phasorDiagram';
            this.angle = 0;
            this.frequency = 60;
            this.amplitude = 150;
            this.phasors = [];
            this.phaseShift = 0;
        }

        getInitialData() {
            return {
                frequency: 60,
                amplitude: 150,
                phaseShift: 0,
                showComponents: true,
                phasors: [
                    { label: 'V', amplitude: 150, phase: 0, color: '#4a9eff' },
                    { label: 'I', amplitude: 100, phase: -45, color: '#00ff88' }
                ]
            };
        }

        createControls() {
            const controls = document.createElement('div');
            controls.className = 'phasor-controls';
            controls.innerHTML = `
                <div class="phasor-tools">
                    <button class="tool-btn" id="add-phasor">+ Add Phasor</button>
                    <button class="tool-btn" id="remove-phasor">- Remove Phasor</button>
                    <button class="tool-btn" id="toggle-components">Toggle Components</button>
                    <button class="tool-btn" id="pause-animation">⏸ Pause</button>
                </div>
                ${this.createSlider('phasor-frequency', 'Frequency (Hz)', 1, 120, 60, 1, 'Hz').outerHTML}
                ${this.createSlider('phasor-phase', 'Phase Shift', -180, 180, 0, 1, '°').outerHTML}
                ${this.createSlider('phasor-amplitude', 'Amplitude', 50, 200, 150, 10, '').outerHTML}
                <div class="phasor-values">
                    <div class="value-item">
                        <span class="label">Real (Re):</span>
                        <span class="value" id="phasor-real">150.00</span>
                    </div>
                    <div class="value-item">
                        <span class="label">Imag (Im):</span>
                        <span class="value" id="phasor-imag">0.00</span>
                    </div>
                    <div class="value-item">
                        <span class="label">Magnitude:</span>
                        <span class="value" id="phasor-magnitude">150.00</span>
                    </div>
                    <div class="value-item">
                        <span class="label">Phase:</span>
                        <span class="value" id="phasor-angle">0.00°</span>
                    </div>
                </div>
            `;
            this.container.appendChild(controls);
            this.isPaused = false;
        }

        bindEvents() {
            document.getElementById('phasor-frequency').addEventListener('input', (e) => {
                this.data.frequency = parseFloat(e.target.value);
                document.getElementById('phasor-frequency-value').textContent = this.data.frequency + 'Hz';
            });

            document.getElementById('phasor-phase').addEventListener('input', (e) => {
                this.data.phaseShift = parseFloat(e.target.value);
                document.getElementById('phasor-phase-value').textContent = this.data.phaseShift + '°';
                this.data.phasors[0].phase = this.data.phaseShift;
            });

            document.getElementById('phasor-amplitude').addEventListener('input', (e) => {
                this.data.amplitude = parseFloat(e.target.value);
                document.getElementById('phasor-amplitude-value').textContent = this.data.amplitude;
                this.data.phasors[0].amplitude = this.data.amplitude;
            });

            document.getElementById('toggle-components').addEventListener('click', () => {
                this.data.showComponents = !this.data.showComponents;
            });

            document.getElementById('pause-animation').addEventListener('click', (e) => {
                this.isPaused = !this.isPaused;
                e.target.textContent = this.isPaused ? '▶ Resume' : '⏸ Pause';
            });

            document.getElementById('add-phasor').addEventListener('click', () => {
                if (this.data.phasors.length < 4) {
                    const colors = ['#ff6b6b', '#ffcc00', '#da70d6'];
                    this.data.phasors.push({
                        label: String.fromCharCode(65 + this.data.phasors.length),
                        amplitude: 100,
                        phase: -this.data.phasors.length * 30,
                        color: colors[this.data.phasors.length - 1]
                    });
                }
            });

            document.getElementById('remove-phasor').addEventListener('click', () => {
                if (this.data.phasors.length > 1) {
                    this.data.phasors.pop();
                }
            });
        }

        start() {
            this.isRunning = true;
            this.animate();
        }

        animate() {
            if (!this.isRunning) return;
            if (!this.isPaused) {
                this.angle += (this.data.frequency * 0.02);
            }
            this.update();
            this.draw();
            this.animationFrame = requestAnimationFrame(() => this.animate());
        }

        update() {
            const rad = (this.angle * Math.PI) / 180;
            const primaryPhasor = this.data.phasors[0];
            const phaseRad = (primaryPhasor.phase * Math.PI) / 180;

            // Calculate real and imaginary components
            this.realComponent = primaryPhasor.amplitude * Math.cos(rad + phaseRad);
            this.imagComponent = primaryPhasor.amplitude * Math.sin(rad + phaseRad);
            this.magnitude = Math.sqrt(this.realComponent ** 2 + this.imagComponent ** 2);
            this.phaseAngle = Math.atan2(this.imagComponent, this.realComponent) * (180 / Math.PI);

            // Update display
            document.getElementById('phasor-real').textContent = this.realComponent.toFixed(2);
            document.getElementById('phasor-imag').textContent = this.imagComponent.toFixed(2);
            document.getElementById('phasor-magnitude').textContent = this.magnitude.toFixed(2);
            document.getElementById('phasor-angle').textContent = this.phaseAngle.toFixed(2) + '°';
        }

        draw() {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;
            const centerX = w / 2;
            const centerY = h / 2;

            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, w, h);

            // Draw axes
            ctx.strokeStyle = '#444';
            ctx.lineWidth = 1;

            // X-axis
            ctx.beginPath();
            ctx.moveTo(50, centerY);
            ctx.lineTo(w - 50, centerY);
            ctx.stroke();

            // Y-axis
            ctx.beginPath();
            ctx.moveTo(centerX, 50);
            ctx.lineTo(centerX, h - 50);
            ctx.stroke();

            // Labels
            ctx.fillStyle = '#888';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Real (Re)', w - 30, centerY - 10);
            ctx.textAlign = 'right';
            ctx.fillText('Imag (Im)', centerX - 10, 60);

            // Draw unit circle
            ctx.strokeStyle = '#333';
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.arc(centerX, centerY, this.data.amplitude, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw phasors
            const timeAngle = (this.angle * Math.PI) / 180;

            this.data.phasors.forEach(phasor => {
                const phasorAngle = timeAngle + (phasor.phase * Math.PI) / 180;
                const endX = centerX + phasor.amplitude * Math.cos(phasorAngle);
                const endY = centerY - phasor.amplitude * Math.sin(phasorAngle);

                // Draw phasor line
                ctx.strokeStyle = phasor.color;
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(endX, endY);
                ctx.stroke();

                // Draw arrow head
                this.drawArrowHead(ctx, centerX, centerY, endX, endY, phasor.color);

                // Draw phasor label
                ctx.fillStyle = phasor.color;
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(phasor.label, endX + 20, endY);

                // Draw component projections if enabled
                if (this.data.showComponents && phasor === this.data.phasors[0]) {
                    // Real component (horizontal)
                    ctx.strokeStyle = 'rgba(74, 158, 255, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([3, 3]);
                    ctx.beginPath();
                    ctx.moveTo(centerX, centerY);
                    ctx.lineTo(endX, centerY);
                    ctx.stroke();

                    // Imaginary component (vertical)
                    ctx.beginPath();
                    ctx.moveTo(centerX, centerY);
                    ctx.lineTo(centerX, endY);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    // Draw sine wave projection
                    this.drawSineProjection(ctx, centerX, centerY, phasor, timeAngle);
                }
            });

            // Draw time indicator
            ctx.fillStyle = '#ffcc00';
            ctx.font = '12px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(`ωt: ${this.angle.toFixed(1)}°`, 60, 30);
            ctx.fillText(`f: ${this.data.frequency} Hz`, 60, 50);
        }

        drawArrowHead(ctx, fromX, fromY, toX, toY, color) {
            const angle = Math.atan2(toY - fromY, toX - fromX);
            const headLength = 12;

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(toX, toY);
            ctx.lineTo(toX - headLength * Math.cos(angle - Math.PI / 6), toY - headLength * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(toX - headLength * Math.cos(angle + Math.PI / 6), toY - headLength * Math.sin(angle + Math.PI / 6));
            ctx.closePath();
            ctx.fill();
        }

        drawSineProjection(ctx, centerX, centerY, phasor, timeAngle) {
            const phaseRad = (phasor.phase * Math.PI) / 180;
            const amplitude = phasor.amplitude;
            const waveStartX = centerX + amplitude + 30;
            const waveWidth = 100;

            ctx.strokeStyle = 'rgba(74, 158, 255, 0.7)';
            ctx.lineWidth = 2;
            ctx.beginPath();

            for (let x = 0; x < waveWidth; x++) {
                const waveAngle = timeAngle + phaseRad - (x / waveWidth) * (Math.PI * 2);
                const y = centerY - amplitude * Math.sin(waveAngle);
                if (x === 0) {
                    ctx.moveTo(waveStartX + x, y);
                } else {
                    ctx.lineTo(waveStartX + x, y);
                }
            }
            ctx.stroke();

            // Draw connection line to wave
            const currentY = centerY - amplitude * Math.sin(timeAngle + phaseRad);
            ctx.strokeStyle = 'rgba(74, 158, 255, 0.3)';
            ctx.setLineDash([2, 4]);
            ctx.beginPath();
            ctx.moveTo(centerX + amplitude * Math.cos(timeAngle + phaseRad), currentY);
            ctx.lineTo(waveStartX, currentY);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        getHelpContent() {
            return `
                <h4>Phasor Diagram (AC)</h4>
                <p>Phasors represent sinusoidal quantities as rotating vectors.</p>
                <ul>
                    <li><strong>Magnitude</strong>: Peak amplitude of the sinusoid</li>
                    <li><strong>Phase</strong>: Angular displacement from reference</li>
                    <li><strong>Angular Velocity (ω)</strong>: 2πf, where f is frequency</li>
                    <li><strong>Real Component</strong>: x = A·cos(ωt + φ)</li>
                    <li><strong>Imaginary Component</strong>: y = A·sin(ωt + φ)</li>
                </ul>
                <p><strong>Controls:</strong> Adjust frequency to change rotation speed. Use phase shift to see phase relationships.</p>
            `;
        }
    }

    // ============================================
    // LOGIC GATE SIMULATION
    // ============================================
    class LogicGateSimulation extends BaseSimulation {
        constructor() {
            super({
                canvasId: 'logic-canvas',
                containerId: 'logic-container',
                width: 800,
                height: 500
            });
            this.name = 'logicGates';
            this.gates = [];
            this.connections = [];
            this.selectedGate = null;
            this.gateTypes = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR'];
            this.gateCounter = 0;
            this.inputStates = [false, false, false];
        }

        getInitialData() {
            return {
                gates: [
                    { id: 1, type: 'AND', x: 350, y: 150, inputs: [false, false] },
                    { id: 2, type: 'NOT', x: 550, y: 150, inputs: [false] }
                ],
                connections: [
                    { from: { gate: 1, output: 0 }, to: { gate: 2, input: 0 } }
                ]
            };
        }

        createControls() {
            const controls = document.createElement('div');
            controls.className = 'logic-controls';
            controls.innerHTML = `
                <div class="gate-palette">
                    <h4>Gate Palette</h4>
                    <div class="gate-buttons">
                        ${this.gateTypes.map(type => `
                            <button class="gate-btn" data-type="${type}" draggable="true">
                                <svg width="40" height="30" viewBox="0 0 40 30">${this.getGateSVG(type)}</svg>
                                <span>${type}</span>
                            </button>
                        `).join('')}
                    </div>
                </div>
                <div class="logic-tools">
                    <button class="tool-btn" id="add-input">+ Input</button>
                    <button class="tool-btn" id="add-output">+ Output</button>
                    <button class="tool-btn" id="clear-circuit">Clear All</button>
                    <button class="tool-btn" id="generate-truth">Truth Table</button>
                </div>
                <div class="truth-table-container" id="truth-table"></div>
                <div class="gate-properties" id="gate-properties"></div>
            `;
            this.container.appendChild(controls);
            this.initGatePalette();
        }

        getGateSVG(type) {
            const shapes = {
                'AND': '<path d="M5,5 Q20,5 30,15 Q20,25 5,25 Z" fill="none" stroke="currentColor" stroke-width="2"/>',
                'OR': '<path d="M5,5 Q25,5 35,15 Q25,25 5,25 Q15,15 5,5" fill="none" stroke="currentColor" stroke-width="2"/>',
                'NOT': '<path d="M5,5 L30,15 L5,25 Z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="36" cy="15" r="2" fill="currentColor"/>',
                'NAND': '<path d="M5,5 Q20,5 30,15 Q20,25 5,25 Z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="36" cy="15" r="3" fill="none" stroke="currentColor" stroke-width="2"/>',
                'NOR': '<path d="M5,5 Q25,5 35,15 Q25,25 5,25 Q15,15 5,5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="38" cy="15" r="3" fill="none" stroke="currentColor" stroke-width="2"/>',
                'XOR': '<path d="M5,5 Q25,5 35,15 Q25,25 5,25 Q15,15 5,5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8,5 Q28,5 38,15 Q28,25 8,25" fill="none" stroke="currentColor" stroke-width="1"/>'
            };
            return shapes[type] || '';
        }

        initGatePalette() {
            const buttons = document.querySelectorAll('.gate-btn');
            buttons.forEach(btn => {
                btn.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('gateType', btn.dataset.type);
                });
            });

            this.canvas.addEventListener('dragover', (e) => e.preventDefault());
            this.canvas.addEventListener('drop', (e) => {
                e.preventDefault();
                const type = e.dataTransfer.getData('gateType');
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                this.addGate(type, x, y);
            });
        }

        addGate(type, x, y) {
            this.gateCounter++;
            const inputCount = type === 'NOT' || type === 'BUFFER' ? 1 : 2;

            const gate = {
                id: this.gateCounter,
                type: type,
                x: x,
                y: y,
                inputs: new Array(inputCount).fill(false),
                output: false
            };

            this.data.gates.push(gate);
            this.updateTruthTable();
            this.evaluateCircuit();
            this.draw();
        }

        bindEvents() {
            this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
            this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
            this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));

            document.getElementById('clear-circuit').addEventListener('click', () => {
                this.data.gates = [];
                this.data.connections = [];
                this.gateCounter = 0;
                this.updateTruthTable();
                this.draw();
            });

            document.getElementById('generate-truth').addEventListener('click', () => {
                this.updateTruthTable();
                document.getElementById('truth-table').classList.toggle('visible');
            });

            document.getElementById('add-input').addEventListener('click', () => {
                this.addGate('INPUT', 100, 100 + this.data.gates.filter(g => g.type === 'INPUT').length * 60);
            });

            document.getElementById('add-output').addEventListener('click', () => {
                this.addGate('OUTPUT', 650, 150 + this.data.gates.filter(g => g.type === 'OUTPUT').length * 60);
            });
        }

        handleMouseDown(e) {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Check if clicking on a gate
            for (const gate of this.data.gates) {
                if (x >= gate.x - 40 && x <= gate.x + 40 &&
                    y >= gate.y - 20 && y <= gate.y + 20) {
                    this.selectedGate = gate;
                    this.draggedGate = gate;
                    this.showGateProperties(gate);
                    break;
                }
            }
        }

        handleMouseMove(e) {
            if (!this.draggedGate) return;
            const rect = this.canvas.getBoundingClientRect();
            this.draggedGate.x = e.clientX - rect.left;
            this.draggedGate.y = e.clientY - rect.top;
            this.draw();
        }

        handleMouseUp() {
            this.draggedGate = null;
        }

        showGateProperties(gate) {
            const props = document.getElementById('gate-properties');
            if (!props) return;

            if (gate.type === 'INPUT') {
                props.innerHTML = `
                    <h4>Input Properties</h4>
                    <label>
                        <input type="checkbox" ${gate.output ? 'checked' : ''} id="input-toggle">
                        High (1)
                    </label>
                `;
                document.getElementById('input-toggle').addEventListener('change', (e) => {
                    gate.output = e.target.checked;
                    this.evaluateCircuit();
                    this.draw();
                });
            } else {
                props.innerHTML = `
                    <h4>${gate.type} Gate</h4>
                    <p>Inputs: ${gate.inputs.map(i => i ? '1' : '0').join(', ')}</p>
                    <p>Output: ${gate.output ? '1' : '0'}</p>
                `;
            }
        }

        evaluateCircuit() {
            // Reset all gate inputs
            this.data.gates.forEach(gate => {
                if (gate.type !== 'INPUT') {
                    gate.inputs = new Array(gate.inputs.length).fill(false);
                }
            });

            // Evaluate gates in order
            this.data.gates.forEach(gate => {
                if (gate.type === 'INPUT') {
                    // Input gates already have their output set
                } else if (gate.type === 'NOT') {
                    const inputGate = this.findInputForGate(gate, 0);
                    gate.output = inputGate ? !inputGate.output : false;
                } else if (gate.type === 'AND') {
                    const in1 = this.findInputForGate(gate, 0);
                    const in2 = this.findInputForGate(gate, 1);
                    gate.output = (in1 ? in1.output : false) && (in2 ? in2.output : false);
                } else if (gate.type === 'OR') {
                    const in1 = this.findInputForGate(gate, 0);
                    const in2 = this.findInputForGate(gate, 1);
                    gate.output = (in1 ? in1.output : false) || (in2 ? in2.output : false);
                } else if (gate.type === 'NAND') {
                    const in1 = this.findInputForGate(gate, 0);
                    const in2 = this.findInputForGate(gate, 1);
                    gate.output = !((in1 ? in1.output : false) && (in2 ? in2.output : false));
                } else if (gate.type === 'NOR') {
                    const in1 = this.findInputForGate(gate, 0);
                    const in2 = this.findInputForGate(gate, 1);
                    gate.output = !((in1 ? in1.output : false) || (in2 ? in2.output : false));
                } else if (gate.type === 'XOR') {
                    const in1 = this.findInputForGate(gate, 0);
                    const in2 = this.findInputForGate(gate, 1);
                    const v1 = in1 ? in1.output : false;
                    const v2 = in2 ? in2.output : false;
                    gate.output = (v1 && !v2) || (!v1 && v2);
                } else if (gate.type === 'OUTPUT') {
                    const inputGate = this.findInputForGate(gate, 0);
                    gate.output = inputGate ? inputGate.output : false;
                }
            });
        }

        findInputForGate(targetGate, inputIndex) {
            // Find the gate whose output is connected to targetGate's inputIndex
            // For simplicity, find the closest gate above
            const inputGates = this.data.gates.filter(g => g.type !== 'OUTPUT' && g.id !== targetGate.id);
            const sorted = inputGates.sort((a, b) => {
                const distA = Math.sqrt((a.x - targetGate.x) ** 2 + (a.y - targetGate.y) ** 2);
                const distB = Math.sqrt((b.x - targetGate.x) ** 2 + (b.y - targetGate.y) ** 2);
                return distA - distB;
            });
            return sorted[inputIndex] || null;
        }

        updateTruthTable() {
            const table = document.getElementById('truth-table');
            const inputGates = this.data.gates.filter(g => g.type === 'INPUT');
            const outputGates = this.data.gates.filter(g => g.type === 'OUTPUT');

            if (inputGates.length === 0 || outputGates.length === 0) {
                table.innerHTML = '<p>Add INPUT and OUTPUT gates to see truth table.</p>';
                return;
            }

            let html = '<table class="truth-table"><thead><tr>';
            inputGates.forEach(g => html += `<th>${g.type} ${g.id}</th>`);
            outputGates.forEach(g => html += `<th>${g.type} ${g.id}</th>`);
            html += '</tr></thead><tbody>';

            const totalRows = Math.pow(2, inputGates.length);
            for (let i = 0; i < totalRows; i++) {
                // Set input states
                inputGates.forEach((gate, idx) => {
                    gate.output = ((i >> (inputGates.length - 1 - idx)) & 1) === 1;
                });

                this.evaluateCircuit();

                html += '<tr>';
                inputGates.forEach(g => html += `<td class="${g.output ? 'high' : 'low'}">${g.output ? '1' : '0'}</td>`);
                outputGates.forEach(g => html += `<td class="${g.output ? 'high' : 'low'}">${g.output ? '1' : '0'}</td>`);
                html += '</tr>';
            }

            html += '</tbody></table>';
            table.innerHTML = html;
        }

        draw() {
            const ctx = this.ctx;
            const w = this.canvas.width;
            const h = this.canvas.height;

            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, w, h);

            // Draw grid
            ctx.strokeStyle = '#2a2a3e';
            ctx.lineWidth = 1;
            for (let x = 0; x < w; x += 50) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();
            }
            for (let y = 0; y < h; y += 50) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }

            // Draw connections
            this.drawConnections();

            // Draw gates
            this.data.gates.forEach(gate => this.drawGate(gate));

            // Draw signal flow animation
            this.drawSignalFlow();
        }

        drawConnections() {
            const ctx = this.ctx;
            ctx.strokeStyle = '#4a9eff';
            ctx.lineWidth = 2;

            // Draw simple connections based on proximity
            this.data.gates.forEach(gate => {
                if (gate.type !== 'INPUT' && gate.type !== 'OUTPUT') {
                    const inputGates = this.data.gates.filter(g =>
                        g.type !== 'OUTPUT' && g.id !== gate.id
                    ).sort((a, b) => {
                        const distA = Math.sqrt((a.x - gate.x) ** 2 + (a.y - gate.y) ** 2);
                        const distB = Math.sqrt((b.x - gate.x) ** 2 + (b.y - gate.y) ** 2);
                        return distA - distB;
                    });

                    inputGates.slice(0, gate.inputs.length).forEach((inputGate, idx) => {
                        const startX = inputGate.x + 25;
                        const startY = inputGate.y;
                        const endX = gate.x - 25;
                        const endY = gate.y - (gate.inputs.length - 1) * 15 + idx * 30;

                        ctx.strokeStyle = inputGate.output ? '#00ff88' : '#666';
                        ctx.beginPath();
                        ctx.moveTo(startX, startY);

                        // Horizontal then vertical
                        ctx.lineTo((startX + endX) / 2, startY);
                        ctx.lineTo((startX + endX) / 2, endY);
                        ctx.lineTo(endX, endY);
                        ctx.stroke();

                        // Draw dot at input
                        ctx.fillStyle = inputGate.output ? '#00ff88' : '#666';
                        ctx.beginPath();
                        ctx.arc(endX, endY, 4, 0, Math.PI * 2);
                        ctx.fill();
                    });
                }
            });
        }

        drawGate(gate) {
            const ctx = this.ctx;
            const x = gate.x;
            const y = gate.y;
            const w = 50;
            const h = 40;

            // Highlight selected
            if (gate === this.selectedGate) {
                ctx.strokeStyle = '#ffcc00';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.rect(x - w / 2 - 5, y - h / 2 - 5, w + 10, h + 10);
                ctx.stroke();
            }

            // Draw based on type
            ctx.strokeStyle = gate.output ? '#00ff88' : '#ff6b6b';
            ctx.lineWidth = 3;
            ctx.fillStyle = '#1a1a2e';

            if (gate.type === 'INPUT') {
                // Input node
                ctx.fillStyle = gate.output ? '#00ff88' : '#ff6b6b';
                ctx.beginPath();
                ctx.arc(x, y, 15, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(gate.output ? '1' : '0', x, y + 5);
                ctx.fillStyle = '#888';
                ctx.font = '10px Arial';
                ctx.fillText(`In${gate.id}`, x, y + 30);
            } else if (gate.type === 'OUTPUT') {
                // Output node
                ctx.fillStyle = gate.output ? '#00ff88' : '#ff6b6b';
                ctx.beginPath();
                ctx.arc(x, y, 15, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(gate.output ? '1' : '0', x, y + 5);
                ctx.fillStyle = '#888';
                ctx.font = '10px Arial';
                ctx.fillText(`Out${gate.id}`, x, y + 30);
            } else {
                // Logic gate shapes
                ctx.beginPath();
                if (gate.type === 'AND') {
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.quadraticCurveTo(x, y - h / 2, x + w / 2, y);
                    ctx.quadraticCurveTo(x, y + h / 2, x - w / 2, y + h / 2);
                    ctx.closePath();
                } else if (gate.type === 'OR') {
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.quadraticCurveTo(x - w / 4, y, x - w / 2, y + h / 2);
                    ctx.quadraticCurveTo(x, y - h / 2 + 10, x + w / 2, y);
                    ctx.quadraticCurveTo(x, y + h / 2 - 10, x - w / 2, y + h / 2);
                } else if (gate.type === 'NOT') {
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.lineTo(x + w / 2, y);
                    ctx.lineTo(x - w / 2, y + h / 2);
                    ctx.closePath();
                    // Inversion bubble
                    ctx.moveTo(x + w / 2 + 8, y);
                    ctx.arc(x + w / 2 + 5, y, 5, 0, Math.PI * 2);
                } else if (gate.type === 'NAND') {
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.quadraticCurveTo(x, y - h / 2, x + w / 2 - 5, y);
                    ctx.quadraticCurveTo(x, y + h / 2, x - w / 2, y + h / 2);
                    ctx.closePath();
                    ctx.moveTo(x + w / 2, y);
                    ctx.arc(x + w / 2 + 5, y, 5, 0, Math.PI * 2);
                } else if (gate.type === 'NOR') {
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.quadraticCurveTo(x - w / 4, y, x - w / 2, y + h / 2);
                    ctx.quadraticCurveTo(x, y - h / 2 + 10, x + w / 2 - 5, y);
                    ctx.quadraticCurveTo(x, y + h / 2 - 10, x - w / 2, y + h / 2);
                    ctx.moveTo(x + w / 2, y);
                    ctx.arc(x + w / 2 + 5, y, 5, 0, Math.PI * 2);
                } else if (gate.type === 'XOR') {
                    ctx.moveTo(x - w / 2 + 5, y - h / 2);
                    ctx.quadraticCurveTo(x - w / 4, y, x - w / 2 + 5, y + h / 2);
                    ctx.quadraticCurveTo(x, y - h / 2 + 10, x + w / 2, y);
                    ctx.quadraticCurveTo(x, y + h / 2 - 10, x - w / 2 + 5, y + h / 2);
                    // Second curve for XOR
                    ctx.moveTo(x - w / 2, y - h / 2);
                    ctx.quadraticCurveTo(x - w / 4, y, x - w / 2, y + h / 2);
                }
                ctx.fill();
                ctx.stroke();

                // Output indicator
                ctx.fillStyle = gate.output ? '#00ff88' : '#ff6b6b';
                ctx.beginPath();
                ctx.arc(x + w / 2 + 20, y, 5, 0, Math.PI * 2);
                ctx.fill();

                // Label
                ctx.fillStyle = '#888';
                ctx.font = '10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(gate.type, x, y + h / 2 + 15);
            }
        }

        drawSignalFlow() {
            const ctx = this.ctx;
            const time = Date.now() / 500;

            ctx.fillStyle = '#00ff88';

            this.data.gates.forEach(gate => {
                if (gate.output) {
                    // Animated particles flowing from outputs
                    for (let i = 0; i < 3; i++) {
                        const offset = (time + i * 10) % 30;
                        ctx.globalAlpha = 1 - offset / 30;
                        ctx.beginPath();
                        ctx.arc(gate.x + 30 + offset, gate.y, 3, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    ctx.globalAlpha = 1;
                }
            });
        }

        getHelpContent() {
            return `
                <h4>Logic Gate Simulator</h4>
                <p>Build and test digital logic circuits.</p>
                <ul>
                    <li><strong>AND</strong>: Output = 1 only if ALL inputs are 1</li>
                    <li><strong>OR</strong>: Output = 1 if ANY input is 1</li>
                    <li><strong>NOT</strong>: Inverts the input (0→1, 1→0)</li>
                    <li><strong>NAND</strong>: NOT of AND (universal gate)</li>
                    <li><strong>NOR</strong>: NOT of OR (universal gate)</li>
                    <li><strong>XOR</strong>: Output = 1 if inputs are DIFFERENT</li>
                </ul>
                <p><strong>Controls:</strong> Drag gates from palette to canvas. Click INPUT gates to toggle. Click "Truth Table" to generate.</p>
            `;
        }
    }

    // ============================================
    // GLOBAL EXPORTS
    // ============================================
    global.SimulationController = SimulationController;
    global.OhmsLawSimulation = OhmsLawSimulation;
    global.SeriesCircuitSimulation = SeriesCircuitSimulation;
    global.ParallelCircuitSimulation = ParallelCircuitSimulation;
    global.PhasorDiagramSimulation = PhasorDiagramSimulation;
    global.LogicGateSimulation = LogicGateSimulation;

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => SimulationController.init());
    } else {
        SimulationController.init();
    }

})(typeof window !== 'undefined' ? window : this);
