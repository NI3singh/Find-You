
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
    const passwordModal = document.getElementById('password-modal');
    const passwordInput = document.getElementById('password-input');
    const submitPasswordBtn = document.getElementById('submit-password-btn');
    const passwordError = document.getElementById('password-error');

    let stream = null;
    let confirmedMobileNumber = '';
    let toleranceValue = 0.6;

    captureBtn.disabled = true;
    uploadPhotoBtn.disabled = true;
    cameraSection.hidden = true; // Show the camera section
    consentSection.hidden = true;

    submitPasswordBtn.addEventListener('click', async () => {
        const password = passwordInput.value.trim();
        const eventId = window.location.pathname.split('/').pop(); // Extract event_id from URL
    
        if (!password) {
            passwordError.textContent = 'Please enter a password.';
            passwordError.style.display = 'block';
            return;
        }
    
        try {
            const response = await fetch('/api/validate_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ event_id: eventId, password }),
            });
    
            if (response.ok) {
                const data = await response.json();
                // Password validated, hide modal and enable buttons
                passwordModal.style.display = 'none';
                passwordError.style.display = 'none'; // Hide any previous error
                consentSection.hidden = false; // Show the consent section
            } else {
                const errorData = await response.json();
                passwordError.textContent = errorData.error || 'Invalid password. Please try again.';
                passwordError.style.display = 'block';
            }
        } catch (error) {
            console.error('Error validating password:', error);
            passwordError.textContent = 'An error occurred. Please try again.';
            passwordError.style.display = 'block';
        }
    });
    

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
    // captureBtn.addEventListener('click', async () => {
    //     canvas.width = video.videoWidth;
    //     canvas.height = video.videoHeight;
    //     canvas.getContext('2d').drawImage(video, 0, 0);

    //     const imageData = canvas.toDataURL('image/jpeg');
    //     capturedImage.src = imageData;
    //     video.hidden = true;
    //     captureBtn.hidden = true;
    //     previewSection.hidden = false;
    //     retakeBtn.hidden = false;

    //     // Show confirmed mobile number in preview
    //     displayMobileNumber.textContent = confirmedMobileNumber;

    //     // Upload the captured image
    //     await uploadImage(imageData);
    // });

    captureBtn.addEventListener('click', async () => {
        try {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
    
            const imageData = canvas.toDataURL('image/jpeg');
            capturedImage.src = imageData;
            
            // Show loading state
            captureBtn.disabled = true;
            loadingSection.hidden = false;
    
            // Upload with better error handling
            await uploadImage(imageData, confirmedMobileNumber);
    
            // Update UI on success
            video.hidden = true;
            captureBtn.hidden = true;
            previewSection.hidden = false;
            retakeBtn.hidden = false;
            displayMobileNumber.textContent = confirmedMobileNumber;
    
        } catch (error) {
            alert(error.message || 'Failed to upload image. Please try again.');
        } finally {
            captureBtn.disabled = false;
            loadingSection.hidden = true;
        }
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
    // async function uploadImage(imageData) {
    //     try {
    //         // Convert base64 to a Blob
    //         const blob = await fetch(imageData).then((res) => res.blob());

    //         // Create FormData and append the Blob
    //         const formData = new FormData();
    //         formData.append('image', blob, 'temp_selfie.png');

    //         // Send the image to the server
    //         const response = await fetch('/api/upload_photo', {
    //             method: 'POST',
    //             body: formData,
    //         });

    //         if (!response.ok) {
    //             throw new Error('Failed to upload image');
    //         }

    //         console.log('Image uploaded successfully.');
    //     } catch (error) {
    //         console.error('Error uploading image:', error);
    //         alert('An error occurred while uploading the image.');
    //     }
    // }

    async function uploadImage(imageData, mobileNumber) {
        try {
            // Validate inputs
            if (!imageData) {
                throw new Error('No image data provided');
            }
    
            // Convert base64 to a Blob if imageData is base64
            let imageBlob;
            if (typeof imageData === 'string' && imageData.startsWith('data:image')) {
                try {
                    imageBlob = await fetch(imageData).then(res => res.blob());
                } catch (error) {
                    throw new Error(`Failed to convert base64 to blob: ${error.message}`);
                }
            } else if (imageData instanceof Blob) {
                imageBlob = imageData;
            } else {
                throw new Error('Invalid image format provided');
            }
    
            // Validate file size (e.g., 10MB limit)
            const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
            if (imageBlob.size > MAX_FILE_SIZE) {
                throw new Error('Image file is too large (max 10MB)');
            }
    
            // Create and validate FormData
            const formData = new FormData();
            formData.append('image', imageBlob, 'temp_selfie.png');
            if (mobileNumber) {
                formData.append('mobile_number', mobileNumber);
            }
    
            // Send request with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
            const response = await fetch('/api/upload_photo', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
    
            clearTimeout(timeoutId);
    
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server responded with ${response.status}: ${errorText}`);
            }
    
            const result = await response.json();
            console.log('Image uploaded successfully:', result);
            return result;
    
        } catch (error) {
            // Specific error handling
            if (error.name === 'AbortError') {
                console.error('Upload timed out after 30 seconds');
                throw new Error('Upload timed out. Please try again.');
            }
            
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                console.error('Network error during upload:', error);
                throw new Error('Network error. Please check your connection and try again.');
            }
    
            console.error('Error uploading image:', {
                message: error.message,
                stack: error.stack,
                timestamp: new Date().toISOString()
            });
    
            throw error; // Re-throw to be handled by calling function
        }
    }
    
});     