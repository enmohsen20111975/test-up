/**
 * Learning Platform State Management - Enhanced Version
 * Handles course progress, user preferences, bookmarks, notes, quiz results
 * Uses localStorage for persistence with event-driven architecture
 */

const LearningState = (function () {
    // Storage keys - separate keys for better organization
    const STORAGE_KEYS = {
        PROGRESS: 'ee_learning_progress',
        BOOKMARKS: 'ee_learning_bookmarks',
        NOTES: 'ee_learning_notes',
        PREFERENCES: 'ee_learning_preferences',
        QUIZ_RESULTS: 'ee_learning_quiz_results'
    };

    // Course data structure - comprehensive lesson mapping
    const courseData = {
        chapters: [
            {
                id: '01-fundamentals',
                title: 'Fundamentals of Electricity',
                lessons: [
                    { id: '01-atomic-structure', title: 'Atomic Structure and Electric Charge', duration: '90 min' },
                    { id: '02-voltage-current-resistance', title: 'Voltage, Current, and Resistance Defined', duration: '75 min' },
                    { id: '03-ohms-law-power', title: 'Ohm\'s Law and Power Calculations', duration: '120 min' },
                    { id: '04-series-circuits', title: 'Series Circuit Analysis', duration: '100 min' },
                    { id: '05-parallel-circuits', title: 'Parallel Circuit Analysis', duration: '100 min' },
                    { id: '06-series-parallel-circuits', title: 'Series-Parallel Circuit Combinations', duration: '120 min' },
                    { id: '07-circuit-theorems', title: 'Circuit Theorems (Thevenin, Norton, Superposition)', duration: '150 min' },
                    { id: '08-conductors-insulators', title: 'Conductors, Insulators, and Semiconductors', duration: '90 min' },
                    { id: '09-measurement-instruments', title: 'Electrical Measurement Instruments', duration: '100 min' },
                    { id: '10-troubleshooting', title: 'Circuit Troubleshooting Fundamentals', duration: '90 min' }
                ]
            },
            {
                id: '02-circuit-analysis',
                title: 'DC Circuits Analysis',
                lessons: [
                    { id: '01-introduction-dc', title: 'Introduction to DC Circuit Analysis', duration: '60 min' },
                    { id: '02-kirchhoffs-current-law', title: 'Kirchhoff\'s Current Law (KCL)', duration: '90 min' },
                    { id: '03-kirchhoffs-voltage-law', title: 'Kirchhoff\'s Voltage Law (KVL)', duration: '90 min' },
                    { id: '04-mesh-analysis', title: 'Mesh Analysis Technique', duration: '120 min' },
                    { id: '05-nodal-analysis', title: 'Nodal Analysis Technique', duration: '120 min' },
                    { id: '06-source-transformation', title: 'Source Transformation Method', duration: '90 min' },
                    { id: '07-thevenin-norton', title: 'Thevenin and Norton Equivalents', duration: '120 min' },
                    { id: '08-superposition', title: 'Superposition Theorem', duration: '100 min' },
                    { id: '09-maximum-power-transfer', title: 'Maximum Power Transfer Theorem', duration: '75 min' },
                    { id: '10-dependent-sources', title: 'Circuits with Dependent Sources', duration: '120 min' }
                ]
            },
            {
                id: '03-power-systems',
                title: 'AC Circuits & Phasors',
                lessons: [
                    { id: '01-ac-fundamentals', title: 'AC Circuit Fundamentals and Sinusoidal Waveforms', duration: '90 min' },
                    { id: '02-phasors', title: 'Phasor Representation and Complex Numbers', duration: '120 min' },
                    { id: '03-ac-power', title: 'AC Power Calculations (Real, Reactive, Apparent)', duration: '120 min' },
                    { id: '04-power-factor', title: 'Power Factor and Power Factor Correction', duration: '100 min' },
                    { id: '05-resonance', title: 'Series and Parallel Resonance', duration: '100 min' },
                    { id: '06-filters', title: 'Passive Filters (Low-pass, High-pass, Band-pass)', duration: '120 min' },
                    { id: '07-transformers', title: 'Transformer Theory and Applications', duration: '120 min' },
                    { id: '08-three-phase', title: 'Three-Phase Systems Fundamentals', duration: '150 min' }
                ]
            },
            {
                id: '04-electronics',
                title: 'Power Systems',
                lessons: [
                    { id: '01-power-generation', title: 'Electrical Power Generation Methods', duration: '120 min' },
                    { id: '02-transmission-systems', title: 'Power Transmission Systems and Grid', duration: '120 min' },
                    { id: '03-distribution-systems', title: 'Power Distribution Systems', duration: '100 min' },
                    { id: '04-protection-devices', title: 'Protection Devices and Circuit Breakers', duration: '100 min' },
                    { id: '05-fault-analysis', title: 'Fault Analysis and Short Circuits', duration: '120 min' },
                    { id: '06-substations', title: 'Substation Design and Equipment', duration: '100 min' },
                    { id: '07-tariffs-metering', title: 'Electrical Tariffs and Smart Metering', duration: '75 min' }
                ]
            },
            {
                id: '05-digital-electronics',
                title: 'Electronics & Semiconductors',
                lessons: [
                    { id: '01-semiconductor-physics', title: 'Semiconductor Physics and Doping', duration: '120 min' },
                    { id: '02-diodes', title: 'P-N Junction Diodes and Applications', duration: '120 min' },
                    { id: '03-rectifiers', title: 'Rectifier Circuits (Half-wave, Full-wave, Bridge)', duration: '120 min' },
                    { id: '04-bjt-transistors', title: 'Bipolar Junction Transistors (BJT)', duration: '150 min' },
                    { id: '05-mosfet-transistors', title: 'MOSFETs and CMOS Technology', duration: '150 min' },
                    { id: '06-amplifiers', title: 'Amplifier Circuits and Biasing', duration: '150 min' },
                    { id: '07-operational-amplifiers', title: 'Operational Amplifiers (Op-Amps)', duration: '150 min' },
                    { id: '08-op-amp-applications', title: 'Op-Amp Applications (Comparator, Filter, Oscillator)', duration: '120 min' },
                    { id: '09-power-electronics', title: 'Power Electronics Basics (Switching, SMPS)', duration: '120 min' },
                    { id: '10-ic-fabrication', title: 'Integrated Circuit Fundamentals', duration: '90 min' }
                ]
            },
            {
                id: '06-electrical-machines',
                title: 'Digital Electronics',
                lessons: [
                    { id: '01-binary-systems', title: 'Number Systems (Binary, Hex, Decimal)', duration: '90 min' },
                    { id: '02-boolean-algebra', title: 'Boolean Algebra and Logic Gates', duration: '120 min' },
                    { id: '03-combinational-logic', title: 'Combinational Logic Circuits', duration: '120 min' },
                    { id: '04-sequential-logic', title: 'Sequential Logic and Flip-Flops', duration: '120 min' },
                    { id: '05-counters-registers', title: 'Counters and Shift Registers', duration: '120 min' },
                    { id: '06-decoders-encoders', title: 'Decoders, Encoders, and Multiplexers', duration: '100 min' },
                    { id: '07-arithmetic-circuits', title: 'Arithmetic Circuits (Adders, Subtractors)', duration: '100 min' },
                    { id: '08-memory-systems', title: 'Memory Systems and Storage', duration: '120 min' },
                    { id: '09-microcontrollers', title: 'Introduction to Microcontrollers', duration: '120 min' },
                    { id: '10-fpga-cpld', title: 'FPGA and CPLD Fundamentals', duration: '100 min' }
                ]
            },
            {
                id: '07-control-systems',
                title: 'Electrical Machines',
                lessons: [
                    { id: '01-magnetic-circuits', title: 'Magnetic Circuits and Transformers', duration: '120 min' },
                    { id: '02-transformer-types', title: 'Transformer Types and Applications', duration: '100 min' },
                    { id: '03-dc-motors', title: 'DC Motors: Construction and Operation', duration: '150 min' },
                    { id: '04-dc-motor-control', title: 'DC Motor Speed and Torque Control', duration: '120 min' },
                    { id: '05-ac-motors', title: 'AC Motors: Induction and Synchronous', duration: '180 min' },
                    { id: '06-ac-motor-control', title: 'AC Motor Control Methods (VFD, Soft Starters)', duration: '150 min' },
                    { id: '07-generators', title: 'DC and AC Generators', duration: '150 min' },
                    { id: '08-special-machines', title: 'Special Machines (Stepper, Servo, BLDC)', duration: '120 min' },
                    { id: '09-motor-selection', title: 'Motor Selection and Sizing', duration: '100 min' },
                    { id: '10-machine-protection', title: 'Electrical Machine Protection', duration: '90 min' }
                ]
            },
            {
                id: '08-renewable-energy',
                title: 'Control Systems',
                lessons: [
                    { id: '01-control-systems-intro', title: 'Introduction to Control Systems', duration: '90 min' },
                    { id: '02-transfer-functions', title: 'Transfer Functions and Block Diagrams', duration: '120 min' },
                    { id: '03-time-response', title: 'Time Response of First and Second Order Systems', duration: '120 min' },
                    { id: '04-stability-analysis', title: 'Stability Analysis (Routh-Hurwitz, Bode)', duration: '150 min' },
                    { id: '05-pid-controllers', title: 'PID Controllers and Tuning', duration: '150 min' },
                    { id: '06-state-space', title: 'State-Space Analysis', duration: '120 min' },
                    { id: '07-compensator-design', title: 'Compensator Design (Lead, Lag, Lead-Lag)', duration: '120 min' },
                    { id: '08-digital-control', title: 'Digital Control Systems', duration: '120 min' }
                ]
            },
            {
                id: '09-safety-standards',
                title: 'Renewable Energy',
                lessons: [
                    { id: '01-solar-energy', title: 'Solar Photovoltaic Systems', duration: '150 min' },
                    { id: '02-wind-energy', title: 'Wind Energy Conversion Systems', duration: '150 min' },
                    { id: '03-hydropower', title: 'Hydropower and Tidal Energy', duration: '120 min' },
                    { id: '04-other-renewables', title: 'Other Renewable Energy Sources', duration: '100 min' },
                    { id: '05-hybrid-systems', title: 'Hybrid Renewable Energy Systems', duration: '120 min' },
                    { id: '06-grid-integration', title: 'Renewable Energy Grid Integration', duration: '120 min' },
                    { id: '07-energy-storage', title: 'Energy Storage Systems (Batteries, Supercapacitors)', duration: '120 min' },
                    { id: '08-future-trends', title: 'Future Energy Trends and Technologies', duration: '90 min' }
                ]
            },
            {
                id: '10-safety-standards',
                title: 'Safety & Standards',
                lessons: [
                    { id: '01-electrical-safety', title: 'Electrical Safety Fundamentals', duration: '120 min' },
                    { id: '02-personal-protection', title: 'Personal Protective Equipment (PPE)', duration: '90 min' },
                    { id: '03-arc-flash', title: 'Arc Flash and Arc Blast Hazards', duration: '100 min' },
                    { id: '04-electrical-codes', title: 'National Electrical Code (NEC) Overview', duration: '120 min' },
                    { id: '05-ieee-standards', title: 'IEEE and IEC Standards', duration: '100 min' },
                    { id: '06-lockout-tagout', title: 'Lockout/Tagout Procedures', duration: '90 min' },
                    { id: '07-emergency-procedures', title: 'Emergency Response Procedures', duration: '75 min' },
                    { id: '08-grounding-bonding', title: 'Grounding and Bonding Systems', duration: '100 min' }
                ]
            }
        ]
    };

    // Internal state
    let listeners = [];

    // Initialize state from localStorage or defaults
    function initialize() {
        if (!localStorage.getItem(STORAGE_KEYS.PROGRESS)) {
            localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify({}));
        }
        if (!localStorage.getItem(STORAGE_KEYS.BOOKMARKS)) {
            localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify([]));
        }
        if (!localStorage.getItem(STORAGE_KEYS.NOTES)) {
            localStorage.setItem(STORAGE_KEYS.NOTES, JSON.stringify({}));
        }
        if (!localStorage.getItem(STORAGE_KEYS.PREFERENCES)) {
            localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify({
                theme: 'dark',
                fontSize: 'medium',
                animations: true,
                autoplay: true
            }));
        }
    }

    // Event system
    function emit(event, data) {
        listeners.forEach(callback => callback(event, data));
    }

    function on(callback) {
        listeners.push(callback);
    }

    // Progress management
    const progress = {
        getAll: function () {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.PROGRESS) || '{}');
        },

        getLessonProgress: function (chapterId, lessonId) {
            const all = this.getAll();
            return all[`${chapterId}/${lessonId}`] || {
                completed: false,
                timeSpent: 0,
                lastAccessed: null,
                quizScore: null
            };
        },

        markLessonComplete: function (chapterId, lessonId) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            all[key] = all[key] || {};
            all[key].completed = true;
            all[key].lastAccessed = new Date().toISOString();
            localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(all));
            emit('progress', { type: 'lesson_complete', key });
        },

        updateTimeSpent: function (chapterId, lessonId, seconds) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            all[key] = all[key] || {};
            all[key].timeSpent = (all[key].timeSpent || 0) + seconds;
            all[key].lastAccessed = new Date().toISOString();
            localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(all));
        },

        saveQuizScore: function (chapterId, lessonId, score) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            all[key] = all[key] || {};
            all[key].quizScore = score;
            all[key].lastAccessed = new Date().toISOString();
            localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(all));
            emit('quiz', { type: 'score_saved', key });
        },

        getOverallProgress: function () {
            const all = this.getAll();
            const lessons = courseData.chapters.reduce((acc, ch) => {
                return acc.concat(ch.lessons.map(l => `${ch.id}/${l.id}`));
            }, []);

            const completed = lessons.filter(l => all[l] && all[l].completed).length;
            return {
                completed,
                total: lessons.length,
                percentage: Math.round((completed / lessons.length) * 100)
            };
        },

        getChapterProgress: function (chapterId) {
            const chapter = courseData.chapters.find(c => c.id === chapterId);
            if (!chapter) return null;

            const all = this.getAll();
            const completed = chapter.lessons.filter(l =>
                all[`${chapterId}/${l.id}`] && all[`${chapterId}/${l.id}`].completed
            ).length;

            return {
                chapterId,
                chapterTitle: chapter.title,
                completed,
                total: chapter.lessons.length,
                percentage: Math.round((completed / chapter.lessons.length) * 100)
            };
        },

        resetProgress: function () {
            localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify({}));
            emit('reset', {});
        }
    };

    // Bookmark management
    const bookmarks = {
        getAll: function () {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.BOOKMARKS) || '[]');
        },

        add: function (chapterId, lessonId, sectionId, title) {
            const all = this.getAll();
            const newBookmark = {
                id: Date.now(),
                chapterId,
                lessonId,
                sectionId,
                title,
                createdAt: new Date().toISOString()
            };
            all.push(newBookmark);
            localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(all));
            emit('bookmark', { type: 'added', bookmark: newBookmark });
            return newBookmark;
        },

        remove: function (bookmarkId) {
            const all = this.getAll();
            const filtered = all.filter(b => b.id !== bookmarkId);
            localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(filtered));
            emit('bookmark', { type: 'removed', id: bookmarkId });
        },

        getForLesson: function (chapterId, lessonId) {
            const all = this.getAll();
            return all.filter(b => b.chapterId === chapterId && b.lessonId === lessonId);
        },

        clear: function () {
            localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify([]));
            emit('bookmark', { type: 'cleared' });
        }
    };

    // Notes management
    const notes = {
        getAll: function () {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.NOTES) || '{}');
        },

        getForLesson: function (chapterId, lessonId) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            return all[key] || [];
        },

        add: function (chapterId, lessonId, sectionId, content) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            all[key] = all[key] || [];

            const newNote = {
                id: Date.now(),
                sectionId,
                content,
                createdAt: new Date().toISOString()
            };

            all[key].push(newNote);
            localStorage.setItem(STORAGE_KEYS.NOTES, JSON.stringify(all));
            emit('note', { type: 'added', note: newNote });
            return newNote;
        },

        update: function (chapterId, lessonId, noteId, content) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            if (all[key]) {
                const note = all[key].find(n => n.id === noteId);
                if (note) {
                    note.content = content;
                    note.updatedAt = new Date().toISOString();
                    localStorage.setItem(STORAGE_KEYS.NOTES, JSON.stringify(all));
                    emit('note', { type: 'updated', note });
                }
            }
        },

        delete: function (chapterId, lessonId, noteId) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            if (all[key]) {
                all[key] = all[key].filter(n => n.id !== noteId);
                localStorage.setItem(STORAGE_KEYS.NOTES, JSON.stringify(all));
                emit('note', { type: 'deleted', noteId });
            }
        }
    };

    // Preferences management
    const preferences = {
        get: function () {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.PREFERENCES) || '{}');
        },

        set: function (newPrefs) {
            const current = this.get();
            const updated = { ...current, ...newPrefs };
            localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(updated));
            emit('preferences', { updated });
        },

        toggleAnimations: function () {
            const current = this.get();
            current.animations = !current.animations;
            this.set(current);
            return current.animations;
        }
    };

    // Quiz results management
    const quizResults = {
        getAll: function () {
            return JSON.parse(localStorage.getItem(STORAGE_KEYS.QUIZ_RESULTS) || '{}');
        },

        saveResult: function (chapterId, lessonId, answers, score, totalQuestions) {
            const all = this.getAll();
            const key = `${chapterId}/${lessonId}`;
            all[key] = {
                answers,
                score,
                totalQuestions,
                percentage: Math.round((score / totalQuestions) * 100),
                completedAt: new Date().toISOString()
            };
            localStorage.setItem(STORAGE_KEYS.QUIZ_RESULTS, JSON.stringify(all));
            emit('quiz', { type: 'result_saved', key });
        },

        getResult: function (chapterId, lessonId) {
            const all = this.getAll();
            return all[`${chapterId}/${lessonId}`] || null;
        }
    };

    // Initialize on load
    initialize();

    // Public API
    return {
        courseData,
        progress,
        bookmarks,
        notes,
        preferences,
        quizResults,
        STORAGE_KEYS,
        on,
        emit
    };
})();

