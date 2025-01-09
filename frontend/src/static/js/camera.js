
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
    const mobileNumberInput = document.getElementById('mobile-number');
    const confirmNumberBtn = document.getElementById('confirm-number-btn');
    const displayMobileNumber = document.getElementById('display-mobile-number');
    const updatetolerancebtn = document.getElementById('update-tolerance-btn');
    const toleranceInput = document.getElementById('tolerance');

    let stream = null;
    let confirmedMobileNumber = '';
    let toleranceValue = 0.6;

    captureBtn.disabled = true;
    uploadPhotoBtn.disabled = true;

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
            // captureBtn.disabled = false;
        } catch (err) {
            console.error('Error accessing camera:', err);
            alert(
                'Unable to access your camera. Please ensure camera permissions are enabled and you are using HTTPS or localhost.'
            );
            cameraSection.hidden = true;
            consentSection.hidden = false;
        }
    });

    // Validate and confirm mobile number
    mobileNumberInput.addEventListener('input', () => {
        const isValid = /^[0-9]{10}$/.test(mobileNumberInput.value); // Check if it's a valid 10-digit number
        confirmNumberBtn.disabled = !isValid;
    });

    toleranceInput.addEventListener('input', () => {
        const isValid = parseFloat(toleranceInput.value) >= 0 && parseFloat(toleranceInput.value) <= 1;
        updatetolerancebtn.disabled = !isValid;
    });

    updatetolerancebtn.addEventListener('click', () => {
        toleranceValue = parseFloat(toleranceInput.value);
        if (toleranceValue >= 0 && toleranceValue <= 1) {
            alert(`Tolerance updated to ${toleranceValue}`);
        } else {
            alert('Please enter a valid tolerance value between 0.0 and 1.0.');
        }
    });

    confirmNumberBtn.addEventListener('click', () => {
        confirmedMobileNumber = mobileNumberInput.value.trim();
        if (confirmedMobileNumber) {
            alert('Mobile number confirmed!');
            captureBtn.disabled = false;
            uploadPhotoBtn.disabled = false;
            mobileNumberInput.disabled = true; // Disable input after confirmation
            confirmNumberBtn.disabled = true; // Disable confirm button
        }
    });

    // Capture photo logic
    captureBtn.addEventListener('click', async () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        const imageData = canvas.toDataURL('image/jpeg');
        capturedImage.src = imageData;
        video.hidden = true;
        captureBtn.hidden = true;
        previewSection.hidden = false;
        retakeBtn.hidden = false;

        // Show confirmed mobile number in preview
        displayMobileNumber.textContent = confirmedMobileNumber;

        // Upload the captured image
        await uploadImage(imageData);
    });

    retakeBtn.addEventListener('click', () => {
        video.hidden = false;
        captureBtn.hidden = false;
        previewSection.hidden = true;
        retakeBtn.hidden = true;
    });

    // Upload photo logic
    uploadPhotoBtn.addEventListener('click', () => {
        uploadPhotoInput.click();
    });

    uploadPhotoInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    // Preview the uploaded image
                    capturedImage.src = e.target.result;

                    // Prepare the form data for uploading the image
                    const formData = new FormData();
                    formData.append('image', file);
                    formData.append('mobile_number', confirmedMobileNumber);

                    // Display loading screen while processing
                    cameraSection.hidden = true;
                    loadingSection.hidden = false;

                    // Call the API to save the uploaded photo as temp_selfie.png
                    const uploadResponse = await fetch('/api/upload_photo', {
                        method: 'POST',
                        body: formData,
                    });

                    if (!uploadResponse.ok) {
                        throw new Error('Failed to upload and save the photo');
                    }

                    console.log('Photo uploaded successfully.');

                    // After successful upload, trigger find_photos API
                    const findPhotosResponse = await fetch('/api/find_photos', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            event_id: getEventIdFromUrl(),
                            mobile_number: confirmedMobileNumber,
                            tolerance: toleranceValue, // Include tolerance value
                        }),
                    });

                    if (!findPhotosResponse.ok) {
                        throw new Error('Failed to find photos');
                    }

                    const data = await findPhotosResponse.json();
                    if (data.resultId) {
                        const mobileNumber = confirmedMobileNumber; // Use the confirmed mobile number
                        window.location.href = `/result/${data.resultId}?mobile_number=${mobileNumber}`;
                    } else {
                        alert('No matching photos found.');
                    }
                } catch (error) {
                    console.error('Error uploading and processing photo:', error);
                    alert('An error occurred while uploading and processing the photo.');
                } finally {
                    // Clear the file input and reset UI
                    uploadPhotoInput.value = ''; // Clear the file input to avoid caching issues
                    loadingSection.hidden = true;
                    cameraSection.hidden = false;
                }
            };

            // Read the file as a data URL
            reader.readAsDataURL(file);
        }
    });

    // Find photos logic
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
                    event_id: eventId,
                    mobile_number: confirmedMobileNumber, // Send mobile number to backend
                    tolerance: toleranceValue,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to find photos');
            }

            const data = await response.json();
            if (data.resultId) {
                const mobileNumber = confirmedMobileNumber; // Use the confirmed mobile number
                window.location.href = `/result/${data.resultId}?mobile_number=${mobileNumber}`;
            }
             else {
                throw new Error('No resultId found in response');
            }
        } catch (error) {
            console.error('Error finding photos:', error);
            alert('Failed to process your photo. Please try again.');
            loadingSection.hidden = true;
            cameraSection.hidden = false;
        }
    });

    // Cleanup media stream on page unload
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    function getEventIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    // Upload image function
    async function uploadImage(imageData) {
        try {
            // Convert base64 to a Blob
            const blob = await fetch(imageData).then((res) => res.blob());

            // Create FormData and append the Blob
            const formData = new FormData();
            formData.append('image', blob, 'temp_selfie.png');

            // Send the image to the server
            const response = await fetch('/api/upload_photo', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload image');
            }

            console.log('Image uploaded successfully.');
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('An error occurred while uploading the image.');
        }
    }
});