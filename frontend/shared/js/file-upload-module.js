// frontend/shared/js/file-upload-module.js

import { i18n } from './i18n.js';
import { analyticsService } from './analytics-service.js';

export const fileUploadModule = {
    uploadedFiles: [],
    selectedSheets: {}, // Stores selected sheets per file for Excel
    currentChart: null, // To store the Chart.js instance
    currentAnalysisData: null, // To store data for analysis tab

    init() {
        document.getElementById('fileInput').addEventListener('change', this.handleFileInputChange.bind(this));
        const uploadDropZone = document.getElementById('uploadDropZone');
        uploadDropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadDropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadDropZone.addEventListener('drop', this.handleDrop.bind(this));
        document.getElementById('clearAllFilesBtn').addEventListener('click', this.clearAllFiles.bind(this));
        document.getElementById('processSelectedFilesBtn').addEventListener('click', this.processSelectedFiles.bind(this));
        document.getElementById('selectAllSheetsBtn').addEventListener('click', this.selectAllSheets.bind(this));
        document.getElementById('clearSheetSelectionBtn').addEventListener('click', this.clearSheetSelection.bind(this));
        
        // Chart controls event listeners
        document.getElementById('renderChartBtn').addEventListener('click', this.renderChart.bind(this));
        document.getElementById('chartTypeSelect').addEventListener('change', this.renderChart.bind(this));
        document.getElementById('xAxisSelect').addEventListener('change', this.renderChart.bind(this));
        document.getElementById('yAxisSelect').addEventListener('change', this.renderChart.bind(this));

        // AI Analysis controls event listeners
        document.getElementById('aiAnalysisType').addEventListener('change', this.handleAiAnalysisTypeChange.bind(this));
        document.getElementById('runAiAnalysisBtn').addEventListener('click', this.runAiAnalysis.bind(this));
    },

    handleFileInputChange(e) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            this.addFileToList(file);
        });
    },

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    },

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
    },

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => {
            this.addFileToList(file);
        });
    },

    addFileToList(file) {
        const existingFile = this.uploadedFiles.find(f => f.name === file.name && f.size === file.size);
        if (existingFile) {
            console.warn(`File ${file.name} already added.`);
            return;
        }

        this.uploadedFiles.push(file);
        this.renderFilesList();
    },

    renderFilesList() {
        const fileListContainer = document.getElementById('filesList');
        fileListContainer.innerHTML = ''; // Clear existing list

        if (this.uploadedFiles.length === 0) {
            fileListContainer.innerHTML = `
                <p style="text-align: center; color: #666; padding: 20px;">
                    ${i18n.getTranslation('analytics.upload.noFiles')}
                </p>
            `;
            return;
        }

        this.uploadedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.dataset.index = index;

            const fileIcon = this.getFileIcon(file.name);

            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">${fileIcon}</div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${this.formatFileSize(file.size)} • ${new Date().toLocaleString(i18n.currentLanguage)}</p>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-info" onclick="fileUploadModule.previewFile(${index})">
                        <i class="fas fa-eye"></i> ${i18n.getTranslation('common.preview')}
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="fileUploadModule.removeFile(${index})">
                        <i class="fas fa-trash"></i> ${i18n.getTranslation('common.delete')}
                    </button>
                </div>
            `;
            fileListContainer.appendChild(fileItem);
        });
    },

    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        delete this.selectedSheets[index]; // Remove sheet selection for this file
        this.renderFilesList();
        this.clearDataPreview();
        this.hideSheetsSection();
    },

    clearAllFiles() {
        this.uploadedFiles = [];
        this.selectedSheets = {};
        this.renderFilesList();
        this.clearDataPreview();
        this.hideSheetsSection();
    },

    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            xlsx: '<i class="fas fa-file-excel" style="color: #2ecc71;"></i>',
            xls: '<i class="fas fa-file-excel" style="color: #2ecc71;"></i>',
            csv: '<i class="fas fa-file-csv" style="color: #3498db;"></i>',
            json: '<i class="fas fa-file-code" style="color: #f39c12;"></i>',
            db: '<i class="fas fa-database" style="color: #607d8b;"></i>', // For potential database files
            sqlite: '<i class="fas fa-database" style="color: #607d8b;"></i>'
        };
        return icons[extension] || '<i class="fas fa-file-alt"></i>';
    },

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    async previewFile(index) {
        const file = this.uploadedFiles[index];
        if (!file) return;

        this.showProgressOverlay(i18n.getTranslation('analytics.upload.previewingFile', { filename: file.name }));
        this.clearDataPreview();
        this.hideSheetsSection();

        try {
            const fileContent = await file.arrayBuffer();
            const fileExtension = file.name.split('.').pop().toLowerCase();

            if (fileExtension === 'xlsx' || fileExtension === 'xls') {
                const response = await analyticsService.getExcelSheets(fileContent, file.name);
                if (response.success) {
                    this.renderSheetsSelection(response.sheets, index);
                    this.showSheetsSection();
                } else {
                    this.showError(response.error);
                }
            } else {
                // For CSV, JSON, or other non-Excel files, directly process for preview
                const response = await analyticsService.processFile(fileContent, file.name);
                if (response.success) {
                    this.renderDataPreview(JSON.parse(response.data));
                } else {
                    this.showError(response.error);
                }
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.upload.previewError', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    renderSheetsSelection(sheets, fileIndex) {
        const sheetsCheckboxes = document.getElementById('sheetsCheckboxes');
        sheetsCheckboxes.innerHTML = sheets.map(sheet => `
            <label class="checkbox-container">
                <input type="checkbox" value="${sheet}" onchange="fileUploadModule.handleSheetSelection(${fileIndex}, '${sheet}', this.checked)"
                    ${(this.selectedSheets[fileIndex] && this.selectedSheets[fileIndex].includes(sheet)) ? 'checked' : ''}>
                <span class="checkmark"></span>
                ${sheet}
            </label>
        `).join('');
    },

    handleSheetSelection(fileIndex, sheetName, isChecked) {
        if (!this.selectedSheets[fileIndex]) {
            this.selectedSheets[fileIndex] = [];
        }
        if (isChecked) {
            if (!this.selectedSheets[fileIndex].includes(sheetName)) {
                this.selectedSheets[fileIndex].push(sheetName);
            }
        } else {
            this.selectedSheets[fileIndex] = this.selectedSheets[fileIndex].filter(s => s !== sheetName);
        }
        // Optionally, re-preview the first selected sheet if any
        if (this.selectedSheets[fileIndex].length > 0) {
            this.previewSheet(fileIndex, this.selectedSheets[fileIndex][0]);
        } else {
            this.clearDataPreview();
        }
    },

    selectAllSheets() {
        const checkboxes = document.querySelectorAll('#sheetsCheckboxes input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            const fileIndex = parseInt(checkbox.closest('.file-item')?.dataset.index || '0'); // Assuming current file is the one being previewed
            const sheetName = checkbox.value;
            this.handleSheetSelection(fileIndex, sheetName, true);
        });
    },

    clearSheetSelection() {
        const checkboxes = document.querySelectorAll('#sheetsCheckboxes input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
            const fileIndex = parseInt(checkbox.closest('.file-item')?.dataset.index || '0'); // Assuming current file is the one being previewed
            const sheetName = checkbox.value;
            this.handleSheetSelection(fileIndex, sheetName, false);
        });
        this.clearDataPreview();
    },

    async previewSheet(fileIndex, sheetName) {
        const file = this.uploadedFiles[fileIndex];
        if (!file) return;

        this.showProgressOverlay(i18n.getTranslation('analytics.upload.previewingSheet', { sheetName: sheetName }));
        this.clearDataPreview();

        try {
            const fileContent = await file.arrayBuffer();
            const response = await analyticsService.processFile(fileContent, file.name, sheetName);
            if (response.success) {
                this.renderDataPreview(JSON.parse(response.data));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.upload.previewError', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    renderDataPreview(data) {
        const dataPreviewContainer = document.getElementById('dataPreview');
        if (!data || data.length === 0) {
            dataPreviewContainer.innerHTML = `
                <div style="text-align: center; color: #666; padding: 40px;">
                    <i class="fas fa-table fa-3x" style="margin-bottom: 10px; display: block;"></i>
                    <p>${i18n.getTranslation('analytics.upload.noDataPreview')}</p>
                </div>
            `;
            return;
        }

        const columns = Object.keys(data[0]);
        let html = `
            <table class="data-preview-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
        `;

        data.slice(0, 50).forEach(row => { // Limit preview to 50 rows
            html += '<tr>';
            columns.forEach(col => {
                html += `<td>${row[col]}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';

        if (data.length > 50) {
            html += `
                <div style="text-align: center; margin-top: 10px; color: #666;">
                    <i class="fas fa-info-circle"></i> ${i18n.getTranslation('analytics.upload.showingFirstRows', { count: 50, total: data.length })}
                </div>
            `;
        }
        dataPreviewContainer.innerHTML = html;
    },

    clearDataPreview() {
        document.getElementById('dataPreview').innerHTML = `
            <div style="text-align: center; color: #666; padding: 40px;">
                <i class="fas fa-table fa-3x" style="margin-bottom: 10px; display: block;"></i>
                <p>${i18n.getTranslation('analytics.upload.selectFileToPreview')}</p>
            </div>
        `;
    },

    showSheetsSection() {
        document.getElementById('sheetsSection').style.display = 'block';
    },

    hideSheetsSection() {
        document.getElementById('sheetsSection').style.display = 'none';
    },

    async processSelectedFiles() {
        if (this.uploadedFiles.length === 0) {
            this.showError(i18n.getTranslation('analytics.upload.noFilesToProcess'));
            return;
        }

        this.showProgressOverlay(i18n.getTranslation('analytics.upload.processingFiles'));
        const processedResults = [];

        try {
            for (let i = 0; i < this.uploadedFiles.length; i++) {
                const file = this.uploadedFiles[i];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                const fileContent = await file.arrayBuffer();

                this.updateProgressDetails(i18n.getTranslation('analytics.upload.processingFile', { filename: file.name }));

                if ((fileExtension === 'xlsx' || fileExtension === 'xls') && this.selectedSheets[i] && this.selectedSheets[i].length > 0) {
                    for (const sheetName of this.selectedSheets[i]) {
                        this.updateProgressDetails(i18n.getTranslation('analytics.upload.processingSheet', { sheetName: sheetName, filename: file.name }));
                        const response = await analyticsService.processFile(fileContent, file.name, sheetName);
                        if (response.success) {
                            processedResults.push({ filename: file.name, sheet: sheetName, data: JSON.parse(response.data), summary: response.summary });
                        } else {
                            this.showError(i18n.getTranslation('analytics.upload.processError', { filename: file.name, error: response.error }));
                        }
                    }
                } else {
                    const response = await analyticsService.processFile(fileContent, file.name);
                    if (response.success) {
                        processedResults.push({ filename: file.name, data: JSON.parse(response.data), summary: response.summary });
                    } else {
                        this.showError(i18n.getTranslation('analytics.upload.processError', { filename: file.name, error: response.error }));
                    }
                }
            }
            
            // After processing, switch to analysis tab and display results
            document.querySelector('.analytics-tab[data-tab="analysis"]').click();
            this.displayProcessedDataInAnalysisTab(processedResults);
            this.showSuccess(i18n.getTranslation('analytics.upload.filesProcessedSuccessfully', { count: processedResults.length }));

        } catch (error) {
            this.showError(i18n.getTranslation('analytics.upload.overallProcessError', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    displayProcessedDataInAnalysisTab(results) {
        const dataPreviewContainer = document.getElementById('analysisDataPreview');
        const chartContainer = document.getElementById('analysisChartContainer');
        const xAxisSelect = document.getElementById('xAxisSelect');
        const yAxisSelect = document.getElementById('yAxisSelect');
        const noChartDataMessage = document.getElementById('noChartDataMessage');

        // Clear previous content
        dataPreviewContainer.innerHTML = '';
        xAxisSelect.innerHTML = '<option value="" data-i18n="analytics.chart.selectXAxis">Select X-Axis</option>';
        yAxisSelect.innerHTML = '<option value="" data-i18n="analytics.chart.selectYAxis">Select Y-Axis</option>';
        if (this.currentChart) {
            this.currentChart.destroy();
            this.currentChart = null;
        }
        noChartDataMessage.style.display = 'block'; // Show "No data available" by default

        if (results.length === 0) {
            dataPreviewContainer.innerHTML = `<p>${i18n.getTranslation('analytics.analysis.noDataAvailable')}</p>`;
            return;
        }

        // For simplicity, display the first processed file's data in the preview
        const firstResult = results[0];
        this.currentAnalysisData = firstResult.data; // Store data for chart rendering

        let previewHtml = `<h3>${i18n.getTranslation('analytics.analysis.previewOf')} ${firstResult.filename}`;
        if (firstResult.sheet) {
            previewHtml += ` (${firstResult.sheet})`;
        }
        previewHtml += `</h3>`;
        
        if (firstResult.data && firstResult.data.length > 0) {
            const columns = Object.keys(firstResult.data[0]);
            previewHtml += `
                <table class="data-preview-table">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
            `;
            firstResult.data.slice(0, 10).forEach(row => { // Show first 10 rows in analysis preview
                previewHtml += '<tr>';
                columns.forEach(col => {
                    previewHtml += `<td>${row[col]}</td>`;
                });
                previewHtml += '</tr>';
            });
            previewHtml += '</tbody></table>';
            if (firstResult.data.length > 10) {
                previewHtml += `<p style="text-align: center; color: #666;">${i18n.getTranslation('analytics.analysis.showingFirstRows', { count: 10, total: firstResult.data.length })}</p>`;
            }

            // Populate X and Y axis selects
            columns.forEach(col => {
                const optionX = document.createElement('option');
                optionX.value = col;
                optionX.textContent = col;
                xAxisSelect.appendChild(optionX);

                const optionY = document.createElement('option');
                optionY.value = col;
                optionY.textContent = col;
                yAxisSelect.appendChild(optionY);
            });
            noChartDataMessage.style.display = 'none'; // Hide "No data available" if data is present
        } else {
            previewHtml += `<p>${i18n.getTranslation('analytics.analysis.noDataInFile')}</p>`;
        }
        dataPreviewContainer.innerHTML = previewHtml;
        this.handleAiAnalysisTypeChange(); // Initialize AI analysis parameters based on available columns
    },

    renderDbTablesList(tables) {
        const dbTablesListContainer = document.getElementById('dbTablesList');
        dbTablesListContainer.innerHTML = ''; // Clear existing list

        if (tables.length === 0) {
            dbTablesListContainer.innerHTML = `
                <p style="text-align: center; color: #666; padding: 20px;">
                    ${i18n.getTranslation('analytics.database.noTablesFound')}
                </p>
            `;
            return;
        }

        tables.forEach(table => {
            const tableItem = document.createElement('div');
            tableItem.className = 'file-item'; // Reusing file-item style
            tableItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon"><i class="fas fa-table" style="color: #607d8b;"></i></div>
                    <div class="file-details">
                        <h4>${table.name}</h4>
                        <p>${table.columns.length} ${i18n.getTranslation('analytics.tables.columns')} • ${table.row_count} ${i18n.getTranslation('analytics.tables.rows')}</p>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-info" onclick="fileUploadModule.previewDbTable('${table.name}')">
                        <i class="fas fa-eye"></i> ${i18n.getTranslation('common.preview')}
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="fileUploadModule.selectDbTableForAnalysis('${table.name}')">
                        <i class="fas fa-chart-line"></i> ${i18n.getTranslation('analytics.database.analyze')}
                    </button>
                </div>
            `;
            dbTablesListContainer.appendChild(tableItem);
        });
    },

    async previewDbTable(tableName) {
        this.showProgressOverlay(i18n.getTranslation('analytics.database.previewingTable', { tableName: tableName }));
        this.clearDataPreview();
        try {
            // Assuming connection parameters are stored or can be retrieved
            // For now, we'll use placeholder connection params. In a real app, these would come from the form.
            const connectionParams = {
                db_type: document.getElementById('dbType').value,
                host: document.getElementById('dbHost').value,
                port: document.getElementById('dbPort').value,
                database: document.getElementById('dbName').value,
                username: document.getElementById('dbUser').value,
                password: document.getElementById('dbPassword').value
            };
            const response = await analyticsService.fetchDatabaseTableData(connectionParams, tableName);
            if (response.success) {
                this.renderDataPreview(JSON.parse(response.data));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.database.previewError', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    async selectDbTableForAnalysis(tableName) {
        this.showProgressOverlay(i18n.getTranslation('analytics.database.analyzingTable', { tableName: tableName }));
        try {
            const connectionParams = {
                db_type: document.getElementById('dbType').value,
                host: document.getElementById('dbHost').value,
                port: document.getElementById('dbPort').value,
                database: document.getElementById('dbName').value,
                username: document.getElementById('dbUser').value,
                password: document.getElementById('dbPassword').value
            };
            const response = await analyticsService.fetchDatabaseTableData(connectionParams, tableName);
            if (response.success) {
                document.querySelector('.analytics-tab[data-tab="analysis"]').click();
                this.displayProcessedDataInAnalysisTab([{ filename: tableName, data: JSON.parse(response.data), summary: response.summary }]);
                this.showSuccess(i18n.getTranslation('analytics.database.tableLoadedForAnalysis', { tableName: tableName }));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.database.analysisError', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    renderChart() {
        const chartType = document.getElementById('chartTypeSelect').value;
        const xAxisColumn = document.getElementById('xAxisSelect').value;
        const yAxisColumn = document.getElementById('yAxisSelect').value;
        const canvas = document.getElementById('myChart');
        const noChartDataMessage = document.getElementById('noChartDataMessage');

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0 || !xAxisColumn || !yAxisColumn) {
            noChartDataMessage.style.display = 'block';
            if (this.currentChart) {
                this.currentChart.destroy();
                this.currentChart = null;
            }
            return;
        }

        noChartDataMessage.style.display = 'none';

        const labels = this.currentAnalysisData.map(row => row[xAxisColumn]);
        const data = this.currentAnalysisData.map(row => row[yAxisColumn]);

        if (this.currentChart) {
            this.currentChart.destroy(); // Destroy existing chart instance
        }

        const ctx = canvas.getContext('2d');
        this.currentChart = new Chart(ctx, {
            type: chartType,
            data: {
                labels: labels,
                datasets: [{
                    label: yAxisColumn,
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: xAxisColumn
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: yAxisColumn
                        }
                    }
                }
            }
        });
    },

    showProgressOverlay(message) {
        document.getElementById('progress-message').textContent = message;
        document.getElementById('progress-details').textContent = '';
        document.getElementById('progress-overlay').style.display = 'flex';
    },

    handleAiAnalysisTypeChange() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisParametersDiv = document.getElementById('aiAnalysisParameters');
        aiAnalysisParametersDiv.innerHTML = '';
        aiAnalysisParametersDiv.style.display = 'none';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0) {
            return;
        }

        const columns = Object.keys(this.currentAnalysisData[0]);
        const numericColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'number');
        const categoricalColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'string');

        let paramsHtml = '';
        switch (aiAnalysisType) {
            case 'descriptive':
                paramsHtml = `
                    <label for="descriptiveColumn" data-i18n="analytics.aiAnalysis.params.column">Column:</label>
                    <select id="descriptiveColumn" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'correlation':
                paramsHtml = `
                    <label for="correlationColumn1" data-i18n="analytics.aiAnalysis.params.column1">Column 1:</label>
                    <select id="correlationColumn1" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="correlationColumn2" data-i18n="analytics.aiAnalysis.params.column2">Column 2:</label>
                    <select id="correlationColumn2" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'prediction':
                paramsHtml = `
                    <label for="predictionTarget" data-i18n="analytics.aiAnalysis.params.target">Target Column:</label>
                    <select id="predictionTarget" class="form-control">
                        <option value="">-- Select Target --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="predictionFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="predictionFeatures" class="form-control" placeholder="e.g., column1, column2">
                `;
                break;
            case 'clustering':
                paramsHtml = `
                    <label for="clusteringFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="clusteringFeatures" class="form-control" placeholder="e.g., column1, column2">
                    <label for="numClusters" data-i18n="analytics.aiAnalysis.params.numClusters">Number of Clusters:</label>
                    <input type="number" id="numClusters" class="form-control" value="3" min="2">
                `;
                break;
        }
        if (paramsHtml) {
            aiAnalysisParametersDiv.innerHTML = paramsHtml;
            aiAnalysisParametersDiv.style.display = 'block';
        }
    },

    async runAiAnalysis() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisResultsDiv = document.getElementById('aiAnalysisResults');
        aiAnalysisResultsDiv.innerHTML = '';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0 || !aiAnalysisType) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.selectDataAndType'));
            return;
        }

        this.showProgressOverlay(i18n.getTranslation('analytics.aiAnalysis.runningAnalysis', { type: aiAnalysisType }));

        let parameters = {};
        try {
            switch (aiAnalysisType) {
                case 'descriptive':
                    parameters.column = document.getElementById('descriptiveColumn').value;
                    if (!parameters.column) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectColumn'));
                    break;
                case 'correlation':
                    parameters.column1 = document.getElementById('correlationColumn1').value;
                    parameters.column2 = document.getElementById('correlationColumn2').value;
                    if (!parameters.column1 || !parameters.column2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTwoColumns'));
                    break;
                case 'prediction':
                    parameters.target = document.getElementById('predictionTarget').value;
                    parameters.features = document.getElementById('predictionFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    if (!parameters.target || parameters.features.length === 0) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTargetAndFeatures'));
                    break;
                case 'clustering':
                    parameters.features = document.getElementById('clusteringFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    parameters.num_clusters = parseInt(document.getElementById('numClusters').value);
                    if (parameters.features.length === 0 || isNaN(parameters.num_clusters) || parameters.num_clusters < 2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectFeaturesAndClusters'));
                    break;
            }

            const response = await analyticsService.analyzeDataWithAI(JSON.stringify(this.currentAnalysisData), aiAnalysisType, parameters);
            if (response.success) {
                aiAnalysisResultsDiv.innerHTML = `
                    <h4>${i18n.getTranslation('analytics.aiAnalysis.results.title')}</h4>
                    <pre>${JSON.stringify(response.results, null, 2)}</pre>
                `;
                this.showSuccess(i18n.getTranslation('analytics.aiAnalysis.results.success'));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.errors.general', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    handleAiAnalysisTypeChange() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisParametersDiv = document.getElementById('aiAnalysisParameters');
        aiAnalysisParametersDiv.innerHTML = '';
        aiAnalysisParametersDiv.style.display = 'none';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0) {
            return;
        }

        const columns = Object.keys(this.currentAnalysisData[0]);
        const numericColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'number');
        const categoricalColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'string');

        let paramsHtml = '';
        switch (aiAnalysisType) {
            case 'descriptive':
                paramsHtml = `
                    <label for="descriptiveColumn" data-i18n="analytics.aiAnalysis.params.column">Column:</label>
                    <select id="descriptiveColumn" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'correlation':
                paramsHtml = `
                    <label for="correlationColumn1" data-i18n="analytics.aiAnalysis.params.column1">Column 1:</label>
                    <select id="correlationColumn1" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="correlationColumn2" data-i18n="analytics.aiAnalysis.params.column2">Column 2:</label>
                    <select id="correlationColumn2" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'prediction':
                paramsHtml = `
                    <label for="predictionTarget" data-i18n="analytics.aiAnalysis.params.target">Target Column:</label>
                    <select id="predictionTarget" class="form-control">
                        <option value="">-- Select Target --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="predictionFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="predictionFeatures" class="form-control" placeholder="e.g., column1, column2">
                `;
                break;
            case 'clustering':
                paramsHtml = `
                    <label for="clusteringFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="clusteringFeatures" class="form-control" placeholder="e.g., column1, column2">
                    <label for="numClusters" data-i18n="analytics.aiAnalysis.params.numClusters">Number of Clusters:</label>
                    <input type="number" id="numClusters" class="form-control" value="3" min="2">
                `;
                break;
        }
        if (paramsHtml) {
            aiAnalysisParametersDiv.innerHTML = paramsHtml;
            aiAnalysisParametersDiv.style.display = 'block';
        }
    },

    async runAiAnalysis() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisResultsDiv = document.getElementById('aiAnalysisResults');
        aiAnalysisResultsDiv.innerHTML = '';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0 || !aiAnalysisType) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.selectDataAndType'));
            return;
        }

        this.showProgressOverlay(i18n.getTranslation('analytics.aiAnalysis.runningAnalysis', { type: aiAnalysisType }));

        let parameters = {};
        try {
            switch (aiAnalysisType) {
                case 'descriptive':
                    parameters.column = document.getElementById('descriptiveColumn').value;
                    if (!parameters.column) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectColumn'));
                    break;
                case 'correlation':
                    parameters.column1 = document.getElementById('correlationColumn1').value;
                    parameters.column2 = document.getElementById('correlationColumn2').value;
                    if (!parameters.column1 || !parameters.column2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTwoColumns'));
                    break;
                case 'prediction':
                    parameters.target = document.getElementById('predictionTarget').value;
                    parameters.features = document.getElementById('predictionFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    if (!parameters.target || parameters.features.length === 0) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTargetAndFeatures'));
                    break;
                case 'clustering':
                    parameters.features = document.getElementById('clusteringFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    parameters.num_clusters = parseInt(document.getElementById('numClusters').value);
                    if (parameters.features.length === 0 || isNaN(parameters.num_clusters) || parameters.num_clusters < 2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectFeaturesAndClusters'));
                    break;
            }

            const response = await analyticsService.analyzeDataWithAI(JSON.stringify(this.currentAnalysisData), aiAnalysisType, parameters);
            if (response.success) {
                aiAnalysisResultsDiv.innerHTML = `
                    <h4>${i18n.getTranslation('analytics.aiAnalysis.results.title')}</h4>
                    <pre>${JSON.stringify(response.results, null, 2)}</pre>
                `;
                this.showSuccess(i18n.getTranslation('analytics.aiAnalysis.results.success'));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.errors.general', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    handleAiAnalysisTypeChange() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisParametersDiv = document.getElementById('aiAnalysisParameters');
        aiAnalysisParametersDiv.innerHTML = '';
        aiAnalysisParametersDiv.style.display = 'none';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0) {
            return;
        }

        const columns = Object.keys(this.currentAnalysisData[0]);
        const numericColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'number');
        const categoricalColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'string');

        let paramsHtml = '';
        switch (aiAnalysisType) {
            case 'descriptive':
                paramsHtml = `
                    <label for="descriptiveColumn" data-i18n="analytics.aiAnalysis.params.column">Column:</label>
                    <select id="descriptiveColumn" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'correlation':
                paramsHtml = `
                    <label for="correlationColumn1" data-i18n="analytics.aiAnalysis.params.column1">Column 1:</label>
                    <select id="correlationColumn1" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="correlationColumn2" data-i18n="analytics.aiAnalysis.params.column2">Column 2:</label>
                    <select id="correlationColumn2" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'prediction':
                paramsHtml = `
                    <label for="predictionTarget" data-i18n="analytics.aiAnalysis.params.target">Target Column:</label>
                    <select id="predictionTarget" class="form-control">
                        <option value="">-- Select Target --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="predictionFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="predictionFeatures" class="form-control" placeholder="e.g., column1, column2">
                `;
                break;
            case 'clustering':
                paramsHtml = `
                    <label for="clusteringFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="clusteringFeatures" class="form-control" placeholder="e.g., column1, column2">
                    <label for="numClusters" data-i18n="analytics.aiAnalysis.params.numClusters">Number of Clusters:</label>
                    <input type="number" id="numClusters" class="form-control" value="3" min="2">
                `;
                break;
        }
        if (paramsHtml) {
            aiAnalysisParametersDiv.innerHTML = paramsHtml;
            aiAnalysisParametersDiv.style.display = 'block';
        }
    },

    async runAiAnalysis() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisResultsDiv = document.getElementById('aiAnalysisResults');
        aiAnalysisResultsDiv.innerHTML = '';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0 || !aiAnalysisType) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.selectDataAndType'));
            return;
        }

        this.showProgressOverlay(i18n.getTranslation('analytics.aiAnalysis.runningAnalysis', { type: aiAnalysisType }));

        let parameters = {};
        try {
            switch (aiAnalysisType) {
                case 'descriptive':
                    parameters.column = document.getElementById('descriptiveColumn').value;
                    if (!parameters.column) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectColumn'));
                    break;
                case 'correlation':
                    parameters.column1 = document.getElementById('correlationColumn1').value;
                    parameters.column2 = document.getElementById('correlationColumn2').value;
                    if (!parameters.column1 || !parameters.column2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTwoColumns'));
                    break;
                case 'prediction':
                    parameters.target = document.getElementById('predictionTarget').value;
                    parameters.features = document.getElementById('predictionFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    if (!parameters.target || parameters.features.length === 0) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTargetAndFeatures'));
                    break;
                case 'clustering':
                    parameters.features = document.getElementById('clusteringFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    parameters.num_clusters = parseInt(document.getElementById('numClusters').value);
                    if (parameters.features.length === 0 || isNaN(parameters.num_clusters) || parameters.num_clusters < 2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectFeaturesAndClusters'));
                    break;
            }

            const response = await analyticsService.analyzeDataWithAI(JSON.stringify(this.currentAnalysisData), aiAnalysisType, parameters);
            if (response.success) {
                aiAnalysisResultsDiv.innerHTML = `
                    <h4>${i18n.getTranslation('analytics.aiAnalysis.results.title')}</h4>
                    <pre>${JSON.stringify(response.results, null, 2)}</pre>
                `;
                this.showSuccess(i18n.getTranslation('analytics.aiAnalysis.results.success'));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.errors.general', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    handleAiAnalysisTypeChange() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisParametersDiv = document.getElementById('aiAnalysisParameters');
        aiAnalysisParametersDiv.innerHTML = '';
        aiAnalysisParametersDiv.style.display = 'none';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0) {
            return;
        }

        const columns = Object.keys(this.currentAnalysisData[0]);
        const numericColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'number');
        const categoricalColumns = columns.filter(col => typeof this.currentAnalysisData[0][col] === 'string');

        let paramsHtml = '';
        switch (aiAnalysisType) {
            case 'descriptive':
                paramsHtml = `
                    <label for="descriptiveColumn" data-i18n="analytics.aiAnalysis.params.column">Column:</label>
                    <select id="descriptiveColumn" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'correlation':
                paramsHtml = `
                    <label for="correlationColumn1" data-i18n="analytics.aiAnalysis.params.column1">Column 1:</label>
                    <select id="correlationColumn1" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="correlationColumn2" data-i18n="analytics.aiAnalysis.params.column2">Column 2:</label>
                    <select id="correlationColumn2" class="form-control">
                        <option value="">-- Select Column --</option>
                        ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                `;
                break;
            case 'prediction':
                paramsHtml = `
                    <label for="predictionTarget" data-i18n="analytics.aiAnalysis.params.target">Target Column:</label>
                    <select id="predictionTarget" class="form-control">
                        <option value="">-- Select Target --</option>
                        ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
                    </select>
                    <label for="predictionFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="predictionFeatures" class="form-control" placeholder="e.g., column1, column2">
                `;
                break;
            case 'clustering':
                paramsHtml = `
                    <label for="clusteringFeatures" data-i18n="analytics.aiAnalysis.params.features">Feature Columns (comma-separated):</label>
                    <input type="text" id="clusteringFeatures" class="form-control" placeholder="e.g., column1, column2">
                    <label for="numClusters" data-i18n="analytics.aiAnalysis.params.numClusters">Number of Clusters:</label>
                    <input type="number" id="numClusters" class="form-control" value="3" min="2">
                `;
                break;
        }
        if (paramsHtml) {
            aiAnalysisParametersDiv.innerHTML = paramsHtml;
            aiAnalysisParametersDiv.style.display = 'block';
        }
    },

    async runAiAnalysis() {
        const aiAnalysisType = document.getElementById('aiAnalysisType').value;
        const aiAnalysisResultsDiv = document.getElementById('aiAnalysisResults');
        aiAnalysisResultsDiv.innerHTML = '';

        if (!this.currentAnalysisData || this.currentAnalysisData.length === 0 || !aiAnalysisType) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.selectDataAndType'));
            return;
        }

        this.showProgressOverlay(i18n.getTranslation('analytics.aiAnalysis.runningAnalysis', { type: aiAnalysisType }));

        let parameters = {};
        try {
            switch (aiAnalysisType) {
                case 'descriptive':
                    parameters.column = document.getElementById('descriptiveColumn').value;
                    if (!parameters.column) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectColumn'));
                    break;
                case 'correlation':
                    parameters.column1 = document.getElementById('correlationColumn1').value;
                    parameters.column2 = document.getElementById('correlationColumn2').value;
                    if (!parameters.column1 || !parameters.column2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTwoColumns'));
                    break;
                case 'prediction':
                    parameters.target = document.getElementById('predictionTarget').value;
                    parameters.features = document.getElementById('predictionFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    if (!parameters.target || parameters.features.length === 0) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectTargetAndFeatures'));
                    break;
                case 'clustering':
                    parameters.features = document.getElementById('clusteringFeatures').value.split(',').map(f => f.trim()).filter(f => f);
                    parameters.num_clusters = parseInt(document.getElementById('numClusters').value);
                    if (parameters.features.length === 0 || isNaN(parameters.num_clusters) || parameters.num_clusters < 2) throw new Error(i18n.getTranslation('analytics.aiAnalysis.errors.selectFeaturesAndClusters'));
                    break;
            }

            const response = await analyticsService.analyzeDataWithAI(JSON.stringify(this.currentAnalysisData), aiAnalysisType, parameters);
            if (response.success) {
                aiAnalysisResultsDiv.innerHTML = `
                    <h4>${i18n.getTranslation('analytics.aiAnalysis.results.title')}</h4>
                    <pre>${JSON.stringify(response.results, null, 2)}</pre>
                `;
                this.showSuccess(i18n.getTranslation('analytics.aiAnalysis.results.success'));
            } else {
                this.showError(response.error);
            }
        } catch (error) {
            this.showError(i18n.getTranslation('analytics.aiAnalysis.errors.general', { error: error.message }));
        } finally {
            this.hideProgressOverlay();
        }
    },

    updateProgressDetails(message) {
        document.getElementById('progress-details').textContent = message;
    },

    hideProgressOverlay() {
        document.getElementById('progress-overlay').style.display = 'none';
    },

    showError(message) {
        alert(`${i18n.getTranslation('common.error')}: ${message}`);
    },

    showSuccess(message) {
        alert(`${i18n.getTranslation('common.success')}: ${message}`);
    }
};
