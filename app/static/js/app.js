document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navLinks = document.querySelectorAll('.sidebar nav a');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const pageId = link.getAttribute('data-page');
            pages.forEach(p => p.classList.add('hidden'));
            
            const activePage = document.getElementById(`${pageId}-page`);
            if(activePage) activePage.classList.remove('hidden');
        });
    });

    // Dashboard Data
    async function loadDashboardData() {
        try {
            const statsRes = await fetch('/api/statistics');
            const stats = await statsRes.json();
            
            document.getElementById('stat-total').textContent = stats.total_detections || 0;
            document.getElementById('stat-alerts').textContent = stats.total_alerts || 0;
            document.getElementById('stat-people').textContent = stats.people_detected || 0;
            document.getElementById('stat-fire').textContent = (stats.violations.FIRE || 0) + (stats.violations.SMOKE || 0);

            // Recent Detections
            const detRes = await fetch('/api/detections/recent?limit=5');
            const detections = await detRes.json();
            const detTbody = document.querySelector('#recent-detections tbody');
            detTbody.innerHTML = detections.map(d => `
                <tr>
                    <td>#${d.id}</td>
                    <td>${d.label}</td>
                    <td>${(d.confidence * 100).toFixed(1)}%</td>
                    <td>${new Date(d.timestamp).toLocaleTimeString()}</td>
                </tr>
            `).join('');

            // Recent Alerts (Dashboard)
            const alertRes = await fetch('/api/alerts/recent?limit=5');
            const alerts = await alertRes.json();
            const alertTbody = document.querySelector('#recent-alerts tbody');
            alertTbody.innerHTML = alerts.map(a => `
                <tr>
                    <td>${a.alert_type}</td>
                    <td><span style="color: ${a.severity === 'CRITICAL' ? 'var(--accent-red)' : 'var(--accent-orange)'}">${a.severity}</span></td>
                    <td>${new Date(a.timestamp).toLocaleTimeString()}</td>
                </tr>
            `).join('');

            // Full History (History Page)
            const fullDetRes = await fetch('/api/detections/recent?limit=50');
            const fullDetections = await fullDetRes.json();
            const historyTbody = document.querySelector('#history-table tbody');
            if(historyTbody) {
                historyTbody.innerHTML = fullDetections.map(d => `
                    <tr>
                        <td>#${d.id}</td>
                        <td>${d.label}</td>
                        <td>${(d.confidence * 100).toFixed(1)}%</td>
                        <td>${new Date(d.timestamp).toLocaleString()}</td>
                        <td><span style="color: ${d.violation ? 'var(--accent-red)' : 'var(--accent-green)'}">${d.violation ? 'Yes' : 'No'}</span></td>
                    </tr>
                `).join('');
            }

            // Full Alerts (Alerts Page)
            const fullAlertRes = await fetch('/api/alerts/recent?limit=50');
            const fullAlerts = await fullAlertRes.json();
            const fullAlertTbody = document.querySelector('#alerts-table tbody');
            if(fullAlertTbody) {
                fullAlertTbody.innerHTML = fullAlerts.map(a => `
                    <tr>
                        <td>${a.alert_type}</td>
                        <td><span style="color: ${a.severity === 'CRITICAL' ? 'var(--accent-red)' : 'var(--accent-orange)'}">${a.severity}</span></td>
                        <td>${a.message || 'Alert Triggered'}</td>
                        <td>${new Date(a.timestamp).toLocaleString()}</td>
                    </tr>
                `).join('');
            }

        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    // Load initial data
    loadDashboardData();
    setInterval(loadDashboardData, 5000); // Poll every 5 seconds

    // Image Upload Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const btnDetect = document.getElementById('btn-detect');
    const btnReupload = document.getElementById('btn-reupload');
    const resultsDiv = document.getElementById('detection-results');
    
    let currentFile = null;

    dropZone.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        if(e.target.files.length) {
            currentFile = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                dropZone.style.display = 'none';
                previewArea.style.display = 'block';
                resultsDiv.style.display = 'none';
            };
            reader.readAsDataURL(currentFile);
        }
    });

    if (btnReupload) {
        btnReupload.addEventListener('click', () => {
            currentFile = null;
            fileInput.value = '';
            imagePreview.src = '';
            dropZone.style.display = '';
            previewArea.style.display = 'none';
            resultsDiv.style.display = 'none';
        });
    }

    btnDetect.addEventListener('click', async () => {
        if(!currentFile) return;
        
        btnDetect.textContent = 'Processing...';
        btnDetect.disabled = true;

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const res = await fetch('/api/detect-image', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            document.getElementById('objects-list').innerHTML = data.detections.map(d => 
                `<li>${d.label} - ${(d.confidence*100).toFixed(1)}%</li>`
            ).join('') || '<li>No objects detected</li>';

            document.getElementById('violations-list').innerHTML = data.violations.map(v => 
                `<li>[${v.severity}] ${v.type}: ${v.message}</li>`
            ).join('') || '<li>No violations detected</li>';

            resultsDiv.style.display = 'block';
        } catch(err) {
            alert("Error processing image.");
        } finally {
            btnDetect.textContent = 'Run Detection';
            btnDetect.disabled = false;
        }
    });
});
