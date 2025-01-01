document.addEventListener('DOMContentLoaded', () => {
    const photosGrid = document.getElementById('photos-grid');
    const noPhotos = document.getElementById('no-photos');
    const downloadAllBtn = document.getElementById('download-all-btn');
    const loadingSpinner = document.getElementById('loading-spinner');

    async function loadPhotos() {
        try {
            const resultId = getResultIdFromUrl();
            const response = await fetch(`/api/result/${resultId}`);

            if (!response.ok) {
                throw new Error('Failed to load photos');
            }

            const data = await response.json();

            if (!data.photos || data.photos.length === 0) {
                noPhotos.hidden = false;  // Show "no photos" section
                photosGrid.hidden = true; // Hide photos grid
                downloadAllBtn.hidden = true; // Hide download button
                return;
            }

            noPhotos.hidden = true;  // Hide "no photos" section
            photosGrid.hidden = false; // Show photos grid
            renderPhotos(data.photos);
            downloadAllBtn.hidden = false;
        } catch (error) {
            console.error('Error loading photos:', error);
            alert('Failed to load photos. Please try again.');
        } finally {
            loadingSpinner.hidden = true;
        }
    }


    function renderPhotos(photos) {
        photosGrid.innerHTML = photos.map(photo => `
            <div class="photo-item">
                <img src="data:image/jpeg;base64,${photo.data}" alt="${photo.name}">
                <div class="photo-actions">
                    <button onclick="downloadPhoto('${photo.name}', '${photo.data}')">Download</button>
                </div>
            </div>
        `).join('');
    }
    

    window.downloadPhoto = (imageName, imageData) => {
        try {
            const a = document.createElement('a');
            const blob = new Blob([Uint8Array.from(atob(imageData), c => c.charCodeAt(0))], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);
            a.href = url;
            a.download = imageName;
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error downloading photo:', error);
            alert('Failed to download photo. Please try again.');
        }
    };

    downloadAllBtn.addEventListener('click', async () => {
        try {
            const resultId = getResultIdFromUrl();
            const response = await fetch(`/api/result/${resultId}/download`);
            if (!response.ok) {
                throw new Error('Failed to download photos');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'matched_photos.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error downloading all photos:', error);
            alert('Failed to download photos. Please try again.');
        }
    });

    function getResultIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    loadPhotos();
});
