// Canvas Course Extractor Frontend Logic
class CanvasExtractor {
    constructor() {
        this.currentStep = 1;
        this.sessionId = null;
        this.selectedCourseId = null;
        this.selectedCourseName = null;
        this.downloadUrl = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.goToStep(1);
    }

    setupEventListeners() {
        // Authentication form
        const authForm = document.getElementById('authForm');
        authForm.addEventListener('submit', (e) => this.handleAuthentication(e));

        // Course selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.course-item')) {
                this.handleCourseSelection(e.target.closest('.course-item'));
            }
        });

        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadFile());
        }
    }

    // Step navigation
    goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(content => {
            content.style.display = 'none';
        });

        // Show current step
        const currentStepContent = document.getElementById(`step${step}`);
        if (currentStepContent) {
            currentStepContent.style.display = 'block';
        }

        // Update progress bar
        this.updateProgressBar(step);
        this.currentStep = step;

        // Step-specific actions
        if (step === 2) {
            this.loadCourses();
        }
    }

    updateProgressBar(activeStep) {
        document.querySelectorAll('.progress-step').forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNumber === activeStep) {
                step.classList.add('active');
            } else if (stepNumber < activeStep) {
                step.classList.add('completed');
            }
        });
    }

    // Authentication handling
    async handleAuthentication(e) {
        e.preventDefault();
        
        const connectBtn = document.getElementById('connectBtn');
        const btnText = connectBtn.querySelector('.btn-text');
        const btnLoading = connectBtn.querySelector('.btn-loading');
        
        // Show loading state
        connectBtn.classList.add('loading');
        connectBtn.disabled = true;

        const formData = new FormData(e.target);
        const apiUrl = formData.get('apiUrl').trim();
        const apiKey = formData.get('apiKey').trim();

        try {
            const response = await fetch('/api/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_url: apiUrl,
                    api_key: apiKey
                })
            });

            const result = await response.json();

            if (result.success) {
                this.sessionId = result.session_id;
                this.showSuccess(result.message);
                setTimeout(() => this.goToStep(2), 1000);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            this.showError('Connection failed. Please check your network and try again.');
        } finally {
            // Hide loading state
            connectBtn.classList.remove('loading');
            connectBtn.disabled = false;
        }
    }

    // Load courses
    async loadCourses() {
        const coursesLoading = document.getElementById('coursesLoading');
        const coursesList = document.getElementById('coursesList');
        
        coursesLoading.style.display = 'block';
        coursesList.style.display = 'none';

        try {
            const response = await fetch('/api/courses', {
                method: 'GET',
                headers: {
                    'Session-Id': this.sessionId
                }
            });

            const result = await response.json();

            if (result.success) {
                this.renderCourses(result.courses);
                coursesLoading.style.display = 'none';
                coursesList.style.display = 'block';
            } else {
                this.showError(result.message);
                this.goToStep(1);
            }
        } catch (error) {
            this.showError('Failed to load courses. Please try again.');
            this.goToStep(1);
        }
    }

    renderCourses(courses) {
        const container = document.getElementById('coursesContainer');
        container.innerHTML = '';

        if (courses.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 40px; color: #6c757d;">No courses found.</p>';
            return;
        }

        courses.forEach(course => {
            const courseItem = document.createElement('div');
            courseItem.className = 'course-item';
            courseItem.dataset.courseId = course.id;
            courseItem.dataset.courseName = course.name;

            const statusClass = course.workflow_state === 'available' ? 'available' : 'unpublished';
            
            courseItem.innerHTML = `
                <div class="course-info">
                    <h3>${this.escapeHtml(course.name)}</h3>
                    <p>Course Code: ${this.escapeHtml(course.code)}</p>
                </div>
                <div class="course-status ${statusClass}">
                    ${course.workflow_state}
                </div>
            `;

            container.appendChild(courseItem);
        });
    }

    handleCourseSelection(courseItem) {
        // Remove previous selection
        document.querySelectorAll('.course-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Select current course
        courseItem.classList.add('selected');
        this.selectedCourseId = courseItem.dataset.courseId;
        this.selectedCourseName = courseItem.dataset.courseName;

        // Enable continue button
        const selectCourseBtn = document.getElementById('selectCourseBtn');
        selectCourseBtn.disabled = false;
    }

    // Parse selected course
    async proceedWithSelectedCourse() {
        if (!this.selectedCourseId) {
            this.showError('Please select a course first.');
            return;
        }

        this.goToStep(3);
        await this.parseCourse();
    }

    async parseCourse() {
        const parsingMessage = document.getElementById('parsingMessage');
        
        try {
            parsingMessage.textContent = `Parsing "${this.selectedCourseName}"...`;

            const response = await fetch('/api/parse-course', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Session-Id': this.sessionId
                },
                body: JSON.stringify({
                    course_id: parseInt(this.selectedCourseId)
                })
            });

            const result = await response.json();

            if (result.success) {
                this.downloadUrl = result.download_url;
                this.showParsingResults(result);
                setTimeout(() => this.goToStep(4), 1000);
            } else {
                this.showError(result.message);
                this.goToStep(2);
            }
        } catch (error) {
            this.showError('Failed to parse course. Please try again.');
            this.goToStep(2);
        }
    }

    showParsingResults(result) {
        const resultsInfo = document.getElementById('resultsInfo');
        resultsInfo.innerHTML = `
            <h3>📊 Extraction Summary</h3>
            <div class="stat">
                <span class="stat-label">Course Name:</span>
                <span class="stat-value">${this.escapeHtml(result.course_name)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Modules Found:</span>
                <span class="stat-value">${result.modules_count}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Total Items:</span>
                <span class="stat-value">${result.total_items}</span>
            </div>
            <div class="stat">
                <span class="stat-label">File Name:</span>
                <span class="stat-value">${this.escapeHtml(result.filename)}</span>
            </div>
        `;

        // Set up download button
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.onclick = () => this.downloadFile();
    }

    // Download the generated file
    downloadFile() {
        if (this.downloadUrl) {
            window.location.href = this.downloadUrl;
            this.showSuccess('Download started! Check your downloads folder.');
        } else {
            this.showError('Download URL not available. Please try extracting the course again.');
        }
    }

    // Start over
    startOver() {
        this.currentStep = 1;
        this.sessionId = null;
        this.selectedCourseId = null;
        this.selectedCourseName = null;
        this.downloadUrl = null;
        
        // Reset form
        document.getElementById('authForm').reset();
        
        // Clean up session if exists
        if (this.sessionId) {
            fetch('/api/cleanup', {
                method: 'POST',
                headers: {
                    'Session-Id': this.sessionId
                }
            });
        }
        
        this.goToStep(1);
    }

    // Utility functions
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        const errorText = errorDiv.querySelector('.error-text');
        errorText.textContent = message;
        errorDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => this.hideError(), 5000);
    }

    showSuccess(message) {
        const successDiv = document.getElementById('successMessage');
        const successText = successDiv.querySelector('.success-text');
        successText.textContent = message;
        successDiv.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => this.hideSuccess(), 3000);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }

    hideSuccess() {
        document.getElementById('successMessage').style.display = 'none';
    }
}

// Global functions (called from HTML)
function toggleApiKeyHelp() {
    const helpDiv = document.getElementById('apiKeyHelp');
    helpDiv.style.display = helpDiv.style.display === 'none' ? 'block' : 'none';
}

function goToStep(step) {
    window.canvasExtractor.goToStep(step);
}

function selectCourse() {
    window.canvasExtractor.proceedWithSelectedCourse();
}

function startOver() {
    window.canvasExtractor.startOver();
}

function hideError() {
    window.canvasExtractor.hideError();
}

function hideSuccess() {
    window.canvasExtractor.hideSuccess();
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.canvasExtractor = new CanvasExtractor();
}); 