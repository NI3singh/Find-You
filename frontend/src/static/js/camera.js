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
    const uploadPhotoBtn = document.getElementById('upload-photo-btn');
    const uploadPhotoInput = document.getElementById('upload-photo-input');

    let stream = null;

    acceptBtn.addEventListener('click', async () => {
        consentSection.hidden = true;
        cameraSection.hidden = false;

        try {
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
            alert(
                'Unable to access your camera. Please ensure camera permissions are enabled and you are using HTTPS or localhost.'
            );
            cameraSection.hidden = true;
            consentSection.hidden = false;
        }
    });

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

    retakeBtn.addEventListener('click', () => {
        video.hidden = false;
        captureBtn.hidden = false;
        previewSection.hidden = true;
        retakeBtn.hidden = true;
    });

    findPhotosBtn.addEventListener('click', async () => {
        const imageData = canvas.toDataURL('image/jpeg').split(',')[1];
        const eventId = getEventIdFromUrl();

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

    uploadPhotoBtn.addEventListener('click', () => {
        uploadPhotoInput.click();
    });

    uploadPhotoInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('event_id', getEventIdFromUrl());

            try {
                cameraSection.hidden = true;
                loadingSection.hidden = false;

                const response = await fetch('/api/find_photos', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error('Failed to upload photo');
                }

                const data = await response.json();
                if (data.resultId) {
                    window.location.href = `/result/${data.resultId}`;
                } else {
                    alert('No matching photos found.');
                }
            } catch (error) {
                console.error('Error uploading photo:', error);
                alert('An error occurred while uploading the photo.');
            } finally {
                loadingSection.hidden = true;
                cameraSection.hidden = false;
            }
        }
    });

    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    function getEventIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }
});