/**
 * Load state from localStorage
 */
function load() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            state = { ...state, ...JSON.parse(saved) };
        }
    } catch (e) {
        console.warn('Failed to load state:', e);
    }
    return state;
}

/**
 * Save state to localStorage
 */
function save() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
        console.warn('Failed to save state:', e);
    }
}

/**
 * Get state value
 */
function get(path) {
    const keys = path.split('.');
    let value = state;
    for (const key of keys) {
        if (value === undefined) return undefined;
        value = value[key];
    }
    return value;
}

/**
 * Set state value
 */
function set(path, value) {
    const keys = path.split('.');
    let obj = state;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!obj[keys[i]]) obj[keys[i]] = {};
        obj = obj[keys[i]];
    }
    obj[keys[keys.length - 1]] = value;
    save();
}

/**
 * Mark lesson as completed
 */
function completeLesson(lessonId) {
    if (!state.progress.completedLessons.includes(lessonId)) {
        state.progress.completedLessons.push(lessonId);
        calculateTotalProgress();
        save();
        emit('lessonCompleted', { lessonId });
    }
}

/**
 * Check if lesson is completed
 */
function isLessonCompleted(lessonId) {
    return state.progress.completedLessons.includes(lessonId);
}

/**
 * Calculate total progress percentage
 */
