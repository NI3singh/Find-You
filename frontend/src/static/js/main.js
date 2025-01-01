document.addEventListener('DOMContentLoaded', () => {
    const dragDropArea = document.getElementById('drag-drop-area');
    const fileInput = document.getElementById('file-input');
    const selectFilesBtn = document.getElementById('select-files-btn');
    const uploadForm = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const generateBtn = document.getElementById('generate-btn'); // Generate button
    const previewContainer = document.getElementById('preview-container');
    const shareSection = document.getElementById('share-section');
    const shareLink = document.getElementById('share-link');
    const copyLinkBtn = document.getElementById('copy-link-btn');
    const progressBar = document.getElementById('upload-progress-bar');
    const uploadStatus = document.getElementById('upload-status');

    const modal = document.getElementById('eventModal'); // Modal element
    const closeModal = document.getElementById('closeModal');
    const cancelButton = document.getElementById('cancelButton');
    const confirmButton = document.getElementById('confirmButton');
    const eventNameInput = document.getElementById('eventNameInput');

    let selectedFiles = [];

    // Drag and drop handlers
    dragDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragDropArea.classList.add('dragover');
    });

    dragDropArea.addEventListener('dragleave', () => {
        dragDropArea.classList.remove('dragover');
    });

    dragDropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dragDropArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        handleFiles(files);
    });

    selectFilesBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });

    function handleFiles(files) {
        const maxFileSize = 10 * 1024 * 1024; // 10MB per file
        const validFiles = [];

        for (const file of files) {
            if (file.size > maxFileSize) {
                alert(`File ${file.name} is too large. Maximum size is 10MB per file.`);
                continue;
            }
            if (!file.type.startsWith('image/')) {
                alert(`File ${file.name} is not an image.`);
                continue;
            }
            validFiles.push(file);
        }

        selectedFiles = [...selectedFiles, ...validFiles];
        updatePreview();
        uploadBtn.disabled = selectedFiles.length === 0;
    }

    function updatePreview() {
        previewContainer.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.className = 'preview-item';
                preview.innerHTML = `
                    <img src="${e.target.result}" class="preview-image" alt="Preview">
                    <button type="button" class="remove-btn" data-index="${index}">×</button>
                `;
                previewContainer.appendChild(preview);
            };
            reader.readAsDataURL(file);
        });
    }

    // Remove preview image
    previewContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-btn')) {
            const index = parseInt(e.target.dataset.index);
            selectedFiles = selectedFiles.filter((_, i) => i !== index);
            updatePreview();
            uploadBtn.disabled = selectedFiles.length === 0;
        }
    });

    // Show modal on upload button click
    uploadBtn.addEventListener('click', (e) => {
        e.preventDefault(); // Prevent form submission
        modal.style.display = 'block'; // Show the modal
    });

    generateBtn.addEventListener('click', async () => {
        const eventId = generateBtn.getAttribute('data-event-id');
        if (!eventId) {
            alert("Event ID not found. Please ensure you have completed the upload.");
            return;
        }
    
        // Show the loader
        const loader = document.getElementById('loader');
        loader.style.display = 'block';
    
        try {
            const response = await fetch('/api/generate_faces', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ event_id: eventId }),
            });
    
            if (!response.ok) {
                throw new Error('Failed to generate faces.');
            }
    
            const data = await response.json();
            alert(`Face processing started for Event ID: ${data.event_id}`);
    
            // Update the sharable link with the event_id
            const shareLinkInput = document.getElementById('share-link');
            shareLinkInput.value = data.share_link;
    
            // Make the share link section visible
            const shareSection = document.getElementById('share-section');
            shareSection.hidden = false;
    
        } catch (error) {
            console.error('Error generating faces:', error);
            alert('Failed to start face processing. Please try again.');
        } finally {
            loader.style.display = 'none';
        }
    });
    

    // Close modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    cancelButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    confirmButton.addEventListener('click', async () => {
        const eventName = eventNameInput.value.trim();
        if (!eventName) {
            alert("Event name cannot be empty!");
            return;
        }

        try {
            const checkResponse = await fetch('/api/check_event_name', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ event_name: eventName }),
            });

            const checkData = await checkResponse.json();

            if (checkData.exists) {
                if (confirm(`Event name "${eventName}" already exists. Do you want to add images to this event?`)) {
                    const formData = new FormData();
                    formData.append('event_id', checkData.event_id);
                    selectedFiles.forEach((file) => {
                        formData.append('images', file);
                    });

                    const addResponse = await fetch('/api/add_to_existing_event', {
                        method: 'POST',
                        body: formData,
                    });

                    if (addResponse.ok) {
                        alert("Images added to the existing event successfully!");
                        modal.style.display = 'none';
                        return;
                    } else {
                        const addError = await addResponse.json();
                        alert(`Error: ${addError.error}`);
                    }
                } else {
                    alert("Please enter a new event name.");
                    return;
                }
            } else {
                const formData = new FormData();
                formData.append('event_name', eventName);
                selectedFiles.forEach((file) => {
                    formData.append('images', file);
                });

                const uploadResponse = await fetch('/api/upload_event', {
                    method: 'POST',
                    body: formData,
                });

                if (uploadResponse.ok) {
                    const uploadData = await uploadResponse.json();
                    alert("Event uploaded successfully!");
                    generateBtn.disabled = false; // Enable Generate button
                    generateBtn.style.cursor = "pointer";
                    generateBtn.style.backgroundColor = "#28a745";
                    generateBtn.setAttribute('data-event-id', uploadData.event_id);
                } else {
                    alert("Failed to upload event!");
                }
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error checking event name.");
        }

        modal.style.display = 'none';
    });

    // Copy share link
    copyLinkBtn.addEventListener('click', () => {
        shareLink.select();
        document.execCommand('copy');
        copyLinkBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyLinkBtn.textContent = 'Copy Link';
        }, 2000);
    });
});
