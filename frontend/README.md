# README.md content

# Face Recognition Web Application

This is a Flask-based web application for face recognition. Users can upload or capture photos to find matched faces from a dataset. The app also provides options to download all matched photos as a zip file.

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Setup Requirements](#setup-requirements)
4. [Installation Steps](#installation-steps)
5. [How to Run the Application](#how-to-run-the-application)
6. [Using HTTPS with Ngrok](#using-https-with-ngrok)
7. [Folder Structure](#folder-structure)
8. [Screenshots](#screenshots)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

---

## Features
- Capture or upload a photo for face recognition.
- Preview the captured photo before processing.
- Identify matched photos from a dataset.
- Download all matched photos as a zip file.
- Secure HTTPS access using Ngrok.

---

## Technologies Used
- **Backend**: Python(Flask)
- **Frontend**: HTML, CSS, JavaScript
- **Face Recognition**: Dlib, Resnet
- **Database**: SQLite

---

## Setup Requirements
1. Python 3.7+
2. Virtual environment (`venv`)
3. Ngrok (for HTTPS)
4. Dlib and OpenCV installed
5. Shape predictor and face recognition models:
   - `shape_predictor_68_face_landmarks.dat`
   - `dlib_face_recognition_resnet_model_v1.dat`

---

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd frontend
   ```
2. Install the required dependencies:
   ```
   pip install retina-face
   ```
2. Install the required dependencies:
   ```
   pip install facenet-pytorch
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

4. Open your web browser and go to `http://127.0.0.1:5000` to access the application.

## Usage

- Upload an image or use the camera to capture an image.
- The application will process the image and perform face detection and recognition.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.