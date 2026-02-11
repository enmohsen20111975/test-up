// Analytics Service - Data Analysis and Query Building
class AnalyticsService {
    constructor() {
        this.baseUrl = 'http://localhost:8000'; // Set the base URL for the backend
        this.authService = authService;
    }

    async processFile(fileContent, filename, sheetName = null) {
        try {
            const formData = new FormData();
            const blob = new Blob([fileContent], { type: 'application/octet-stream' });
            formData.append('file', blob, filename);
            if (sheetName) {
                formData.append('sheet_name', sheetName);
            }
            
            const response = await fetch(`${this.baseUrl}/analytics/upload`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'File processing failed');
            }

            return await response.json();
        } catch (error) {
            console.error('File processing error:', error);
            return { success: false, error: error.message };
        }
    }

    async getExcelSheets(fileContent, filename) {
        try {
            const formData = new FormData();
            const blob = new Blob([fileContent], { type: 'application/octet-stream' });
            formData.append('file', blob, filename);
            
            const response = await fetch(`${this.baseUrl}/analytics/excel-sheets`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get Excel sheets');
            }

            return await response.json();
        } catch (error) {
            console.error('Excel sheets error:', error);
            return { success: false, error: error.message };
        }
    }

    async processDatabaseConnection(connectionParams) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/database-connect`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify(connectionParams)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Database connection failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Database connection error:', error);
            return { success: false, error: error.message };
        }
    }

    async fetchDatabaseTableData(connectionParams, tableName) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/database-table-data`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify({ connection_params: connectionParams, table_name: tableName })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Failed to fetch data from table ${tableName}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Error fetching table data for ${tableName}:`, error);
            return { success: false, error: error.message };
        }
    }

    async executeQuery(data, query) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/query`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify({
                    data: data,
                    query: query
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Query execution failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Query execution error:', error);
            throw error;
        }
    }

    async getDataSummary(data) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/summary`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify({
                    data: data
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Data summary failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Data summary error:', error);
            throw error;
        }
    }

    async getColumnDistribution(data, column, bins = 10) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/distribution`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify({
                    data: data,
                    column: column,
                    bins: bins
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Column distribution failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Column distribution error:', error);
            throw error;
        }
    }

    async getAnalyticsTemplates() {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/templates`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${this.authService.getToken()}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get templates');
            }

            return await response.json();
        } catch (error) {
            console.error('Templates error:', error);
            throw error;
        }
    }

    async generateReport(content) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/generate-report`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify(content)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Report generation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Report generation error:', error);
            throw error;
        }
    }

    async analyzeDataWithAI(data, analysisType, parameters) {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/ai-analyze`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authService.getToken()}`
                },
                body: JSON.stringify({
                    data: data,
                    analysis_type: analysisType,
                    parameters: parameters
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'AI analysis failed');
            }

            return await response.json();
        } catch (error) {
            console.error('AI analysis error:', error);
            return { success: false, error: error.message };
        }
    }
}

// SQL Functions Library - Comprehensive function library for query building
const SQL_FUNCTIONS = {
    aggregate: [
        { name: 'SUM', syntax: 'SUM(column)', desc: 'Sum of values' },
        { name: 'AVG', syntax: 'AVG(column)', desc: 'Average of values' },
        { name: 'COUNT', syntax: 'COUNT(column)', desc: 'Count of rows' },
        { name: 'MIN', syntax: 'MIN(column)', desc: 'Minimum value' },
        { name: 'MAX', syntax: 'MAX(column)', desc: 'Maximum value' },
        { name: 'COUNT_DISTINCT', syntax: 'COUNT(DISTINCT column)', desc: 'Count distinct values' }
    ],
    string: [
        { name: 'UPPER', syntax: 'UPPER(column)', desc: 'Convert to uppercase' },
        { name: 'LOWER', syntax: 'LOWER(column)', desc: 'Convert to lowercase' },
        { name: 'TRIM', syntax: 'TRIM(column)', desc: 'Remove whitespace' },
        { name: 'LENGTH', syntax: 'LENGTH(column)', desc: 'String length' },
        { name: 'SUBSTRING', syntax: 'SUBSTRING(column, start, length)', desc: 'Extract substring' },
        { name: 'CONCAT', syntax: 'CONCAT(col1, col2)', desc: 'Concatenate strings' },
        { name: 'REPLACE', syntax: 'REPLACE(column, find, replace)', desc: 'Replace text' }
    ],
    date: [
        { name: 'YEAR', syntax: 'YEAR(date)', desc: 'Extract year' },
        { name: 'MONTH', syntax: 'MONTH(date)', desc: 'Extract month' },
        { name: 'DAY', syntax: 'DAY(date)', desc: 'Extract day' },
        { name: 'NOW', syntax: 'NOW()', desc: 'Current date/time' },
        { name: 'DATEDIFF', syntax: 'DATEDIFF(date1, date2)', desc: 'Difference in days' },
        { name: 'DATE_FORMAT', syntax: 'DATE_FORMAT(date, format)', desc: 'Format date' }
    ],
    math: [
        { name: 'ROUND', syntax: 'ROUND(number, decimals)', desc: 'Round number' },
        { name: 'CEIL', syntax: 'CEIL(number)', desc: 'Round up' },
        { name: 'FLOOR', syntax: 'FLOOR(number)', desc: 'Round down' },
        { name: 'ABS', syntax: 'ABS(number)', desc: 'Absolute value' },
        { name: 'POWER', syntax: 'POWER(base, exponent)', desc: 'Raise to power' },
        { name: 'SQRT', syntax: 'SQRT(number)', desc: 'Square root' }
    ],
    conditional: [
        { name: 'CASE', syntax: 'CASE WHEN condition THEN value END', desc: 'Conditional logic' },
        { name: 'IF', syntax: 'IF(condition, true_value, false_value)', desc: 'If-then-else' },
        { name: 'COALESCE', syntax: 'COALESCE(val1, val2, ...)', desc: 'First non-null value' },
        { name: 'NULLIF', syntax: 'NULLIF(val1, val2)', desc: 'NULL if values equal' }
    ]
};

