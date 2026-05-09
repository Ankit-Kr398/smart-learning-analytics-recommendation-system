// charts.js
// Runs after the dashboard template injects
// subjectLabels, subjectScores, placementScore,
// consistencyScore, overallScore into the page.

document.addEventListener('DOMContentLoaded', function () {

    // Guard: only run on dashboard where these variables exist
    if (typeof subjectLabels === 'undefined') return;

    // ── SUBJECT BAR CHART ────────────────────────
    const subjectCtx = document.getElementById('subjectChart');
    if (subjectCtx) {
        new Chart(subjectCtx, {
            type: 'bar',
            data: {
                labels: subjectLabels,
                datasets: [{
                    label: 'Health Score',
                    data: subjectScores,
                    backgroundColor: subjectScores.map(score =>
                        score >= 70 ? 'rgba(34,197,94,0.7)' :
                        score >= 40 ? 'rgba(234,179,8,0.7)' :
                                      'rgba(239,68,68,0.7)'
                    ),
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { color: '#1f2937' }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: '#9ca3af' },
                        grid: { color: '#1f2937' }
                    }
                }
            }
        });
    }

    // ── SCORE DONUT CHART ────────────────────────
    const donutCtx = document.getElementById('scoreDonut');
    if (donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Placement', 'Consistency', 'Remaining'],
                datasets: [{
                    data: [
                        placementScore,
                        consistencyScore,
                        Math.max(0, 100 - overallScore)
                    ],
                    backgroundColor: [
                        'rgba(99,102,241,0.8)',
                        'rgba(34,197,94,0.8)',
                        'rgba(30,30,50,0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#9ca3af', padding: 12 }
                    }
                }
            }
        });
    }
});