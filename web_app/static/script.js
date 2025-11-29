document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const resultSection = document.getElementById('result-section');
    const canvas = document.getElementById('result-canvas');
    const ctx = canvas.getContext('2d');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resetBtn = document.getElementById('reset-btn');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    resetBtn.addEventListener('click', () => {
        resultSection.style.display = 'none';
        resetBtn.style.display = 'none';
        dropZone.style.display = 'block';
        fileInput.value = '';

        document.getElementById('medical-report').style.display = 'none';
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }

        dropZone.style.display = 'none';
        resultSection.style.display = 'block';
        loadingOverlay.style.display = 'flex';
        resetBtn.style.display = 'none';

        const img = new Image();
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            uploadAndPredict(file, img.width, img.height);
        };
        img.src = URL.createObjectURL(file);
    }

    async function uploadAndPredict(file, width, height) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Prediction failed');

            const data = await response.json();
            
            // 1. Disegna i box rossi (codice vecchio)
            drawBoxes(data.boxes, data.scores);

            // 2. Gestione del Report Medico (CODICE NUOVO)
            // ---------------------------------------------------------
            const reportBox = document.getElementById('medical-report');
            const reportTitle = document.getElementById('report-title');
            const reportText = document.getElementById('report-text');

            if (data.report) {
                // Rendi visibile il box del report
                reportBox.style.display = 'block';

                // Inserisci il titolo e il testo ricevuti da Python
                reportTitle.textContent = data.report.titolo;
                reportText.textContent = data.report.testo;

                // Cambia i colori in base alla gravità (Rosso o Verde)
                reportTitle.style.color = data.report.colore;
                reportBox.style.borderLeftColor = data.report.colore;
            }
            // ---------------------------------------------------------

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during analysis.');
        } finally {
            loadingOverlay.style.display = 'none';
            resetBtn.style.display = 'inline-block';
        }
    }
    function drawBoxes(boxes, scores) {
        ctx.lineWidth = 4;
        ctx.font = '24px Arial';

        boxes.forEach((box, i) => {
            const [x1, y1, x2, y2] = box;
            const score = scores[i];

            ctx.strokeStyle = 'rgba(239, 68, 68, 0.9)';
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            const text = `Pneumonia ${(score * 100).toFixed(1)}%`;
            const textWidth = ctx.measureText(text).width;

            ctx.fillStyle = 'rgba(239, 68, 68, 0.9)';
            ctx.fillRect(x1, y1 - 30, textWidth + 10, 30);

            ctx.fillStyle = 'white';
            ctx.fillText(text, x1 + 5, y1 - 7);
        });

        if (boxes.length === 0) {
            ctx.fillStyle = 'rgba(16, 185, 129, 0.9)';
            ctx.fillRect(20, 20, 160, 50);

            ctx.fillStyle = 'white';
            ctx.font = 'bold 30px Arial';
            ctx.fillText('Healthy', 35, 55);
        }
    }
});
