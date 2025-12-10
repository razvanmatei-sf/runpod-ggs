// ABOUTME: Main JavaScript for SF AI Workbench
// ABOUTME: Handles modals, navigation, and common interactions

document.addEventListener('DOMContentLoaded', function() {
    // Modal handling
    const moreBtn = document.getElementById('more-btn');
    const moreModal = document.getElementById('more-modal');
    const helpBtn = document.getElementById('help-btn');
    const helpModal = document.getElementById('help-modal');

    // Open More modal
    if (moreBtn && moreModal) {
        moreBtn.addEventListener('click', function() {
            moreModal.classList.add('active');
        });
    }

    // Open Help modal
    if (helpBtn && helpModal) {
        helpBtn.addEventListener('click', function() {
            helpModal.classList.add('active');
        });
    }

    // Close modals when clicking overlay
    document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });

    // Close modals with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(function(modal) {
                modal.classList.remove('active');
            });
        }
    });

    // Handle JupyterLab launch from More modal
    const jupyterBtn = document.querySelector('[data-tool="jupyter-lab"]');
    if (jupyterBtn) {
        jupyterBtn.addEventListener('click', function() {
            fetch('/start/jupyter-lab', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'started' || data.status === 'already_running') {
                        // Get runpod ID from page or use localhost
                        const runpodId = document.body.dataset.runpodId;
                        const port = 8888;
                        if (runpodId) {
                            window.open('https://' + runpodId + '-' + port + '.proxy.runpod.net/', '_blank');
                        } else {
                            window.open('http://localhost:' + port, '_blank');
                        }
                    }
                    // Close modal
                    if (moreModal) {
                        moreModal.classList.remove('active');
                    }
                });
        });
    }
});
