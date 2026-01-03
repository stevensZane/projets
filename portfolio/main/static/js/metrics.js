// static/js/metrics.js
class ProjectMetrics {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.initialized = false;
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    async trackClick(projectSlug, clickType) {
        try {
            const response = await fetch('/api/track-click/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    project_slug: projectSlug,
                    type: clickType
                })
            });

            if (!response.ok) {
                console.error('Failed to track click');
                return false;
            }

            return true;
        } catch (error) {
            console.error('Error tracking click:', error);
            return false;
        }
    }

    bindProjectLinks() {
        document.querySelectorAll('[data-track-click]').forEach(element => {
            element.addEventListener('click', async (e) => {
                const projectSlug = element.dataset.projectSlug;
                const clickType = element.dataset.clickType;

                if (projectSlug && clickType) {
                    // Don't prevent default, track in background
                    this.trackClick(projectSlug, clickType);
                }
            });
        });
    }

    async getFilterData() {
        try {
            const response = await fetch('/api/filter-data/');
            if (!response.ok) {
                throw new Error('Failed to fetch filter data');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching filter data:', error);
            return null;
        }
    }

    initialize() {
        if (this.initialized) return;
        
        this.bindProjectLinks();
        this.initialized = true;
    }
}

// Initialize globally
window.projectMetrics = new ProjectMetrics();
document.addEventListener('DOMContentLoaded', () => {
    window.projectMetrics.initialize();
});