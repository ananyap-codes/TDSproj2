// Data Analyst Agent API Demo Application
const API_ENDPOINT = 'tdsproj2-production-6765.up.railway.app';

class DataAnalystDemo {
    constructor() {
        this.uploadedFiles = [];
        this.sessionHistory = [];
        this.currentResults = null;
        
        // Example datasets from the application data
        this.exampleData = {
            movies: {
                name: "Movie Revenue Analysis",
                description: "Analyze highest-grossing films data",
                questions: "1. How many $2bn movies were released before 2000?\n2. Which is the earliest film that grossed over $1.5bn?\n3. What's the correlation between Rank and Peak?\n4. Draw a scatterplot of Rank and Peak with a regression line.",
                data: [
                    {"Rank": 1, "Peak": 1, "Title": "Avatar", "Revenue": 2900, "Year": 2009},
                    {"Rank": 2, "Peak": 1, "Title": "Avengers: Endgame", "Revenue": 2800, "Year": 2019},
                    {"Rank": 3, "Peak": 3, "Title": "Avatar 2", "Revenue": 2300, "Year": 2022},
                    {"Rank": 4, "Peak": 1, "Title": "Titanic", "Revenue": 2200, "Year": 1997},
                    {"Rank": 5, "Peak": 5, "Title": "Star Wars VII", "Revenue": 2100, "Year": 2015}
                ]
            },
            sales: {
                name: "Sales Performance",
                description: "Quarterly sales analysis",
                questions: "1. What was the total revenue for the year?\n2. Which quarter had the highest growth rate?\n3. Create a line chart showing quarterly trends.\n4. Identify seasonal patterns in the data.",
                data: [
                    {"Quarter": "Q1", "Revenue": 150000, "Units": 1200, "Growth": 5.2},
                    {"Quarter": "Q2", "Revenue": 165000, "Units": 1350, "Growth": 10.0},
                    {"Quarter": "Q3", "Revenue": 180000, "Units": 1500, "Growth": 9.1},
                    {"Quarter": "Q4", "Revenue": 195000, "Units": 1650, "Growth": 8.3}
                ]
            }
        };
        
        this.init();
    }
    
    init() {
        // Ensure modals are hidden on init
        this.hideAllModals();
        this.setupEventListeners();
        this.loadDefaultApiEndpoint();
    }
    
    hideAllModals() {
        const errorModal = document.getElementById('errorModal');
        const notification = document.getElementById('notification');
        
        if (errorModal) {
            errorModal.classList.add('hidden');
        }
        if (notification) {
            notification.classList.add('hidden');
        }
    }
    
    setupEventListeners() {
        // File upload events
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
            uploadArea.addEventListener('drop', this.handleDrop.bind(this));
            fileInput.addEventListener('change', this.handleFileSelection.bind(this));
        }
        
        // Example card events
        document.querySelectorAll('.example-card').forEach(card => {
            card.addEventListener('click', this.loadExample.bind(this));
        });
        
        // Question input events
        document.querySelectorAll('.example-question-btn').forEach(btn => {
            btn.addEventListener('click', this.addExampleQuestion.bind(this));
        });
        
        // API configuration events
        const testConnectionBtn = document.getElementById('testConnection');
        if (testConnectionBtn) {
            testConnectionBtn.addEventListener('click', this.testApiConnection.bind(this));
        }
        
