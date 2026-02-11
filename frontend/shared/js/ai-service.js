// AI Service
class AIService {
    constructor() {
        this.baseUrl = '/api';
    }
    
    async explainCalculation(calcType, inputs, results) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/explain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: JSON.stringify({
                    calc_type: calcType,
                    inputs: inputs,
                    results: results
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get AI explanation');
            }
            
            const data = await response.json();
            return data.explanation;
        } catch (error) {
            console.error('AI explanation error:', error);
            if (typeof i18n !== 'undefined') {
                return i18n.getTranslation('ai.errors.explain');
            }
            return 'Unable to get AI explanation. Please try again.';
        }
    }
    
    async analyzeData(datasetSummary, chartType = 'bar') {
        try {
            const response = await fetch(`${this.baseUrl}/ai/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: JSON.stringify({
                    dataset_summary: datasetSummary,
                    chart_type: chartType
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to analyze data');
            }
            
            const data = await response.json();
            return data.analysis;
        } catch (error) {
            console.error('Data analysis error:', error);
            if (typeof i18n !== 'undefined') {
                return i18n.getTranslation('ai.errors.analyze');
            }
            return 'Unable to analyze data. Please try again.';
        }
    }
    
    async generateReport(calcResults, analysisData, template = 'professional') {
        try {
            const response = await fetch(`${this.baseUrl}/ai/report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: JSON.stringify({
                    calc_results: calcResults,
                    analysis_data: analysisData,
                    template: template
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate report');
            }
            
            const data = await response.json();
            return data.report;
        } catch (error) {
            console.error('Report generation error:', error);
            if (typeof i18n !== 'undefined') {
                return i18n.getTranslation('ai.errors.report');
            }
            return 'Unable to generate report. Please try again.';
        }
    }
    
    async chat(message, context = '') {
        try {
            const response = await fetch(`${this.baseUrl}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authService.getToken()}`
                },
                body: JSON.stringify({
                    message: message,
                    context: context
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to chat with AI');
            }
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('AI chat error:', error);
            if (typeof i18n !== 'undefined') {
                return i18n.getTranslation('ai.errors.chat');
            }
            return 'Unable to reach AI. Please try again.';
        }
    }
    
    showLoading(element) {
        const loadingText = typeof i18n !== 'undefined' ? i18n.getTranslation('ai.loading') : 'Analyzing...';
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <div style="margin-left: 10px;">${loadingText}</div>
            </div>
        `;
    }
    
    hideLoading(element) {
        element.innerHTML = '';
    }
}

// Initialize AI service
export const aiService = new AIService();
