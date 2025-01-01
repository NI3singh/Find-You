# Face Recognition Web Application

This is a Flask-based web application for face recognition. Users can upload or capture photos to find matched faces from a dataset. The app also provides options to download all matched photos as a zip file.

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Setup Requirements](#setup-requirements)
4. [Model Installation Steps](#model-installation-steps)
5. [How to Run the Application](#how-to-run-the-application)
6. [Usage](#usage)
7. [Contributing](#contributing)

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
4. Retinface and Facenet Installed

---

## Model Installation
1.For Downlaoding Resnet model, go to the given repo link "https://github.com/ageitgey/face_recognition_models/blob/master/face_recognition_models/models/dlib_face_recognition_resnet_model_v1.dat"
2. Tap on "View raw" or Downlaod button.
3. For Downloading shape_predictor dlib model, go to the given repo link
"https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat"
4. Tap on "View raw" or Download button.

---

## How to Run the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd frontend
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

- Launch the application
- Upload all event images at once
- tap on Generate Button after Successfull Upload
- Then copy the generated link
- open in new tab/device/window
- provide the permissions
- take a selfie/picture
- tap on find my photos
- The application will process the image and perform face detection and recognition.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.
