document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const acceptBtn = document.getElementById('accept-btn');
    const cameraSection = document.getElementById('camera-section');
    const consentSection = document.getElementById('consent-section');
    const captureBtn = document.getElementById('capture-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const previewSection = document.getElementById('preview-section');
    const capturedImage = document.getElementById('captured-image');
    const findPhotosBtn = document.getElementById('find-photos-btn');
    const loadingSection = document.getElementById('loading-section');

    let stream = null;

    // Handle consent and camera initialization
    acceptBtn.addEventListener('click', async () => {
        consentSection.hidden = true;
        cameraSection.hidden = false;

        try {
            // Request camera access
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
            });
            video.srcObject = stream;
            captureBtn.disabled = false;
        } catch (err) {
            console.error('Error accessing camera:', err);

            // Show permission pop-up
            alert(
                'Unable to access your camera. Please ensure that:\n' +
                '1. You have allowed camera permissions in your browser.\n' +
                '2. The browser has access to your camera.\n' +
                '3. You are accessing this website via HTTPS or localhost.'
            );

            // Re-enable the consent section
            cameraSection.hidden = true;
            consentSection.hidden = false;
        }
    });

    // Capture photo
    captureBtn.addEventListener('click', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        capturedImage.src = canvas.toDataURL('image/jpeg');
        video.hidden = true;
        captureBtn.hidden = true;
        previewSection.hidden = false;
        retakeBtn.hidden = false;
    });

    // Retake photo
    retakeBtn.addEventListener('click', () => {
        video.hidden = false;
        captureBtn.hidden = false;
        previewSection.hidden = true;
        retakeBtn.hidden = true;
    });

    // Find photos
    findPhotosBtn.addEventListener('click', async () => {
        const imageData = canvas.toDataURL('image/jpeg').split(',')[1];
        const eventId = getEventIdFromUrl(); // Function to extract event_id from URL

        try {
            cameraSection.hidden = true;
            loadingSection.hidden = false;

            const response = await fetch('/api/find_photos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    event_id: eventId,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to find photos');
            }

            const data = await response.json();
            if (data.resultId) {
                window.location.href = `/result/${data.resultId}`;
            } else {
                throw new Error('No resultId found in response');
            }
        } catch (error) {
            console.error('Error finding photos:', error);
            alert('Failed to process your photo. Please try again.');
            loadingSection.hidden = true;
            cameraSection.hidden = false;
        }
    });

    // Cleanup when the user leaves the page
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    function getEventIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1]; // Assumes URL ends with the event_id
    }
});