// Query Builder - Client-side query building and management
class QueryBuilder {
    constructor() {
        this.state = {
            tables: [],
            canvasTables: [],
            joins: [],
            filters: [],
            groupBy: [],
            orderBy: [],
            calculatedFields: [],
            selectedFields: [],
            queryResults: null,
            savedQueries: [],
            draggedTable: null,
            dragOffset: { x: 0, y: 0 },
            isDragging: false,
            joinMode: false,
            joinStart: null,
            favoriteFunctions: [],
            recentFunctions: [],
            functionUsage: {},
            currentFunctionFilter: 'all'
        };
        
        this.loadFunctionPreferences();
    }

    loadFunctionPreferences() {
        const saved = localStorage.getItem('functionPreferences');
        if (saved) {
            const prefs = JSON.parse(saved);
            this.state.favoriteFunctions = prefs.favorites || [];
            this.state.recentFunctions = prefs.recent || [];
            this.state.functionUsage = prefs.usage || {};
        }
    }

    saveFunctionPreferences() {
        localStorage.setItem('functionPreferences', JSON.stringify({
            favorites: this.state.favoriteFunctions,
            recent: this.state.recentFunctions,
            usage: this.state.functionUsage
        }));
    }

    async addTable(tableData) {
        this.state.tables.push(tableData);
        this.state.canvasTables.push(tableData);
    }

    removeTable(tableId) {
        this.state.canvasTables = this.state.canvasTables.filter(table => table.id !== tableId);
    }

    addFilter(column, operator, value) {
        this.state.filters.push({ column, operator, value });
    }

    removeFilter(index) {
        this.state.filters.splice(index, 1);
    }

    addGroupBy(column) {
        if (!this.state.groupBy.includes(column)) {
            this.state.groupBy.push(column);
        }
    }

    removeGroupBy(column) {
        this.state.groupBy = this.state.groupBy.filter(col => col !== column);
    }

    addOrderBy(column, ascending = true) {
        const existing = this.state.orderBy.find(order => order.column === column);
        if (existing) {
            existing.ascending = ascending;
        } else {
            this.state.orderBy.push({ column, ascending });
        }
    }

    removeOrderBy(column) {
        this.state.orderBy = this.state.orderBy.filter(order => order.column !== column);
    }

    addCalculatedField(name, expression) {
        this.state.calculatedFields.push({ name, expression });
    }

    removeCalculatedField(index) {
        this.state.calculatedFields.splice(index, 1);
    }

    addSelectedField(field) {
        if (!this.state.selectedFields.includes(field)) {
            this.state.selectedFields.push(field);
        }
    }

    removeSelectedField(field) {
        this.state.selectedFields = this.state.selectedFields.filter(f => f !== field);
    }

    buildQuery() {
        const query = {
            filters: this.state.filters,
            group_by: this.state.groupBy,
            order_by: this.state.orderBy.map(order => order.column),
            ascending: this.state.orderBy.map(order => order.ascending),
            calculated_fields: this.state.calculatedFields,
            selected_fields: this.state.selectedFields
        };
        
        return query;
    }

    trackFunctionUsage(funcName) {
        this.state.functionUsage[funcName] = (this.state.functionUsage[funcName] || 0) + 1;
        
        // Add to recent functions
        const recentIndex = this.state.recentFunctions.indexOf(funcName);
        if (recentIndex !== -1) {
            this.state.recentFunctions.splice(recentIndex, 1);
        }
        this.state.recentFunctions.unshift(funcName);
        this.state.recentFunctions = this.state.recentFunctions.slice(0, 10);
        
        this.saveFunctionPreferences();
    }

    toggleFavorite(funcName) {
        const index = this.state.favoriteFunctions.indexOf(funcName);
        if (index !== -1) {
            this.state.favoriteFunctions.splice(index, 1);
        } else {
            this.state.favoriteFunctions.push(funcName);
        }
        this.saveFunctionPreferences();
    }

    isFavorite(funcName) {
        return this.state.favoriteFunctions.includes(funcName);
    }

    getRecentFunctions() {
        return this.state.recentFunctions.slice(0, 10);
    }

    getMostUsedFunctions() {
        return Object.entries(this.state.functionUsage)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 15)
            .map(([name, count]) => ({ name, count }));
    }
}

// Initialize analytics service and query builder
export const analyticsService = new AnalyticsService();
export const queryBuilder = new QueryBuilder();