        // Analysis submission
        const analyzeBtn = document.getElementById('analyzeButton');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.submitAnalysis.bind(this));
        }
        
        // Results events
        const toggleRawBtn = document.getElementById('toggleRaw');
        const exportJsonBtn = document.getElementById('exportJson');
        const exportPdfBtn = document.getElementById('exportPdf');
        
        if (toggleRawBtn) {
            toggleRawBtn.addEventListener('click', this.toggleRawJson.bind(this));
        }
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', this.exportJson.bind(this));
        }
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', this.exportPdf.bind(this));
        }
        
        // Modal events
        const closeError = document.getElementById('closeError');
        const closeErrorBtn = document.getElementById('closeErrorBtn');
        const errorModal = document.getElementById('errorModal');
        
        if (closeError) {
            closeError.addEventListener('click', this.closeErrorModal.bind(this));
        }
        if (closeErrorBtn) {
            closeErrorBtn.addEventListener('click', this.closeErrorModal.bind(this));
        }
        if (errorModal) {
            // Close modal when clicking overlay
            errorModal.addEventListener('click', (e) => {
                if (e.target === errorModal || e.target.classList.contains('modal__overlay')) {
                    this.closeErrorModal();
                }
            });
        }
        
        // History events
        const historyList = document.getElementById('historyList');
        if (historyList) {
            historyList.addEventListener('click', this.loadHistoryItem.bind(this));
        }
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeErrorModal();
            }
        });
    }
    
    loadDefaultApiEndpoint() {
        const apiEndpoint = document.getElementById('apiEndpoint');
        if (apiEndpoint) {
            apiEndpoint.value = 'http://localhost:5000/api/';
        }
    }
    
    // File handling methods
    handleDragOver(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.classList.add('dragover');
        }
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.classList.remove('dragover');
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.classList.remove('dragover');
        }
        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }
    
    handleFileSelection(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
    }
    
    processFiles(files) {
        const validTypes = ['.csv', '.xlsx', '.xls', '.json', '.txt', '.png', '.jpg', '.jpeg', '.tsv'];
        
        files.forEach(file => {
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            
            if (validTypes.includes(fileExt)) {
                if (!this.uploadedFiles.find(f => f.name === file.name && f.size === file.size)) {
                    this.uploadedFiles.push({
                        file: file,
                        name: file.name,
                        size: file.size,
                        type: fileExt,
                        status: 'ready'
                    });
                }
            } else {
                this.showError(`File type ${fileExt} is not supported. Please use: CSV, Excel, JSON, TXT, Images, or TSV files.`);
            }
        });
        
        this.updateFilePreview();
    }
    
    updateFilePreview() {
        const previewContainer = document.getElementById('filePreview');
        if (!previewContainer) return;
        
        previewContainer.innerHTML = '';
        
        if (this.uploadedFiles.length === 0) {
            return;
        }
        
        this.uploadedFiles.forEach((fileData, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item fade-in';
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">${this.getFileIcon(fileData.type)}</div>
                    <div class="file-details">
                        <h4>${fileData.name}</h4>
                        <p>${this.formatFileSize(fileData.size)} • ${fileData.type.toUpperCase()}</p>
                    </div>
                </div>
                <div class="file-status">
                    <span class="status status--success">Ready</span>
                    <button class="file-remove" data-index="${index}" title="Remove file">&times;</button>
                </div>
            `;
            
            // Add remove functionality
            const removeBtn = fileItem.querySelector('.file-remove');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    this.removeFile(parseInt(e.target.dataset.index));
                });
            }
            
            previewContainer.appendChild(fileItem);
        });
    }
    
    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.updateFilePreview();
    }
    
    getFileIcon(type) {
        const icons = {
            '.csv': '📊',
            '.xlsx': '📈',
            '.xls': '📈',
            '.json': '🔧',
            '.txt': '📄',
            '.tsv': '📊',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️'
        };
        return icons[type] || '📄';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Example loading methods
    loadExample(e) {
        const exampleType = e.currentTarget.dataset.example;
        const example = this.exampleData[exampleType];
        
        if (!example) return;
        
        // Clear current files
        this.uploadedFiles = [];
        this.updateFilePreview();
        
        // Create a JSON file with the example data
        const jsonData = JSON.stringify(example.data, null, 2);
        const blob = new Blob([jsonData], { type: 'application/json' });
        const file = new File([blob], `${exampleType}_data.json`, { type: 'application/json' });
        
        this.uploadedFiles.push({
            file: file,
            name: file.name,
            size: file.size,
            type: '.json',
            status: 'ready'
        });
        
        // Set the questions
        const questionsInput = document.getElementById('questionsInput');
        if (questionsInput) {
            questionsInput.value = example.questions;
        }
        
        // Update file preview
        this.updateFilePreview();
        
        // Show success notification
        this.showNotification(`${example.name} example loaded successfully!`);
        
        // Scroll to questions section
        const questionsSection = document.querySelector('.questions-section');
        if (questionsSection) {
            questionsSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
    
    addExampleQuestion(e) {
        const question = e.target.dataset.question;
        const questionsInput = document.getElementById('questionsInput');
        
        if (!questionsInput) return;
        
        if (questionsInput.value.trim()) {
            questionsInput.value += '\n' + question;
        } else {
            questionsInput.value = question;
        }
        
        questionsInput.focus();
        questionsInput.scrollTop = questionsInput.scrollHeight;
    }
    
    // API methods
    async testApiConnection() {
        const apiEndpoint = document.getElementById('apiEndpoint');
        const statusDiv = document.getElementById('connectionStatus');
        
        if (!apiEndpoint || !statusDiv) return;
        
        statusDiv.textContent = 'Testing connection...';
        statusDiv.className = 'connection-status';
        
        try {
            const response = await fetch(apiEndpoint.value + 'health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                statusDiv.textContent = 'Connection successful!';
                statusDiv.className = 'connection-status success';
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            statusDiv.textContent = `Connection failed: ${error.message}`;
            statusDiv.className = 'connection-status error';
        }
        
        // Clear status after 3 seconds
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = 'connection-status';
        }, 3000);
    }
    
    async submitAnalysis() {
        if (this.uploadedFiles.length === 0) {
            this.showError('Please upload at least one file before analyzing.');
            return;
        }
        
        const questionsInput = document.getElementById('questionsInput');
        if (!questionsInput) return;
        
        const questions = questionsInput.value.trim();
        if (!questions) {
            this.showError('Please enter at least one question for analysis.');
            return;
        }
        
        const apiEndpoint = document.getElementById('apiEndpoint');
        if (!apiEndpoint) return;
        
        this.showProgress();
        
        try {
            const formData = new FormData();
            
            // Add files
            this.uploadedFiles.forEach((fileData) => {
                formData.append('files', fileData.file);
            });
            
            // Add questions
            formData.append('questions', questions);
            
            const response = await fetch(apiEndpoint.value + 'analyze', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }
            
            const results = await response.json();
            this.displayResults(results);
            this.addToHistory(questions, results);
            this.showNotification('Analysis completed successfully!');
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}. Please check your API endpoint and try again.`);
        } finally {
            this.hideProgress();
        }
    }
    
    showProgress() {
        const button = document.getElementById('analyzeButton');
        const progressBar = document.getElementById('progressBar');
        
        if (!button || !progressBar) return;
        
        const buttonText = button.querySelector('.button-text');
        const loadingSpinner = button.querySelector('.loading-spinner');
        
        if (buttonText) buttonText.style.display = 'none';
        if (loadingSpinner) loadingSpinner.classList.remove('hidden');
        button.disabled = true;
        
        progressBar.classList.remove('hidden');
        const progressFill = progressBar.querySelector('.progress-bar__fill');
        if (progressFill) {
            progressFill.style.width = '100%';
        }
    }
    
    hideProgress() {
        const button = document.getElementById('analyzeButton');
        const progressBar = document.getElementById('progressBar');
        
        if (!button || !progressBar) return;
        
        const buttonText = button.querySelector('.button-text');
        const loadingSpinner = button.querySelector('.loading-spinner');
        
        if (buttonText) buttonText.style.display = 'inline';
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
        button.disabled = false;
        
        progressBar.classList.add('hidden');
        const progressFill = progressBar.querySelector('.progress-bar__fill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }
    }
    
    displayResults(results) {
        this.currentResults = results;
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');
        const rawJson = document.getElementById('rawJson');
        
        if (!resultsSection || !resultsContent || !rawJson) return;
        
        resultsContent.innerHTML = '';
        
        if (results.answers && Array.isArray(results.answers)) {
            results.answers.forEach((answer, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item fade-in';
                
                let chartsHtml = '';
                if (answer.charts && answer.charts.length > 0) {
                    chartsHtml = `
                        <div class="result-charts">
                            ${answer.charts.map(chart => `
                                <img src="${chart}" alt="Analysis Chart" />
                            `).join('')}
                        </div>
                    `;
                }
                
                resultItem.innerHTML = `
                    <h3>Question ${index + 1}</h3>
                    <p><strong>Q:</strong> ${answer.question || 'Analysis question'}</p>
                    <p><strong>A:</strong> ${answer.answer || 'No answer provided'}</p>
                    ${chartsHtml}
                `;
                
                resultsContent.appendChild(resultItem);
            });
        } else if (results.insights) {
            // Handle alternative response format
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item fade-in';
            resultItem.innerHTML = `
                <h3>Analysis Results</h3>
                <p>${results.insights}</p>
            `;
            resultsContent.appendChild(resultItem);
        } else {
            // Handle any other response format
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item fade-in';
            resultItem.innerHTML = `
                <h3>Analysis Complete</h3>
                <p>Your data has been analyzed. See the raw JSON response below for detailed results.</p>
            `;
            resultsContent.appendChild(resultItem);
        }
        
        // Update raw JSON
        rawJson.textContent = JSON.stringify(results, null, 2);
        
        // Show results section
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    toggleRawJson() {
        const rawJson = document.getElementById('rawJson');
        const toggleBtn = document.getElementById('toggleRaw');
        
        if (!rawJson || !toggleBtn) return;
        
        if (rawJson.classList.contains('hidden')) {
            rawJson.classList.remove('hidden');
            toggleBtn.textContent = 'Hide Raw JSON';
        } else {
            rawJson.classList.add('hidden');
            toggleBtn.textContent = 'Show Raw JSON';
        }
    }
    
    // Export methods
    exportJson() {
        if (!this.currentResults) {
            this.showError('No results to export.');
            return;
        }
        
        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `analysis_results_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.showNotification('Results exported as JSON!');
    }
    
    exportPdf() {
        this.showError('PDF export is not yet implemented in this demo. Use JSON export instead.');
    }
    
    // History management
    addToHistory(questions, results) {
        const historyItem = {
            timestamp: new Date(),
            questions: questions,
            results: results,
            files: this.uploadedFiles.map(f => ({ name: f.name, size: f.size, type: f.type }))
        };
        
        this.sessionHistory.unshift(historyItem);
        
        // Limit history to 10 items
        if (this.sessionHistory.length > 10) {
            this.sessionHistory = this.sessionHistory.slice(0, 10);
        }
        
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        if (this.sessionHistory.length === 0) {
            historyList.innerHTML = '<p class="history-empty">No previous analyses in this session</p>';
            return;
        }
        
        historyList.innerHTML = this.sessionHistory.map((item, index) => `
            <div class="history-item" data-index="${index}">
                <h4>Analysis ${this.sessionHistory.length - index}</h4>
                <p>${item.timestamp.toLocaleString()} • ${item.files.length} file(s)</p>
            </div>
        `).join('');
    }
    
    loadHistoryItem(e) {
        const historyItem = e.target.closest('.history-item');
        if (!historyItem) return;
        
        const index = parseInt(historyItem.dataset.index);
        const item = this.sessionHistory[index];
        
        if (item) {
            const questionsInput = document.getElementById('questionsInput');
            if (questionsInput) {
                questionsInput.value = item.questions;
            }
            this.displayResults(item.results);
            this.showNotification('Previous analysis loaded!');
        }
    }
    
    // Utility methods
    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorModal = document.getElementById('errorModal');
        
        if (errorMessage && errorModal) {
            errorMessage.textContent = message;
            errorModal.classList.remove('hidden');
        }
    }
    
    closeErrorModal() {
        const errorModal = document.getElementById('errorModal');
        if (errorModal) {
            errorModal.classList.add('hidden');
        }
    }
    
    showNotification(message) {
        const notification = document.getElementById('notification');
        const text = notification?.querySelector('.notification__text');
        
        if (notification && text) {
            text.textContent = message;
            notification.classList.remove('hidden');
            
            setTimeout(() => {
                notification.classList.add('hidden');
            }, 3000);
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new DataAnalystDemo();
    } catch (error) {
        console.error('Failed to initialize DataAnalystDemo:', error);
    }
});
