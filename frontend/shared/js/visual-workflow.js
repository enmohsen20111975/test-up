const DATA_SOURCES = ['../shared/data', 'shared/data', '/shared/data'];

async function fetchLibraryFile(fileName) {
    for (const base of DATA_SOURCES) {
        try {
            const response = await fetch(`${base}/${fileName}`, { cache: 'no-store' });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            continue;
        }
    }
    throw new Error(`Unable to load ${fileName}`);
}

const VisualWorkflow = {
    canvas: null,
    ctx: null,
    nodes: [],
    connections: [],
    scale: 1,
    offset: { x: 0, y: 0 },
    selectedNode: null,
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    isConnecting: false,
    connectionStart: null,
    tempWireEnd: null,
    undoStack: [],
    redoStack: [],
    maxHistorySize: 50,
    collapsedCategories: {},
    workflowLibrary: [],
    examplesLibrary: [],
    librarySearchTerm: '',
    examplesMenuInitialized: false,

    init: function() {
        this.canvas = document.getElementById('visual-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.dpr = window.devicePixelRatio || 1;
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.setupEventListeners();
        this.render();
        console.log('Visual Calculator Workflow Builder Initialized');
        this.populateComponents();
        this.loadLibraries();
    },

    show: function() {
        try {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('console-view').classList.add('hidden');
            document.getElementById('visual-builder-view').classList.remove('hidden');
            
            if (!this.canvas) {
                this.init();
            }
            
            this.populateComponents();
            this.render();
            console.log('Visual Workflow Builder shown');
            this.showNotification('🎨 Visual Workflow Builder loaded - Drag calculators to canvas', 'success', 3000);
        } catch (error) {
            console.error('Error showing visual workflow:', error);
            this.showNotification('Error loading workflow builder: ' + error.message, 'error', 3000);
        }
    },

    resize: function() {
        const container = this.canvas.parentElement;
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.canvas.width = width * this.dpr;
        this.canvas.height = height * this.dpr;
        this.canvas.style.width = width + 'px';
        this.canvas.style.height = height + 'px';
        
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.scale(this.dpr, this.dpr);
        this.render();
    },

    setupEventListeners: function() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e), false);
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e), false);
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e), false);
        this.canvas.style.touchAction = 'none';

        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undo();
            } else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
                e.preventDefault();
                this.redo();
            } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveWorkflow();
            } else if (e.key === 'Escape') {
                const menu = document.getElementById('examples-menu');
                if (menu) menu.style.display = 'none';
            }
        });

        document.addEventListener('click', (e) => {
            const menu = document.getElementById('examples-menu');
            if (!menu) return;
            
            const target = e.target;
            const isMenuButton = target.closest('button')?.textContent.includes('Examples');
            const isInsideMenu = menu.contains(target);
            
            if (!isMenuButton && !isInsideMenu && menu.style.display === 'block') {
                menu.style.display = 'none';
            }
        });

        this.canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });

        this.canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            const data = e.dataTransfer.getData('calculatorNode');
            if (!data) return;
            
            const { moduleKey, calcKey } = JSON.parse(data);
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.offset.x) / this.scale;
            const y = (e.clientY - rect.top - this.offset.y) / this.scale;
            
            this.addCalculatorNode(moduleKey, calcKey, x, y);
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' && this.selectedNode) {
                this.deleteNode(this.selectedNode);
            }
            if (e.key === 'Escape') {
                this.isConnecting = false;
                this.connectionStart = null;
                this.canvas.style.cursor = 'default';
                this.render();
            }
        });
    },

    calculatorFields: {
        loadCalculation: {
            fields: [
                { name: 'power', label: 'Power(kW)', type: 'number', required: true },
                { name: 'voltage', label: 'Voltage(V)', type: 'number', required: true },
                { name: 'powerFactor', label: 'Power Factor', type: 'number', required: false },
                { name: 'systemType', label: 'System Type', type: 'select', options: [
                    { value: '3phase', label: '3-Phase' },
                    { value: '1phase', label: '1-Phase' }
                ]}
            ],
            outputs: [
                { name: 'current', label: 'Current(A)', type: 'number' },
                { name: 'apparentPower', label: 'Apparent Power(kVA)', type: 'number' }
            ]
        },
        cableSizing: {
            fields: [
                { name: 'current', label: 'Current(A)', type: 'number', required: true },
                { name: 'length', label: 'Cable Length(m)', type: 'number', required: true },
                { name: 'voltageSystem', label: 'System Voltage(V)', type: 'number', required: true },
                { name: 'standard', label: 'Standard', type: 'select', options: [
                    { value: 'IEC', label: 'IEC' },
                    { value: 'NEC', label: 'NEC' }
                ]}
            ],
            outputs: [
                { name: 'cableSize', label: 'Cable Size(mm²)', type: 'string' },
                { name: 'voltageDrop', label: 'Voltage Drop(%)', type: 'number' }
            ]
        },
        transformerSizing: {
            fields: [
                { name: 'totalLoad', label: 'Total Load(kVA)', type: 'number', required: true },
                { name: 'growthFactor', label: 'Growth Factor', type: 'number', required: false },
                { name: 'efficiency', label: 'Efficiency (%)', type: 'number', required: false },
                { name: 'standard', label: 'Standard', type: 'select', options: [
                    { value: 'IEC', label: 'IEC' },
                    { value: 'IEEE', label: 'IEEE' }
                ]},
                { name: 'coolingType', label: 'Cooling Type', type: 'select', options: [
                    { value: 'ONAN', label: 'ONAN' },
                    { value: 'ONAF', label: 'ONAF' },
                    { value: 'OFAF', label: 'OFAF' },
                    { value: 'OFWF', label: 'OFWF' }
                ]}
            ],
            outputs: [
                { name: 'requiredKVA', label: 'Required kVA', type: 'number' },
                { name: 'standardSize', label: 'Standard Size (kVA)', type: 'number' },
                { name: 'loadingStatus', label: 'Loading Status', type: 'string' }
            ]
        },
        pipeSizing: {
            fields: [
                { name: 'flowRate', label: 'Flow Rate(L/s)', type: 'number', required: true },
                { name: 'velocity', label: 'Velocity(m/s)', type: 'number', required: true }
            ],
            outputs: [
                { name: 'diameter', label: 'Pipe Diameter(mm)', type: 'number' }
            ]
        },
        pumpSizing: {
            fields: [
                { name: 'flowRate', label: 'Flow Rate(m³/h)', type: 'number', required: true },
                { name: 'head', label: 'Total Head(m)', type: 'number', required: true },
                { name: 'efficiency', label: 'Pump Efficiency(%)', type: 'number', required: false }
            ],
            outputs: [
                { name: 'power', label: 'Pump Power(kW)', type: 'number' }
            ]
        },
        concreteVolume: {
            fields: [
                { name: 'length', label: 'Length(m)', type: 'number', required: true },
                { name: 'width', label: 'Width(m)', type: 'number', required: true },
                { name: 'height', label: 'Height(m)', type: 'number', required: true },
                { name: 'wastage', label: 'Wastage(%)', type: 'number', required: false }
            ],
            outputs: [
                { name: 'volume', label: 'Volume(m³)', type: 'number' }
            ]
        },
        steelWeight: {
            fields: [
                { name: 'diameter', label: 'Bar Diameter(mm)', type: 'number', required: true },
                { name: 'length', label: 'Total Length(m)', type: 'number', required: true }
            ],
            outputs: [
                { name: 'weight', label: 'Weight(kg)', type: 'number' }
            ]
        }
    },

    addCalculatorNode: function(moduleKey, calcKey, x, y) {
        const module = Calculators.modules[moduleKey];
        if (!module) {
            console.error('Module not found:', moduleKey);
            return;
        }

        let calculator = null;
        let calcName = '';
        for (const [name, calc] of Object.entries(module.calculators)) {
            if (calc && calc.key === calcKey) {
                calculator = calc;
                calcName = name;
                break;
            }
        }

        if (!calculator) {
            console.error('Calculator not found:', calcKey);
            return;
        }

        const calcDef = this.calculatorFields[calcKey] || {
            fields: [{ name: 'value', label: 'Value', type: 'number', required: true }],
            outputs: [{ name: 'result', label: 'Result', type: 'number' }]
        };

        const newNode = new CalculatorNode(
            Date.now(), 
            calcName, 
            moduleKey, 
            calcKey, 
            x, y, 
            calcDef.fields, 
            calcDef.outputs
        );
        
        this.nodes.push(newNode);
        this.selectedNode = newNode;
        this.updateProperties(newNode);
        this.saveState();
        this.render();
        this.showNotification(`✓ Added ${calcName} node`, 'success', 2000);
    },

    deleteNode: function(node) {
        this.connections = this.connections.filter(c => c.fromNode !== node && c.toNode !== node);
        this.nodes = this.nodes.filter(n => n !== node);
        this.selectedNode = null;
        this.updateProperties(null);
        this.saveState();
        this.render();
    },

    populateComponents: function() {
        console.log('populateComponents() called');
        const container = document.getElementById('builder-components');
        console.log('Container found:', !!container);
        if (!container) return;
        
        // Check if i18n system is available
        if (typeof i18n === 'undefined' || !i18n.getTranslation) {
            console.log('i18n not available, retrying in 100ms');
            setTimeout(() => this.populateComponents(), 100);
            return;
        }

        let html = '<div class="component-categories" style="max-height: calc(100vh - 200px); overflow-y: auto;">';
        
        Object.entries(Calculators.modules).forEach(([moduleKey, module]) => {
            const calcs = Object.entries(module.calculators);
            if (calcs.length === 0) return;

            const isCollapsed = this.collapsedCategories[moduleKey] || false;
            html += `
                <div class="component-category" style="margin-bottom: 1rem;">
                    <h4 class="category-title" 
                        onclick="VisualWorkflow.toggleCategory('${moduleKey}')"
                        style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer; display: flex; align-items: center; gap: 6px; padding: 8px; border-radius: 6px; transition: all 0.2s;"
                        onmouseover="this.style.background='rgba(59,130,246,0.1)'; this.style.color='#3b82f6';"
                        onmouseout="this.style.background='transparent'; this.style.color='#9ca3af';"}
                    >
                        <span style="transition: transform 0.2s; display: inline-block; ${isCollapsed ? '' : 'transform: rotate(90deg);'};">▶</span>
                        ${module.icon} ${module.name}
                        <span style="font-size: 0.75rem; opacity: 0.6;">(${calcs.length})</span>
                    </h4>
                    <div class="category-items" style="display: ${isCollapsed ? 'none' : 'block'}; padding-left: 8px;">
                         ${calcs.map(([calcName, calc]) => `
                            <div class="draggable-component glass" 
                                draggable="true" 
                                data-module-key="${moduleKey}" 
                                data-calc-key="${calc.key}"
                                ondragstart="VisualWorkflow.onDragStart(event, '${moduleKey}', '${calc.key}')"
                                ontouchstart="VisualWorkflow.onComponentTouchStart(event, '${moduleKey}', '${calc.key}')"
                                ontouchend="VisualWorkflow.onComponentTouchEnd(event)"
                                style="padding: 10px 12px; cursor: grab; border-radius: 6px; margin-bottom: 6px; font-size: 0.85rem; transition: all 0.2s; border: 1px solid rgba(59,130,246,0.3); background: rgba(30,41,59,0.5);"
                                onmouseover="this.style.background='rgba(59,130,246,0.2)'; this.style.borderColor='rgba(59,130,246,0.5)';"
                                onmouseout="this.style.background='rgba(30,41,59,0.5)'; this.style.borderColor='rgba(59,130,246,0.3)';"
                            >
                                <div style="font-weight: 600; color: #f8fafc; margin-bottom: 2px;">${calc.nameKey ? (i18n.getTranslation(calc.nameKey) || calcName) : calcName}</div>
                                <div style="font-size: 0.75rem; color: #94a3b8;">${calc.desc || ''}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
        console.log('Calculators.modules:', Calculators.modules);
        console.log('Visual Workflow: Populated', Object.keys(Calculators.modules).length, 'categories');
    },

    loadLibraries: async function() {
        try {
            const workflowsData = await fetchLibraryFile('workflows.json');
            this.workflowLibrary = Array.isArray(workflowsData.workflows) ? workflowsData.workflows : [];
        } catch (error) {
            console.warn('Workflow library unavailable:', error);
        }

        try {
            const examplesData = await fetchLibraryFile('examples.json');
            this.examplesLibrary = Array.isArray(examplesData.examples) ? examplesData.examples : [];
        } catch (error) {
            console.warn('Examples library unavailable:', error);
        }

        this.populateExamplesMenu();
    },

    populateExamplesMenu: function() {
        const featuredContainer = document.getElementById('examples-featured');
        const workflowsContainer = document.getElementById('workflows-library');
        const examplesContainer = document.getElementById('examples-library');
        const searchInput = document.getElementById('examples-search');

        if (!featuredContainer || !workflowsContainer || !examplesContainer) return;

        if (searchInput && !this.examplesMenuInitialized) {
            searchInput.addEventListener('input', (event) => {
                this.librarySearchTerm = event.target.value.toLowerCase();
                this.populateExamplesMenu();
            });
            this.examplesMenuInitialized = true;
        }

        const term = this.librarySearchTerm;
        const matchesSearch = (text) => !term || (text && text.toLowerCase().includes(term));

        featuredContainer.innerHTML = Object.entries(this.exampleWorkflows).map(([key, example]) => {
            const matches = matchesSearch(example.name) || matchesSearch(example.description);
            if (!matches) return '';
            return `
                <div class="example-item" onclick="VisualWorkflow.loadExample('${key}')">
                    <h5>${example.name}</h5>
                    <p>${example.description}</p>
                </div>
            `;
        }).join('');

        const workflowItems = this.workflowLibrary.filter((workflow) => {
            return matchesSearch(workflow.title) || matchesSearch(workflow.description) || matchesSearch(workflow.domain);
        });

        workflowsContainer.innerHTML = workflowItems.map((workflow) => `
            <div class="example-item" onclick="VisualWorkflow.showWorkflowDetails('${workflow.id}')">
                <h5>${workflow.title}</h5>
                <p>${workflow.domain.toUpperCase()} · ${workflow.description}</p>
            </div>
        `).join('');

        const exampleItems = this.examplesLibrary.filter((example) => {
            return matchesSearch(example.title) || matchesSearch(example.scenario) || matchesSearch(example.domain);
        });

        examplesContainer.innerHTML = exampleItems.map((example) => `
            <div class="example-item" onclick="VisualWorkflow.showExampleDetails('${example.id}')">
                <h5>${example.title}</h5>
                <p>${example.domain.toUpperCase()} · ${example.scenario}</p>
            </div>
        `).join('');
    },

    showWorkflowDetails: function(workflowId) {
        const workflow = this.workflowLibrary.find((item) => item.id === workflowId);
        if (!workflow) return;
        const container = document.getElementById('builder-props-content');
        if (!container) return;

        container.innerHTML = `
            <div class="node-properties">
                <h3>${workflow.title}</h3>
                <p style="color: var(--text-secondary); margin-top: -0.5rem;">${workflow.domain.toUpperCase()} workflow</p>
                <p>${workflow.description}</p>
                <div class="results-section">
                    <h4>Inputs</h4>
                    ${workflow.inputs.map((item) => `<div class="result-item"><span>${item}</span></div>`).join('')}
                </div>
                <div class="results-section">
                    <h4>Outputs</h4>
                    ${workflow.outputs.map((item) => `<div class="result-item"><span>${item}</span></div>`).join('')}
                </div>
                <div class="results-section">
                    <h4>Steps</h4>
                    ${workflow.steps.map((item, index) => `<div class="result-item"><span>${index + 1}. ${item}</span></div>`).join('')}
                </div>
            </div>
        `;
    },

    showExampleDetails: function(exampleId) {
        const example = this.examplesLibrary.find((item) => item.id === exampleId);
        if (!example) return;
        const container = document.getElementById('builder-props-content');
        if (!container) return;

        const formatPairs = (obj) => Object.entries(obj || {}).map(([key, value]) => {
            return `<div class="result-item"><span>${key}</span><span>${value}</span></div>`;
        }).join('');

        container.innerHTML = `
            <div class="node-properties">
                <h3>${example.title}</h3>
                <p style="color: var(--text-secondary); margin-top: -0.5rem;">${example.domain.toUpperCase()} example</p>
                <p>${example.scenario}</p>
                <div class="results-section">
                    <h4>Inputs</h4>
                    ${formatPairs(example.inputs)}
                </div>
                <div class="results-section">
                    <h4>Outputs</h4>
                    ${formatPairs(example.outputs)}
                </div>
            </div>
        `;
    },

    toggleCategory: function(moduleKey) {
        this.collapsedCategories[moduleKey] = !this.collapsedCategories[moduleKey];
        this.populateComponents();
    },

    onDragStart: function(e, moduleKey, calcKey) {
        e.dataTransfer.setData('calculatorNode', JSON.stringify({ moduleKey, calcKey }));
    },

    onComponentTouchStart: function(e, moduleKey, calcKey) {
        this.touchDraggingComponent = {
            moduleKey: moduleKey,
            calcKey: calcKey,
            startX: e.touches[0].clientX,
            startY: e.touches[0].clientY,
            element: e.currentTarget
        };
        
        e.currentTarget.style.opacity = '0.7';
        e.currentTarget.style.background = 'rgba(59,130,246,0.3)';
        e.currentTarget.style.borderColor = 'rgba(59,130,246,0.7)';
    },

    onComponentTouchEnd: function(e) {
        if (!this.touchDraggingComponent) return;
        
        const touch = e.changedTouches[0];
        const canvasRect = this.canvas.getBoundingClientRect();
        
        if (touch.clientX >= canvasRect.left && touch.clientX <= canvasRect.right && 
            touch.clientY >= canvasRect.top && touch.clientY <= canvasRect.bottom) {
            const x = (touch.clientX - canvasRect.left - this.offset.x) / this.scale;
            const y = (touch.clientY - canvasRect.top - this.offset.y) / this.scale;
            this.addCalculatorNode(this.touchDraggingComponent.moduleKey, this.touchDraggingComponent.calcKey, x, y);
            this.showNotification('✅ Component added to canvas', 'success', 2000);
        } else {
            this.showNotification('⚠️ Drop component on the canvas area', 'warning', 2000);
        }

        if (this.touchDraggingComponent.element) {
            this.touchDraggingComponent.element.style.opacity = '1';
            this.touchDraggingComponent.element.style.background = 'rgba(30,41,59,0.5)';
            this.touchDraggingComponent.element.style.borderColor = 'rgba(59,130,246,0.3)';
        }
        this.touchDraggingComponent = null;
    },

    handleMouseDown: function(e) {
        const pos = this.getMousePos(e);
        
        if (e.button === 2) {
            e.preventDefault();
            const conn = this.getConnectionAt(pos.x, pos.y);
            if (conn) {
                this.deleteConnection(conn);
                return;
            }
            
            const clickedNode = [...this.nodes].reverse().find(n => n.isAt(pos.x, pos.y));
            if (clickedNode) {
                this.showNodeContextMenu(clickedNode, e);
                return;
            }
        }

        if (e.detail === 2) {
            const clickedNode = [...this.nodes].reverse().find(n => n.isAt(pos.x, pos.y));
            if (clickedNode) {
                this.renameNode(clickedNode);
                return;
            }
        }

        let clickedPort = null;
        for (const node of this.nodes) {
            const portClick = node.getPortAt(pos.x, pos.y);
            if (portClick) {
                clickedPort = { node, portClick };
                break;
            }
        }

        if (clickedPort) {
            e.stopPropagation();
            this.startConnection(clickedPort.node, clickedPort.portClick.index, clickedPort.portClick.type);
            return;
        }

        this.selectedNode = [...this.nodes].reverse().find(n => n.isAt(pos.x, pos.y));
        if (this.selectedNode) {
            this.isDragging = true;
            this.dragStart = { x: pos.x - this.selectedNode.x, y: pos.y - this.selectedNode.y };
            this.updateProperties(this.selectedNode);
        } else {
            this.isDragging = true;
            this.dragStart = { x: e.clientX - this.offset.x, y: e.clientY - this.offset.y };
            this.selectedNode = null;
            this.updateProperties(null);
        }
        
        this.render();
    },

    getConnectionAt: function(x, y) {
        const threshold = 10;
        for (const conn of this.connections) {
            const fromPos = conn.fromNode.getOutputPortPos(conn.fromPort);
            const toPos = conn.toNode.getInputPortPos(conn.toPort);
            
            const cpDist = Math.abs(toPos.x - fromPos.x) / 2;
            const midX = (fromPos.x + toPos.x) / 2;
            const midY = (fromPos.y + toPos.y) / 2;
            
            const dist = Math.sqrt((x - midX) ** 2 + (y - midY) ** 2);
            if (dist < threshold) {
                return conn;
            }
        }
        return null;
    },

    handleMouseMove: function(e) {
        const pos = this.getMousePos(e);
        
        if (this.isConnecting) {
            this.tempWireEnd = pos;
            this.hoveredPort = null;
            
            for (const node of this.nodes) {
                const portClick = node.getPortAt(pos.x, pos.y);
                if (portClick && this.canConnect(this.connectionStart, { node, ...portClick })) {
                    this.hoveredPort = { node, ...portClick };
                    break;
                }
            }
            
            this.render();
            return;
        }

        if (!this.isDragging) return;
        
        if (this.selectedNode) {
            this.selectedNode.x = pos.x - this.dragStart.x;
            this.selectedNode.y = pos.y - this.dragStart.y;
        } else {
            this.offset.x = e.clientX - this.dragStart.x;
            this.offset.y = e.clientY - this.dragStart.y;
        }
        
        this.render();
    },

    handleMouseUp: function(e) {
        if (this.isConnecting) {
            const pos = this.getMousePos(e);
            
            for (const node of this.nodes) {
                const portClick = node.getPortAt(pos.x, pos.y);
                if (portClick && this.canConnect(this.connectionStart, { node, ...portClick })) {
                    this.createConnection(this.connectionStart, { node, ...portClick });
                    break;
                }
            }
            
            this.isConnecting = false;
            this.connectionStart = null;
            this.tempWireEnd = null;
            this.hoveredPort = null;
            this.canvas.style.cursor = 'default';
        }
        
        if (this.isDragging && this.selectedNode) {
            this.saveState();
        }
        
        this.isDragging = false;
        this.render();
    },

    handleWheel: function(e) {
        e.preventDefault();
        const oldScale = this.scale;
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = Math.max(0.3, Math.min(3, oldScale * zoomFactor));
        
        if (newScale !== oldScale) {
            const canvasPos = this.screenToCanvas(e.clientX, e.clientY);
            this.scale = newScale;
            const newScreenPos = this.canvasToScreen(canvasPos.x, canvasPos.y);
            this.offset.x += e.clientX - this.canvas.getBoundingClientRect().left - newScreenPos.x;
            this.offset.y += e.clientY - this.canvas.getBoundingClientRect().top - newScreenPos.y;
        }
        
        this.render();
    },

    handleTouchStart: function(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY,
                button: 0
            });
            this.handleMouseDown(mouseEvent);
        } else if (e.touches.length === 2) {
            this.touchDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
            this.isDragging = false;
        }
    },

    handleTouchMove: function(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.handleMouseMove(mouseEvent);
        } else if (e.touches.length === 2) {
            const newDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
            const oldScale = this.scale;
            const scaleChange = newDistance / this.touchDistance;
            const newScale = Math.max(0.3, Math.min(3, oldScale * scaleChange));
            
            if (newScale !== oldScale) {
                const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
                const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
                const canvasPos = this.screenToCanvas(centerX, centerY);
                
                this.scale = newScale;
                const newScreenPos = this.canvasToScreen(canvasPos.x, canvasPos.y);
                this.offset.x += centerX - this.canvas.getBoundingClientRect().left - newScreenPos.x;
                this.offset.y += centerY - this.canvas.getBoundingClientRect().top - newScreenPos.y;
                
                this.render();
            }
            
            this.touchDistance = newDistance;
        }
    },

    handleTouchEnd: function(e) {
        e.preventDefault();
        if (e.touches.length === 0) {
            const mouseEvent = new MouseEvent('mouseup', {
                clientX: e.changedTouches[0].clientX,
                clientY: e.changedTouches[0].clientY
            });
            this.handleMouseUp(mouseEvent);
            this.touchDistance = null;
        } else if (e.touches.length === 1) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.handleMouseMove(mouseEvent);
        }
    },

    getTouchDistance: function(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    },

    getMousePos: function(e) {
        return this.screenToCanvas(e.clientX, e.clientY);
    },

    screenToCanvas: function(screenX, screenY) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (screenX - rect.left - this.offset.x) / this.scale,
            y: (screenY - rect.top - this.offset.y) / this.scale
        };
    },

    canvasToScreen: function(canvasX, canvasY) {
        return {
            x: canvasX * this.scale + this.offset.x,
            y: canvasY * this.scale + this.offset.y
        };
    },

    startConnection: function(node, portIndex, portType) {
        if (portType !== 'output') {
            console.log('Can only start connections from output ports (right side)');
            this.showNotification('⚠️ Start connections from output ports (right side)', 'warning', 2000);
            return;
        }
        
        this.isConnecting = true;
        this.connectionStart = { node, portIndex, portType };
        this.isDragging = false;
        this.canvas.style.cursor = 'crosshair';
        this.showNotification('🔌 Drag to an input port (left side)', 'info', 1500);
    },

    canConnect: function(from, to) {
        if (from.portType !== 'output' || to.type !== 'input') return false;
        if (from.node === to.node) return false;
        
        const exists = this.connections.some(c => 
            c.fromNode === from.node && c.fromPort === from.portIndex && 
            c.toNode === to.node && c.toPort === to.index
        );
        if (exists) return false;
        
        const inputAlreadyConnected = this.connections.some(c => 
            c.toNode === to.node && c.toPort === to.index
        );
        
        if (inputAlreadyConnected) {
            this.showNotification('⚠️ Input already connected - will replace', 'warning', 1500);
        }
        
        const fromPort = from.node.outputPorts[from.portIndex];
        const toPort = to.node.inputPorts[to.index];
        
        return fromPort.type === toPort.type || fromPort.type === 'any' || toPort.type === 'any' || 
               (fromPort.type === 'number' && toPort.type === 'string');
    },

    createConnection: function(from, to) {
        this.connections = this.connections.filter(c => !(c.toNode === to.node && c.toPort === to.index));
        this.connections.push({
            fromNode: from.node,
            fromPort: from.portIndex,
            toNode: to.node,
            toPort: to.index
        });
        
        const fanOutCount = this.connections.filter(c => 
            c.fromNode === from.node && c.fromPort === from.portIndex
        ).length;
        
        this.saveState();
        
        if (fanOutCount > 1) {
            this.showNotification(`✓ Connected ${from.node.name} → ${to.node.name} (Fan-out: ${fanOutCount} targets)`, 'success', 2500);
        } else {
            this.showNotification(`✓ Connected ${from.node.name} → ${to.node.name}`, 'success', 2000);
        }
        
        this.render();
    },

    deleteConnection: function(conn) {
        this.connections = this.connections.filter(c => c !== conn);
        this.saveState();
        this.showNotification('Connection removed', 'info', 2000);
        this.render();
    },

    render: function() {
        if (!this.ctx) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.save();
        this.ctx.translate(this.offset.x, this.offset.y);
        this.ctx.scale(this.scale, this.scale);
        
        this.drawGrid();
        this.connections.forEach(c => this.drawConnection(c));
        
        if (this.isConnecting && this.tempWireEnd) {
            this.drawTempWire();
        }
        
        this.nodes.forEach(n => n.draw(this.ctx, n === this.selectedNode, this.connections));
        
        this.ctx.restore();
    },

    drawGrid: function() {
        const rect = this.canvas.getBoundingClientRect();
        const gridSize = 50;
        const minorGridSize = 10;
        
        const startX = Math.floor(-this.offset.x / this.scale / gridSize) * gridSize;
        const startY = Math.floor(-this.offset.y / this.scale / gridSize) * gridSize;
        const endX = startX + rect.width / this.scale + gridSize;
        const endY = startY + rect.height / this.scale + gridSize;
        
        if (this.scale > 0.5) {
            this.ctx.fillStyle = '#1a1a1a';
            for (let x = Math.floor(startX / minorGridSize) * minorGridSize; x < endX; x += minorGridSize) {
                for (let y = Math.floor(startY / minorGridSize) * minorGridSize; y < endY; y += minorGridSize) {
                    this.ctx.fillRect(x - 0.5, y - 0.5, 1, 1);
                }
            }
        }
        
        this.ctx.strokeStyle = '#2a2a2a';
        this.ctx.lineWidth = 1;
        for (let x = startX; x < endX; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, startY);
            this.ctx.lineTo(x, endY);
            this.ctx.stroke();
        }
        for (let y = startY; y < endY; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(startX, y);
            this.ctx.lineTo(endX, y);
            this.ctx.stroke();
        }
    },

    drawConnection: function(conn) {
        const fromPos = conn.fromNode.getOutputPortPos(conn.fromPort);
        const toPos = conn.toNode.getInputPortPos(conn.toPort);
        const fromPort = conn.fromNode.outputPorts[conn.fromPort];
        const toPort = conn.toNode.inputPorts[conn.toPort];
        
        const colors = {
            number: '#3b82f6',
            string: '#10b981',
            object: '#a855f7',
            boolean: '#f59e0b',
            any: '#64748b'
        };
        
        const color = colors[fromPort.type] || colors.any;
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = color.replace(')', ', 0.4)').replace('rgb', 'rgba');
        
        const dx = toPos.x - fromPos.x;
        const dy = toPos.y - fromPos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const tension = Math.min(distance * 0.4, 150);
        
        this.ctx.beginPath();
        this.ctx.moveTo(fromPos.x, fromPos.y);
        this.ctx.bezierCurveTo(
            fromPos.x + tension, fromPos.y,
            toPos.x - tension, toPos.y,
            toPos.x, toPos.y
        );
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;
        
        this.drawConnectionArrow(toPos, fromPos, color);
    },

    drawConnectionArrow: function(toPos, fromPos, color) {
        const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
        const arrowSize = 8;
        
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.moveTo(toPos.x, toPos.y);
        this.ctx.lineTo(
            toPos.x - arrowSize * Math.cos(angle - Math.PI / 6),
            toPos.y - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.lineTo(
            toPos.x - arrowSize * Math.cos(angle + Math.PI / 6),
            toPos.y - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.closePath();
        this.ctx.fill();
    },

    drawTempWire: function() {
        const fromPos = this.connectionStart.node.getOutputPortPos(this.connectionStart.portIndex);
        const isValid = this.hoveredPort !== null;
        
        this.ctx.strokeStyle = isValid ? '#10b981' : '#60a5fa';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        this.ctx.beginPath();
        this.ctx.moveTo(fromPos.x, fromPos.y);
        this.ctx.lineTo(this.tempWireEnd.x, this.tempWireEnd.y);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        if (this.hoveredPort) {
            const hoverPos = this.hoveredPort.type === 'input' 
                ? this.hoveredPort.node.getInputPortPos(this.hoveredPort.index)
                : this.hoveredPort.node.getOutputPortPos(this.hoveredPort.index);
                
            this.ctx.strokeStyle = '#10b981';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(hoverPos.x, hoverPos.y, 10, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    },

    updateProperties: function(node) {
        const container = document.getElementById('builder-props-content');
        if (!container) return;
        
        if (!node) {
            container.innerHTML = '<p class="text-muted">Select a calculator node to edit properties</p>';
            return;
        }
        
        container.innerHTML = node.getPropertiesHTML();
    },

    onPropChange: function(nodeId, key, value) {
        const node = this.nodes.find(n => n.id === nodeId);
        if (node) {
            const field = node.fields.find(f => f.name === key);
            if (field) {
                if (field.type === 'number') {
                    value = parseFloat(value) || 0;
                } else if (field.type === 'checkbox') {
                    value = value === 'true' || value === true;
                }
            }
            
            node.inputValues[key] = value;
            node.hasError = false;
            this.render();
            
            if (this.selectedNode === node) {
                this.updateProperties(node);
            }
        }
    },

    executeWorkflow: async function() {
        try {
            if (this.nodes.length === 0) {
                this.showNotification('No nodes to execute', 'warning', 3000);
                return;
            }
            
            const order = this.topologicalSort();
            if (!order) {
                this.showNotification('❌ Circular dependency detected! Cannot execute workflow with loops.', 'error', 5000);
                return;
            }
            
            this.showNotification(`🚀 Executing workflow with ${order.length} nodes...`, 'info', 2000);
            
            let results = [];
            let errors = [];
            
            for (let i = 0; i < order.length; i++) {
                const node = order[i];
                try {
                    const inputs = { ...node.inputValues };
                    
                    this.connections.forEach(conn => {
                        if (conn.toNode === node) {
                            const fromResult = conn.fromNode.outputValues;
                            const fromPort = conn.fromNode.outputPorts[conn.fromPort];
                            const toPort = node.inputPorts[conn.toPort];
                            
                            if (fromResult && fromResult[fromPort.name] !== undefined) {
                                inputs[toPort.name] = fromResult[fromPort.name];
                            }
                        }
                    });
                    
                    const missingInputs = node.inputPorts
                        .filter(port => {
                            const field = node.fields.find(f => f.name === port.name);
                            return field && field.required && !inputs[port.name];
                        })
                        .map(port => port.label);
                        
                    if (missingInputs.length > 0) {
                        throw new Error(`Missing required inputs: ${missingInputs.join(', ')}`);
                    }
                    
                    const result = await node.execute(inputs);
                    results.push({ node: node.name, result });
                    node.hasError = false;
                    this.render();
                    
                } catch (error) {
                    node.hasError = true;
                    node.errorMessage = error.message;
                    errors.push({ node: node.name, error: error.message });
                    console.error(`Error in node ${node.name}:`, error);
                    this.render();
                }
            }
            
            if (errors.length === 0) {
                this.showNotification(`✅ Workflow completed! Processed ${results.length} calculators.`, 'success', 4000);
            } else {
                this.showNotification(`⚠️ Workflow completed with ${errors.length} error(s). Check console for details.`, 'warning', 5000);
            }
            
            if (this.selectedNode) {
                this.updateProperties(this.selectedNode);
            }
            
            this.render();
            
        } catch (error) {
            console.error('Workflow execution error:', error);
            this.showNotification('❌ Workflow execution failed: ' + error.message, 'error', 5000);
        }
    },

    topologicalSort: function() {
        const visited = new Set();
        const temp = new Set();
        const order = [];
        
        const visit = (node) => {
            if (temp.has(node)) return false;
            if (visited.has(node)) return true;
            
            temp.add(node);
            const deps = this.connections.filter(c => c.toNode === node).map(c => c.fromNode);
            
            for (const dep of deps) {
                if (!visit(dep)) return false;
            }
            
            temp.delete(node);
            visited.add(node);
            order.push(node);
            return true;
        };
        
        for (const node of this.nodes) {
            if (!visit(node)) return null;
        }
        
        return order;
    },

    zoomIn: function() {
        this.scale = Math.min(3, this.scale * 1.1);
        this.render();
    },

    zoomOut: function() {
        this.scale = Math.max(0.3, this.scale * 0.9);
        this.render();
    },

    resetView: function() {
        this.offset = { x: 0, y: 0 };
        this.scale = 1;
        this.render();
    },

    fitToScreen: function() {
        if (this.nodes.length === 0) {
            this.resetView();
            return;
        }
        
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        
        this.nodes.forEach(node => {
            minX = Math.min(minX, node.x);
            minY = Math.min(minY, node.y);
            maxX = Math.max(maxX, node.x + node.width);
            maxY = Math.max(maxY, node.y + node.height);
        });
        
        const rect = this.canvas.getBoundingClientRect();
        const padding = 50;
        const contentWidth = maxX - minX + padding * 2;
        const contentHeight = maxY - minY + padding * 2;
        
        const scaleX = rect.width / contentWidth;
        const scaleY = rect.height / contentHeight;
        this.scale = Math.min(scaleX, scaleY, 2);
        
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        this.offset.x = rect.width / 2 - centerX * this.scale;
        this.offset.y = rect.height / 2 - centerY * this.scale;
        
        this.render();
    },

    clearWorkflow: function() {
        if (this.nodes.length === 0) return;
        
        if (confirm('Are you sure you want to clear all nodes and connections? This cannot be undone.')) {
            this.nodes = [];
            this.connections = [];
            this.selectedNode = null;
            this.updateProperties(null);
            this.saveState();
            this.render();
            this.showNotification('🗑️ Workflow cleared', 'info', 2000);
        }
    },

    saveState: function() {
        const state = this.serializeWorkflow();
        this.undoStack.push(state);
        if (this.undoStack.length > this.maxHistorySize) {
            this.undoStack.shift();
        }
        this.redoStack = [];
        this.updateHistoryButtons();
    },

    undo: function() {
        if (this.undoStack.length === 0) {
            this.showNotification('Nothing to undo', 'info', 1500);
            return;
        }
        
        this.redoStack.push(this.serializeWorkflow());
        const prevState = this.undoStack.pop();
        this.restoreWorkflow(prevState);
        this.updateHistoryButtons();
        this.showNotification('↶ Undo', 'info', 1000);
    },

    redo: function() {
        if (this.redoStack.length === 0) {
            this.showNotification('Nothing to redo', 'info', 1500);
            return;
        }
        
        this.undoStack.push(this.serializeWorkflow());
        const nextState = this.redoStack.pop();
        this.restoreWorkflow(nextState);
        this.updateHistoryButtons();
        this.showNotification('↷ Redo', 'info', 1000);
    },

    updateHistoryButtons: function() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');
        if (undoBtn) undoBtn.disabled = this.undoStack.length === 0;
        if (redoBtn) redoBtn.disabled = this.redoStack.length === 0;
    },

    serializeWorkflow: function() {
        return JSON.stringify({
            nodes: this.nodes.map(n => ({
                id: n.id,
                name: n.name,
                moduleKey: n.moduleKey,
                calcKey: n.calcKey,
                x: n.x,
                y: n.y,
                inputValues: n.inputValues,
                outputValues: n.outputValues
            })),
            connections: this.connections.map(c => ({
                fromNodeId: c.fromNode.id,
                fromPort: c.fromPort,
                toNodeId: c.toNode.id,
                toPort: c.toPort
            }))
        });
    },

    restoreWorkflow: function(stateJson) {
        try {
            const state = JSON.parse(stateJson);
            
            this.nodes = state.nodes.map(nodeData => {
                const calcDef = this.calculatorFields[nodeData.calcKey] || {
                    fields: [{ name: 'value', label: 'Value', type: 'number', required: true }],
                    outputs: [{ name: 'result', label: 'Result', type: 'number' }]
                };
                
                const node = new CalculatorNode(
                    nodeData.id,
                    nodeData.name,
                    nodeData.moduleKey,
                    nodeData.calcKey,
                    nodeData.x,
                    nodeData.y,
                    calcDef.fields,
                    calcDef.outputs
                );
                
                node.inputValues = nodeData.inputValues || {};
                node.outputValues = nodeData.outputValues || {};
                return node;
            });
            
            this.connections = state.connections.map(connData => {
                const fromNode = this.nodes.find(n => n.id === connData.fromNodeId);
                const toNode = this.nodes.find(n => n.id === connData.toNodeId);
                return { fromNode, fromPort: connData.fromPort, toNode, toPort: connData.toPort };
            }).filter(c => c.fromNode && c.toNode);
            
            this.selectedNode = null;
            this.updateProperties(null);
            this.render();
            
        } catch (error) {
            console.error('Error restoring workflow:', error);
            this.showNotification('Error restoring workflow', 'error', 3000);
        }
    },

    saveWorkflow: function() {
        try {
            const state = this.serializeWorkflow();
            const blob = new Blob([state], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `workflow_${new Date().getTime()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            this.showNotification('💾 Workflow saved', 'success', 2000);
        } catch (error) {
            console.error('Error saving workflow:', error);
            this.showNotification('Error saving workflow', 'error', 3000);
        }
    },

    loadWorkflow: function() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    this.restoreWorkflow(event.target.result);
                    this.undoStack = [];
                    this.redoStack = [];
                    this.updateHistoryButtons();
                    this.showNotification('📂 Workflow loaded', 'success', 2000);
                } catch (error) {
                    console.error('Error loading workflow:', error);
                    this.showNotification('Error loading workflow file', 'error', 3000);
                }
            };
            reader.readAsText(file);
        };
        input.click();
    },

    exampleWorkflows: {
        electrical_power_distribution: {
            name: '⚡ Electrical Power Distribution System',
            description: 'Load calculation → Cable sizing → Transformer sizing',
            workflow: {
                nodes: [
                    { id: 1001, name: 'Load Calculation', moduleKey: 'electrical', calcKey: 'loadCalculation', x: 100, y: 200, inputValues: {}, outputValues: {} },
                    { id: 1002, name: 'Cable Sizing', moduleKey: 'electrical', calcKey: 'cableSizing', x: 400, y: 200, inputValues: {}, outputValues: {} },
                    { id: 1003, name: 'Transformer Sizing', moduleKey: 'electrical', calcKey: 'transformerSizing', x: 700, y: 200, inputValues: {}, outputValues: {} }
                ],
                connections: [
                    { fromNodeId: 1001, fromPort: 0, toNodeId: 1002, toPort: 0 },
                    { fromNodeId: 1001, fromPort: 1, toNodeId: 1003, toPort: 0 }
                ]
            }
        },
        piping_system: {
            name: '🔧 Piping & Pump System Design',
            description: 'Pipe sizing → Pump sizing with shared flow rate',
            workflow: {
                nodes: [
                    { id: 2001, name: 'Pipe Sizing', moduleKey: 'mechanical', calcKey: 'pipeSizing', x: 200, y: 250, inputValues: {}, outputValues: {} },
                    { id: 2002, name: 'Pump Sizing', moduleKey: 'mechanical', calcKey: 'pumpSizing', x: 550, y: 250, inputValues: {}, outputValues: {} }
                ],
                connections: [
                    { fromNodeId: 2001, fromPort: 0, toNodeId: 2002, toPort: 0 }
                ]
            }
        },
        concrete_structure: {
            name: '🏗️ Concrete Structure Design',
            description: 'Concrete volume calculation → Steel reinforcement',
            workflow: {
                nodes: [
                    { id: 4001, name: 'Concrete Volume', moduleKey: 'civil', calcKey: 'concreteVolume', x: 200, y: 200, inputValues: {}, outputValues: {} },
                    { id: 4002, name: 'Steel Weight', moduleKey: 'civil', calcKey: 'steelWeight', x: 550, y: 200, inputValues: {}, outputValues: {} }
                ],
                connections: []
            }
        }
    },

    loadExample: function(exampleKey) {
        const example = this.exampleWorkflows[exampleKey];
        if (!example) {
            this.showNotification('Example not found', 'error', 2000);
            return;
        }
        
        try {
            const workflowJson = JSON.stringify(example.workflow);
            this.restoreWorkflow(workflowJson);
            this.undoStack = [];
            this.redoStack = [];
            this.updateHistoryButtons();
            this.showNotification(`📚 Loaded: ${example.name}`, 'success', 3000);
            console.log('Loaded example:', example.name);
        } catch (error) {
            console.error('Error loading example:', error);
            this.showNotification('Error loading example workflow', 'error', 3000);
        }
    },

    showExamplesMenu: function() {
        const menu = document.getElementById('examples-menu');
        if (!menu) return;

        if (!this.examplesMenuInitialized) {
            this.populateExamplesMenu();
        }
        
        const isHidden = menu.style.display === 'none' || !menu.style.display;
        menu.style.display = isHidden ? 'block' : 'none';
    },

    showNodeContextMenu: function(node, e) {
        const menu = document.createElement('div');
        menu.style.cssText = `
            position: fixed;
            left: ${e.clientX}px;
            top: ${e.clientY}px;
            background: rgba(30,41,59,0.98);
            border: 2px solid rgba(59,130,246,0.5);
            border-radius: 8px;
            padding: 0.5rem;
            z-index: 10000;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            backdrop-filter: blur(12px);
        `;
        
        menu.innerHTML = `
            <div style="padding: 0.5rem 1rem; cursor: pointer; color: #60a5fa; border-radius: 4px; transition: all 0.2s; font-weight: 600;"
                 onmouseover="this.style.background='rgba(59,130,246,0.2)';"
                 onmouseout="this.style.background='transparent';"
                 onclick="VisualWorkflow.renameNode(VisualWorkflow.nodes.find(n=>n.id===${node.id})); this.parentElement.remove();">
                ✏️ Rename
            </div>
            <div style="padding: 0.5rem 1rem; cursor: pointer; color: #ef4444; border-radius: 4px; transition: all 0.2s; font-weight: 600;"
                 onmouseover="this.style.background='rgba(239,68,68,0.2)';"
                 onmouseout="this.style.background='transparent';"
                 onclick="VisualWorkflow.deleteNode(VisualWorkflow.nodes.find(n=>n.id===${node.id})); this.parentElement.remove();">
                🗑️ Delete
            </div>
        `;
        
        document.body.appendChild(menu);
        
        setTimeout(() => {
            const closeMenu = (ev) => {
                if (!menu.contains(ev.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            };
            document.addEventListener('click', closeMenu);
        }, 100);
    },

    renameNode: function(node) {
        if (!node) return;
        
        const newName = prompt('Enter new name for this node:', node.name);
        if (newName && newName.trim()) {
            node.name = newName.trim();
            this.saveState();
            this.render();
            this.updateProperties(node);
            this.showNotification('✓ Node renamed', 'success', 1500);
        }
    },

    generateWorkflowReport: function() {
        if (this.nodes.length === 0) {
            this.showNotification('No workflow to report', 'warning', 2000);
            return;
        }

        let report = {
            title: 'Visual Workflow Execution Report',
            timestamp: new Date().toLocaleString(),
            nodes: [],
            connections: [],
            executionOrder: []
        };

        try {
            const sorted = this.topologicalSort();
            report.executionOrder = sorted.map(n => n.name);

            sorted.forEach(node => {
                const hasOutputs = Object.keys(node.outputValues || {}).length > 0;
                const nodeData = {
                    name: node.name,
                    type: `${node.moduleKey}-${node.calcKey}`,
                    status: node.hasError ? 'error' : (hasOutputs ? 'completed' : 'pending'),
                    inputs: {},
                    outputs: {}
                };

                node.inputPorts.forEach(port => {
                    const value = node.inputValues[port.name];
                    nodeData.inputs[port.label] = value !== undefined ? value : 'Not set';
                });

                node.outputPorts.forEach(port => {
                    const value = node.outputValues[port.name];
                    nodeData.outputs[port.label] = value !== undefined ? value : 'Not calculated';
                });

                report.nodes.push(nodeData);
            });

            this.connections.forEach(conn => {
                report.connections.push({
                    from: `${conn.fromNode.name} [${conn.fromNode.outputPorts[conn.fromPort].label}]`,
                    to: `${conn.toNode.name} [${conn.toNode.inputPorts[conn.toPort].label}]`
                });
            });

        } catch (error) {
            report.error = error.message;
        }

        // Try backend API first, fallback to client-side generation
        const token = localStorage.getItem('token');
        if (token) {
            fetch('/analytics/generate-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    report_type: 'workflow',
                    format: 'html',
                    content: {
                        title: report.title,
                        nodes: report.nodes,
                        connections: report.connections,
                        execution_order: report.executionOrder,
                        error: report.error || null
                    }
                })
            })
            .then(res => res.ok ? res.json() : Promise.reject('API error'))
            .then(data => {
                if (data.success && data.html) {
                    this._downloadReportHTML(data.html, data.report_id);
                } else {
                    this._downloadReportHTML(this.generateReportHTML(report));
                }
            })
            .catch(() => {
                this._downloadReportHTML(this.generateReportHTML(report));
            });
        } else {
            this._downloadReportHTML(this.generateReportHTML(report));
        }

        this.showNotification('Workflow report generated', 'success', 2000);
    },

    _downloadReportHTML: function(html, reportId) {
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `workflow_report_${reportId || Date.now()}.html`;
        a.click();
        URL.revokeObjectURL(url);
    },

    _escHTML: function(value) {
        if (value === null || value === undefined) return 'N/A';
        const div = document.createElement('div');
        div.textContent = String(value);
        return div.innerHTML;
    },

    generateReportHTML: function(report) {
        const e = this._escHTML;
        const now = new Date();
        const reportId = `RPT-${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}`;
        const dateStr = now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        const totalNodes = report.nodes.length;
        const completedNodes = report.nodes.filter(n => n.status === 'completed').length;
        const errorNodes = report.nodes.filter(n => n.status === 'error').length;
        const pendingNodes = report.nodes.filter(n => n.status === 'pending').length;

        // Execution order steps
        const orderHTML = report.executionOrder.length > 0
            ? `<ol class="step-list">${report.executionOrder.map(name => `<li class="step-item">${e(name)}</li>`).join('')}</ol>`
            : '<p>No execution order determined.</p>';

        // Node detail cards
        const nodesHTML = report.nodes.map((node, i) => {
            const statusClass = node.status === 'completed' ? 'badge-pass' : node.status === 'error' ? 'badge-fail' : 'badge-info';
            const inputRows = Object.entries(node.inputs).map(([k, v]) =>
                `<tr><td>${e(k)}</td><td>${e(v)}</td></tr>`
            ).join('') || '<tr><td colspan="2">No inputs</td></tr>';
            const outputRows = Object.entries(node.outputs).map(([k, v]) =>
                `<tr><td>${e(k)}</td><td>${e(v)}</td></tr>`
            ).join('') || '<tr><td colspan="2">Not calculated</td></tr>';

            return `
                <div class="section" style="margin-left: 15px;">
                    <div class="subsection-title">
                        Node ${i + 1}: ${e(node.name)}
                        <span class="badge ${statusClass}" style="margin-left: 10px;">${e(node.status)}</span>
                    </div>
                    <p style="font-size: 9pt; color: #7f8c8d; margin-bottom: 8px;">Type: ${e(node.type)}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div class="subsection-title" style="font-size: 10pt;">Input Parameters</div>
                            <table class="data-table">
                                <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
                                <tbody>${inputRows}</tbody>
                            </table>
                        </div>
                        <div>
                            <div class="subsection-title" style="font-size: 10pt;">Output Results</div>
                            <table class="data-table">
                                <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
                                <tbody>${outputRows}</tbody>
                            </table>
                        </div>
                    </div>
                </div>`;
        }).join('');

        // Connections
        const connectionsHTML = report.connections.map(conn =>
            `<div class="connection-item">${e(conn.from)} <span class="connection-arrow">&rarr;</span> ${e(conn.to)}</div>`
        ).join('') || '<p>No connections defined.</p>';

        // Error note
        const errorHTML = report.error
            ? `<div class="section"><div class="section-title">6. Notes</div><div class="note-box">${e(report.error)}</div></div>`
            : '';

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Workflow Execution Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; color: #2c3e50; font-size: 11pt; line-height: 1.5; }
        .page { padding: 30px 40px; }
        .report-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #2c3e50; padding-bottom: 15px; margin-bottom: 25px; }
        .header-left { flex: 1; }
        .header-right { text-align: right; font-size: 9pt; color: #7f8c8d; }
        .report-title { font-size: 20pt; font-weight: 700; color: #2c3e50; margin-bottom: 4px; }
        .report-subtitle { font-size: 11pt; color: #7f8c8d; }
        .report-id { font-size: 9pt; color: #95a5a6; font-family: monospace; }
        .meta-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .meta-table td { padding: 6px 12px; border: 1px solid #dce1e7; font-size: 10pt; }
        .meta-table td:first-child { background: #f7f9fc; font-weight: 600; width: 180px; color: #34495e; }
        .section { margin-bottom: 22px; page-break-inside: avoid; }
        .section-title { font-size: 13pt; font-weight: 700; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-bottom: 12px; }
        .subsection-title { font-size: 11pt; font-weight: 600; color: #34495e; margin: 10px 0 6px 0; }
        .data-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 10pt; }
        .data-table th { background: #2c3e50; color: white; padding: 8px 12px; text-align: left; font-weight: 600; }
        .data-table td { padding: 7px 12px; border-bottom: 1px solid #ecf0f1; }
        .data-table tr:nth-child(even) { background: #f7f9fc; }
        .data-table tr:hover { background: #edf2f7; }
        .result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin: 10px 0; }
        .result-card { background: #f7f9fc; border: 1px solid #dce1e7; border-radius: 6px; padding: 12px; text-align: center; }
        .result-card .label { font-size: 9pt; color: #7f8c8d; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .result-card .value { font-size: 16pt; font-weight: 700; color: #2c3e50; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 9pt; font-weight: 600; }
        .badge-pass { background: #d5f5e3; color: #27ae60; }
        .badge-fail { background: #fadbd8; color: #e74c3c; }
        .badge-info { background: #d6eaf8; color: #2980b9; }
        .step-list { list-style: none; padding: 0; counter-reset: step-counter; }
        .step-item { position: relative; padding: 10px 12px 10px 50px; margin-bottom: 8px; background: #f7f9fc; border-radius: 6px; border-left: 3px solid #3498db; counter-increment: step-counter; }
        .step-item::before { content: counter(step-counter); position: absolute; left: 12px; top: 10px; width: 24px; height: 24px; background: #3498db; color: white; border-radius: 50%; text-align: center; line-height: 24px; font-size: 10pt; font-weight: 700; }
        .connection-item { padding: 6px 12px; margin-bottom: 5px; background: #edf2f7; border-radius: 4px; font-size: 10pt; border-left: 3px solid #2c3e50; }
        .connection-arrow { color: #3498db; font-weight: 700; margin: 0 6px; }
        .note-box { background: #fef9e7; border-left: 4px solid #f39c12; padding: 12px 15px; margin: 10px 0; border-radius: 0 6px 6px 0; font-size: 10pt; }
        .signature-block { margin-top: 40px; display: flex; justify-content: space-between; }
        .signature-col { width: 45%; }
        .signature-line { border-top: 1px solid #2c3e50; margin-top: 40px; padding-top: 5px; font-size: 10pt; }
        .signature-label { font-size: 9pt; color: #7f8c8d; }
        .report-footer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #dce1e7; font-size: 8pt; color: #95a5a6; display: flex; justify-content: space-between; }
        @media print { .page { padding: 20px; } .section { page-break-inside: avoid; } }
    </style>
</head>
<body>
<div class="page">
    <div class="report-header">
        <div class="header-left">
            <div class="report-title">Workflow Execution Report</div>
            <div class="report-subtitle">${e(report.title)}</div>
            <div class="report-id">${reportId}</div>
        </div>
        <div class="header-right">
            <strong>EngiSuite Analytics Pro</strong><br>
            ${dateStr} ${timeStr}
        </div>
    </div>

    <div class="section">
        <div class="section-title">1. Project Information</div>
        <table class="meta-table">
            <tr><td>Report Title</td><td>${e(report.title)}</td></tr>
            <tr><td>Execution Date</td><td>${now.toISOString().slice(0, 19).replace('T', ' ')}</td></tr>
            <tr><td>Total Nodes</td><td>${totalNodes}</td></tr>
            <tr><td>Total Connections</td><td>${report.connections.length}</td></tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">2. Execution Summary</div>
        <div class="result-grid">
            <div class="result-card">
                <div class="label">Total Nodes</div>
                <div class="value">${totalNodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Completed</div>
                <div class="value" style="color: #27ae60;">${completedNodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Errors</div>
                <div class="value" style="color: ${errorNodes > 0 ? '#e74c3c' : '#27ae60'};">${errorNodes}</div>
            </div>
            <div class="result-card">
                <div class="label">Pending</div>
                <div class="value" style="color: ${pendingNodes > 0 ? '#f39c12' : '#27ae60'};">${pendingNodes}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">3. Execution Order</div>
        ${orderHTML}
    </div>

    <div class="section">
        <div class="section-title">4. Node Details &amp; Results</div>
        ${nodesHTML || '<p>No nodes in workflow.</p>'}
    </div>

    <div class="section">
        <div class="section-title">5. Data Flow Connections</div>
        ${connectionsHTML}
    </div>

    ${errorHTML}

    <div class="signature-block">
        <div class="signature-col">
            <div class="signature-line">
                <strong>Prepared By</strong><br>
                <span class="signature-label">Engineer / Date</span>
            </div>
        </div>
        <div class="signature-col">
            <div class="signature-line">
                <strong>Reviewed By</strong><br>
                <span class="signature-label">Reviewer / Date</span>
            </div>
        </div>
    </div>

    <div class="report-footer">
        <span>${reportId}</span>
        <span>EngiSuite Analytics Pro - Confidential</span>
        <span>${now.toISOString().slice(0, 16).replace('T', ' ')}</span>
    </div>
</div>
</body>
</html>`;
    },

    showNotification: function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10001;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            font-weight: 500;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
};

class CalculatorNode {
    constructor(id, name, moduleKey, calcKey, x, y, fields, outputs) {
        this.id = id;
        this.name = name;
        this.moduleKey = moduleKey;
        this.calcKey = calcKey;
        this.x = x;
        this.y = y;
        this.width = 220;
        this.height = 100;
        this.fields = fields || [];
        this.outputDefs = outputs || [];
        this.inputPorts = this.buildInputPorts(fields);
        this.outputPorts = this.buildOutputPorts(outputs);
        this.inputValues = {};
        this.outputValues = {};
        this.hasError = false;
        this.errorMessage = '';
    }

    buildInputPorts(fields) {
        if (!fields || fields.length === 0) return [];
        return fields.map((field, index) => ({
            name: field.name,
            label: field.label || field.name,
            type: field.type || 'number',
            index: index
        }));
    }

    buildOutputPorts(outputs) {
        if (!outputs || outputs.length === 0) {
            return [{ name: 'result', label: 'Result', type: 'object', index: 0 }];
        }
        return outputs.map((output, index) => ({
            name: output.name || output,
            label: output.label || output.name || output,
            type: output.type || 'number',
            index: index
        }));
    }

    isAt(x, y) {
        return x >= this.x && x <= this.x + this.width && y >= this.y && y <= this.y + this.height;
    }

    getPortAt(x, y) {
        const portRadius = 12;
        
        for (let i = 0; i < this.inputPorts.length; i++) {
            const pos = this.getInputPortPos(i);
            const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
            if (dist < portRadius) {
                return { type: 'input', index: i };
            }
        }
        
        for (let i = 0; i < this.outputPorts.length; i++) {
            const pos = this.getOutputPortPos(i);
            const dist = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
            if (dist < portRadius) {
                return { type: 'output', index: i };
            }
        }
        
        return null;
    }

    getInputPortPos(index) {
        const spacing = this.height / (this.inputPorts.length + 1);
        return { x: this.x, y: this.y + spacing * (index + 1) };
    }

    getOutputPortPos(index) {
        const spacing = this.height / (this.outputPorts.length + 1);
        return { x: this.x + this.width, y: this.y + spacing * (index + 1) };
    }

    draw(ctx, isSelected, connections = []) {
        if (!this.hasError) {
            ctx.shadowColor = 'rgba(0,0,0,0.5)';
            ctx.shadowBlur = 15;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 4;
        }
        
        const gradient = ctx.createLinearGradient(this.x, this.y, this.x, this.y + this.height);
        if (this.hasError) {
            gradient.addColorStop(0, 'rgba(239,68,68,0.3)');
            gradient.addColorStop(1, 'rgba(239,68,68,0.1)');
        } else {
            gradient.addColorStop(0, 'rgba(30,41,59,0.98)');
            gradient.addColorStop(1, 'rgba(15,23,42,0.98)');
        }
        
        ctx.fillStyle = gradient;
        ctx.strokeStyle = isSelected ? '#3b82f6' : (this.hasError ? '#ef4444' : '#475569');
        ctx.lineWidth = isSelected ? 3 : 2;
        ctx.beginPath();
        ctx.roundRect(this.x, this.y, this.width, this.height, 8);
        ctx.fill();
        ctx.stroke();
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        if (isSelected) {
            ctx.strokeStyle = 'rgba(59,130,246,0.3)';
            ctx.lineWidth = 6;
            ctx.stroke();
        }
        
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 13px Inter, system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(this.name, this.x + this.width / 2, this.y + 12);
        
        const module = Calculators.modules[this.moduleKey];
        if (module) {
            ctx.fillStyle = '#94a3b8';
            ctx.font = '10px Inter, system-ui, sans-serif';
            ctx.fillText(`${module.icon} ${module.name}`, this.x + this.width / 2, this.y + 30);
        }
        
        this.inputPorts.forEach((port, i) => {
            const pos = this.getInputPortPos(i);
            const isConnected = connections.some(c => c.toNode === this && c.toPort === i);
            
            ctx.fillStyle = isConnected ? 'rgba(59,130,246,0.4)' : 'rgba(59,130,246,0.2)';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, isConnected ? 9 : 8, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = isConnected ? '#60a5fa' : '#3b82f6';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, isConnected ? 6 : 5, 0, Math.PI * 2);
            ctx.fill();
            
            if (isConnected) {
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
            
            ctx.fillStyle = isConnected ? '#e0f2fe' : '#cbd5e1';
            ctx.font = isConnected ? 'bold 9px Inter, system-ui, sans-serif' : '9px Inter, system-ui, sans-serif';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(port.label, pos.x + 14, pos.y);
        });
        
        this.outputPorts.forEach((port, i) => {
            const pos = this.getOutputPortPos(i);
            const connectionCount = connections.filter(c => c.fromNode === this && c.fromPort === i).length;
            
            ctx.fillStyle = connectionCount > 0 ? 'rgba(16,185,129,0.4)' : 'rgba(16,185,129,0.2)';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, connectionCount > 0 ? 9 : 8, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = connectionCount > 0 ? '#34d399' : '#10b981';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, connectionCount > 0 ? 6 : 5, 0, Math.PI * 2);
            ctx.fill();
            
            if (connectionCount > 1) {
                ctx.fillStyle = '#059669';
                ctx.beginPath();
                ctx.arc(pos.x + 6, pos.y - 6, 7, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 8px Inter, system-ui, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(connectionCount.toString(), pos.x + 6, pos.y - 6);
            }
            
            ctx.fillStyle = connectionCount > 0 ? '#d1fae5' : '#cbd5e1';
            ctx.font = connectionCount > 0 ? 'bold 9px Inter, system-ui, sans-serif' : '9px Inter, system-ui, sans-serif';
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            ctx.fillText(port.label, pos.x - 14, pos.y);
        });
        
        if (Object.keys(this.outputValues).length > 0 && !this.hasError) {
            ctx.fillStyle = '#10b981';
            ctx.beginPath();
            ctx.arc(this.x + this.width - 12, this.y + 12, 5, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = 'rgba(16,185,129,0.3)';
            ctx.beginPath();
            ctx.arc(this.x + this.width - 12, this.y + 12, 8, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    getPropertiesHTML() {
        let html = `
            <div class="node-properties">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(59,130,246,0.3);">
                    <h3 style="font-size: 1.1rem; margin: 0; color: #f8fafc;">${this.name}</h3>
                    <button onclick="VisualWorkflow.renameNode(VisualWorkflow.nodes.find(n=>n.id===${this.id}))"
                            style="padding: 0.4rem 0.8rem; background: rgba(59,130,246,0.2); border: 1px solid rgba(59,130,246,0.4); border-radius: 6px; color: #60a5fa; cursor: pointer; font-weight: 600; font-size: 0.8rem; transition: all 0.2s;"
                            onmouseover="this.style.background='rgba(59,130,246,0.3)';"
                            onmouseout="this.style.background='rgba(59,130,246,0.2)';"
                            title="Rename this node">
                        ✏️ Rename
                    </button>
                </div>
                
                <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 1rem;">${this.moduleKey}/${this.calcKey}</div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.75rem;">Inputs</h4>
        `;
        
        this.inputPorts.forEach((port, i) => {
            const field = this.fields[i];
            const value = this.inputValues[port.name] || '';
            
            html += `
                <div style="margin-bottom: 0.75rem;">
                    <label style="display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.25rem;">${port.label}</label>
                    ${field && field.type === 'select' && field.options ? `
                        <select onchange="VisualWorkflow.onPropChange(${this.id}, '${port.name}', this.value)"
                                class="select-input" style="width: 100%;">
                            ${field.options.map(opt => `
                                <option value="${opt.value}" ${value === opt.value ? 'selected' : ''}>${opt.label}</option>
                            `).join('')}
                        </select>
                    ` : `
                        <input type="${field?.type || 'number'}"
                               value="${value}"
                               onchange="VisualWorkflow.onPropChange(${this.id}, '${port.name}', this.value)"
                               class="text-input" style="width: 100%;"
                               placeholder="Enter ${port.label}">
                    `}
                </div>
            `;
        });
        
        html += `
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.75rem;">📡 Data Flow</h4>
        `;
        
        const incomingConns = VisualWorkflow.connections.filter(c => c.toNode === this);
        if (incomingConns.length > 0) {
            html += `
                <div style="background: rgba(34,197,94,0.1); border-left: 3px solid #22c55e; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.75rem;">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #22c55e; margin-bottom: 0.5rem;">📥 Incoming (${incomingConns.length})</div>
                    ${incomingConns.map(conn => {
                        const fromPort = conn.fromNode.outputPorts[conn.fromPort];
                        const toPort = this.inputPorts[conn.toPort];
                        return `
                            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.25rem;">
                                ${conn.fromNode.name}.${fromPort.label} → <strong>${toPort.label}</strong>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }
        
        const outgoingConns = VisualWorkflow.connections.filter(c => c.fromNode === this);
        if (outgoingConns.length > 0) {
            html += `
                <div style="background: rgba(59,130,246,0.1); border-left: 3px solid #3b82f6; padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #60a5fa; margin-bottom: 0.5rem;">📤 Outgoing (${outgoingConns.length})</div>
                    ${outgoingConns.map(conn => {
                        const fromPort = this.outputPorts[conn.fromPort];
                        const toPort = conn.toNode.inputPorts[conn.toPort];
                        return `
                            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.25rem;">
                                <strong>${fromPort.label}</strong> → ${conn.toNode.name}.${toPort.label}
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }
        
        if (incomingConns.length === 0 && outgoingConns.length === 0) {
            html += `
                <div style="font-size: 0.85rem; color: #64748b; text-align: center; padding: 1rem; background: rgba(100,116,139,0.1); border-radius: 6px;">
                    No connections yet
                </div>
            `;
        }
        
        html += `
                </div>
        `;
        
        if (Object.keys(this.outputValues).length > 0) {
            html += `
                <div>
                    <h4 style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.75rem;">Results</h4>
                    <div class="glass" style="padding: 1rem; border-radius: 8px;">
                        ${Object.entries(this.outputValues).map(([key, value]) => `
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: #cbd5e1; font-size: 0.85rem;">${key}:</span>
                                <span style="color: #f8fafc; font-weight: 600; font-size: 0.85rem;">${value}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        if (this.hasError) {
            html += `
                <div style="background: rgba(239,68,68,0.2); border: 1px solid #ef4444; padding: 0.75rem; border-radius: 6px; margin-top: 1rem;">
                    <div style="color: #fca5a5; font-size: 0.85rem;">❌ ${this.errorMessage}</div>
                </div>
            `;
        }
        
        html += `
            </div>
        `;
        
        return html;
    }

    async execute(inputs) {
        try {
            this.hasError = false;
            this.errorMessage = '';
            
            const module = Calculators.modules[this.moduleKey];
            if (!module) {
                throw new Error(`Module ${this.moduleKey} not found`);
            }
            
            const calculator = module.calculators[this.calcKey];
            if (!calculator) {
                throw new Error(`Calculator ${this.calcKey} not available`);
            }
            
            const calcFunction = window[calculator.key];
            if (typeof calcFunction !== 'function') {
                throw new Error(`Calculator function ${calculator.key} not found`);
            }
            
            const result = await calcFunction(inputs);
            this.outputValues = result || {};
            return result;
            
        } catch (error) {
            this.hasError = true;
            this.errorMessage = error.message;
            throw error;
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📋 Visual Workflow Engine initialized');
    });
}