function calculateTotalProgress() {
    // This will be updated when course data is loaded
    const total = getTotalLessons();
    if (total > 0) {
        state.progress.totalProgress = Math.round(
            (state.progress.completedLessons.length / total) * 100
        );
    }
}

/**
 * Set total lessons count
 */
let totalLessons = 0;
function setTotalLessons(count) {
    totalLessons = count;
    calculateTotalProgress();
}

function getTotalLessons() {
    return totalLessons;
}

/**
 * Add bookmark
 */
function addBookmark(lessonId, title) {
    if (!state.bookmarks.find(b => b.lessonId === lessonId)) {
        state.bookmarks.push({ lessonId, title, addedAt: Date.now() });
        save();
        emit('bookmarkAdded', { lessonId });
    }
}

/**
 * Remove bookmark
 */
function removeBookmark(lessonId) {
    state.bookmarks = state.bookmarks.filter(b => b.lessonId !== lessonId);
    save();
    emit('bookmarkRemoved', { lessonId });
}

/**
 * Get bookmarks
 */
function getBookmarks() {
    return state.bookmarks;
}

/**
 * Add note
 */
function addNote(lessonId, content) {
    if (!state.notes[lessonId]) {
        state.notes[lessonId] = [];
    }
    state.notes[lessonId].push({
        content,
        createdAt: Date.now()
    });
    save();
    emit('noteAdded', { lessonId });
}

