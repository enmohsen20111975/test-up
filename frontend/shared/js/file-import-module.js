// File Import Module - Advanced file uploading and management
class FileImportModule {
    constructor() {
        this.uploadedFiles = [];
        this.currentFile = null;
        this.excelSheets = [];
        this.selectedSheets = [];
    }

    async importFile(file) {
        const fileType = file.name.split('.').pop().toLowerCase();
        let data = [];
        
        try {
            if (fileType === 'csv') {
                const text = await this.readFileAsText(file);
                data = this.parseCSV(text);
            } else if (fileType === 'json') {
                const text = await this.readFileAsText(file);
                data = this.parseJSON(text);
            } else if (fileType === 'xlsx' || fileType === 'xls') {
                data = await this.readExcelFile(file);
            } else {
                throw new Error(`Unsupported file type: ${fileType}`);
            }
            
            return {
                name: file.name,
                data: data,
                rowCount: data.length,
                columns: data.length > 0 ? Object.keys(data[0]) : []
            };
        } catch (error) {
            console.error('File import error:', error);
            throw error;
        }
    }

    async handleFileUpload(file) {
        const fileType = file.name.split('.').pop().toLowerCase();

        try {
            let data;
            
            if (fileType === 'csv') {
                const text = await this.readFileAsText(file);
                data = this.parseCSV(text);
            } else if (fileType === 'json') {
                const text = await this.readFileAsText(file);
                data = this.parseJSON(text);
            } else if (fileType === 'xlsx' || fileType === 'xls') {
                data = await this.readExcelFile(file);
            } else {
                throw new Error('Unsupported file type');
            }

            return await this.processFile(file, data);
        } catch (error) {
            console.error('File upload error:', error);
            throw error;
        }
    }

    parseCSV(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        if (lines.length === 0) return [];

        // Parse CSV handling quoted fields
        const parseCSVLine = (line) => {
            const result = [];
            let current = '';
            let inQuotes = false;
            
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                const nextChar = line[i + 1];
                
                if (char === '"') {
                    if (inQuotes && nextChar === '"') {
                        current += '"';
                        i++;
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    result.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            result.push(current.trim());
            return result;
        };

        const headers = parseCSVLine(lines[0]);
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            const values = parseCSVLine(lines[i]);
            if (values.length !== headers.length && values.length > 0) {
                console.warn(`Row ${i + 1} has ${values.length} columns but expected ${headers.length}`);
            }
            
            const row = {};
            headers.forEach((header, index) => {
                let value = values[index] !== undefined ? values[index] : '';
                // Auto-convert numbers
                if (value && !isNaN(value) && value.trim() !== '') {
                    const num = parseFloat(value);
                    if (!isNaN(num)) value = num;
                }
                row[header] = value;
            });
            data.push(row);
        }

        return data;
    }

    parseJSON(text) {
        const data = JSON.parse(text);
        if (!Array.isArray(data)) {
            if (typeof data === 'object') {
                return [data];
            }
            throw new Error('JSON must be an array or object');
        }
        return data;
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    async readExcelFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const jsonData = XLSX.utils.sheet_to_json(firstSheet);
                    resolve(jsonData);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = (e) => reject(e);
            reader.readAsArrayBuffer(file);
        });
    }

    async getExcelSheets(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    resolve(workbook.SheetNames);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = (e) => reject(e);
            reader.readAsArrayBuffer(file);
        });
    }

    async processFile(file, data) {
        try {
            // Upload to backend for processing
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/analytics/upload', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'File upload failed');
            }

            const result = await response.json();
            
            // Add to uploaded files
            const fileData = {
                id: Date.now().toString(),
                name: file.name,
                type: file.type,
                size: file.size,
                data: JSON.parse(result.data),
                summary: result.summary,
                uploadedAt: new Date()
            };
            
            this.uploadedFiles.push(fileData);
            this.currentFile = fileData;
            
            return fileData;
        } catch (error) {
            console.error('File processing error:', error);
            throw error;
        }
    }

    async connectToDatabase(connectionParams) {
        try {
            const response = await fetch('/analytics/database-connect', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: JSON.stringify(connectionParams)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Database connection failed');
            }

            const result = await response.json();
            return result.tables;
        } catch (error) {
            console.error('Database connection error:', error);
            throw error;
        }
    }

    getFileById(fileId) {
        return this.uploadedFiles.find(file => file.id === fileId);
    }

    getFilesByType(fileType) {
        return this.uploadedFiles.filter(file => file.type.includes(fileType));
    }

    removeFile(fileId) {
        this.uploadedFiles = this.uploadedFiles.filter(file => file.id !== fileId);
        if (this.currentFile && this.currentFile.id === fileId) {
            this.currentFile = null;
        }
    }

    clearAllFiles() {
        this.uploadedFiles = [];
        this.currentFile = null;
    }

    async exportData(data, format = 'csv', filename = 'export') {
        let content;
        let mimeType;
        let extension;

        if (format === 'csv') {
            content = this.convertToCSV(data);
            mimeType = 'text/csv';
            extension = 'csv';
        } else if (format === 'json') {
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            extension = 'json';
        } else if (format === 'excel') {
            return this.exportToExcel(data, filename);
        } else {
            throw new Error('Unsupported export format');
        }

        this.downloadFile(content, `${filename}.${extension}`, mimeType);
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => {
                    const value = row[header];
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                }).join(',')
            )
        ].join('\n');
        
        return csv;
    }

    async exportToExcel(data, filename) {
        try {
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Data');
            
            XLSX.writeFile(wb, `${filename}.xlsx`);
        } catch (error) {
            console.error('Excel export error:', error);
            throw error;
        }
    }

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }
}

// Initialize file import module
const fileImportModule = new FileImportModule();