/**
 * Get notes for lesson
 */
function getNotes(lessonId) {
    return state.notes[lessonId] || [];
}

/**
 * Update preferences
 */
function updatePreference(key, value) {
    state.preferences[key] = value;
    applyPreference(key, value);
    save();
}

/**
 * Apply preference
 */
function applyPreference(key, value) {
    switch (key) {
        case 'theme':
            document.body.classList.toggle('dark', value === 'dark');
            break;
        case 'fontSize':
            document.body.style.fontSize = {
                small: '14px',
                medium: '16px',
                large: '18px'
            }[value] || '16px';
            break;
    }
}

/**
 * Event system
 */
const listeners = new Map();
function emit(event, data) {
    if (listeners.has(event)) {
        listeners.get(event).forEach(callback => callback(data));
    }
}

function on(event, callback) {
    if (!listeners.has(event)) {
        listeners.set(event, []);
    }
    listeners.get(event).push(callback);
}

/**
 * Initialize state
 */
function init() {
    load();
    applyAllPreferences();
}

function applyAllPreferences() {
    Object.entries(state.preferences).forEach(([key, value]) => {
        applyPreference(key, value);
    });
}

// Legacy API compatibility
const State = (function () {
    function load() { return {}; }
    function save() { }
    function get() { return null; }
    function set() { }

    function completeLesson(lessonId) {
        const parts = lessonId.split('/');
        const chapterId = parts[0];
        const lessonNum = parts[1];
        const lessonIdFull = parts.slice(1).join('/');
        LearningState.progress.markLessonComplete(chapterId, lessonIdFull);
    }

    function isLessonCompleted(lessonId) {
        const parts = lessonId.split('/');
        if (parts.length === 2) {
            const progress = LearningState.progress.getLessonProgress(parts[0], parts[1]);
            return progress.completed;
        }
        return false;
    }

    function setTotalLessons(count) { }
    function getTotalLessons() { return 76; }

    function addBookmark(lessonId, title) {
        LearningState.bookmarks.add('01-fundamentals', lessonId, null, title);
    }

    function removeBookmark(lessonId) {
        const bookmarks = LearningState.bookmarks.getAll();
        const bm = bookmarks.find(b => b.lessonId === lessonId);
        if (bm) LearningState.bookmarks.remove(bm.id);
    }

    function getBookmarks() {
        return LearningState.bookmarks.getAll();
    }

    function addNote(lessonId, content) {
        LearningState.notes.add('01-fundamentals', lessonId, null, content);
    }

    function getNotes(lessonId) {
        return LearningState.notes.getForLesson('01-fundamentals', lessonId);
    }

    function updatePreference(key, value) {
        LearningState.preferences.set({ [key]: value });
    }

    function on(event, callback) {
        LearningState.on(callback);
    }

    return {
        init: () => { },
        get,
        set,
        completeLesson,
        isLessonCompleted,
        setTotalLessons,
        getTotalLessons,
        addBookmark,
        removeBookmark,
        getBookmarks,
        addNote,
        getNotes,
        updatePreference,
        on
    };
})();

// Export both
window.LearningState = LearningState;
window.State = State;