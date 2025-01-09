# README.md content

# Face Recognition Web Application

This is a Flask-based web application for face recognition. Users can upload or capture photos to find matched faces from a dataset. The app also provides options to download all matched photos as a zip file.

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Setup Requirements](#setup-requirements)
4. [How to Run the Application](#how-to-run-the-application)
5. [Using HTTPS with Ngrok](#using-https-with-ngrok)
6. [Directory Structure](#directory-structure)
7. [Screenshots](#screenshots)
8. [Usage](#usage)
9. [Contributing](#contributing)

---

## Features
- Capture or upload a photo for face recognition.
- Preview the captured photo before processing.
- Identify matched photos from a dataset.
- Download all matched photos as a zip file.
- Secure HTTPS access using Ngrok.
- Authorized access only by "Password-Protected-Link".
- Only Admin access for Event Creation and Images Uplaod.

## Technologies Used
- **Backend**: Python(Flask)
- **Frontend**: HTML, CSS, JavaScript
- **Face Recognition**: RetinaFace, Facenet
- **Database**: SQLite

---

## Setup Requirements
1. Python 3.7+
2. Virtual environment (`venv`)
3. Ngrok (for HTTPS)
4. RetinaFace and Facenet installed

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

3. Run User Database File for creating a Login-id and Password you can configure as per your choice in init_db.py:
   ```
   python init_db.py
   ```

4. Run the application:
   ```
   python src/app.py
   ```

5. Open your web browser and go to `http://127.0.0.1:5000` to access the application.


## Using HTTPS with Ngrok
1. Create account on Ngrok
2. Install the .exe application in your device
3. Go to Setup&Installation Menu on Ngrok Website
3. Now open cmd in Administrator mode
4. Copy ngrok.yml command and Paste in cmd
5. Now run the application in your IDE (e.g Vscode)
6. Now copy deploy command from Ngrok website
7. Paste it on opened cmd and update the port number with your port number
   ```
   example: ngrok http http://localhost:8080 --> ngrok http http://localhost:5000 (as i'm running my application on port = 5000)
   ```
8. hit enter and used the link provided there to access your web app.

## Directory structure:
└── chandreshsutariya-frs/
    ├── README.md
    ├── facer_2/
    │   ├── LICENSE
    │   ├── faceGrouper.py
    │   ├── imageFinder.py
    │   ├── requirements.txt
    │   └── __pycache__/
    └── frontend/
        ├── README.md
        ├── requirements.txt
        ├── .env
        └── src/
            ├── api.py
            ├── app.py
            ├── init_db.py
            ├── models.py
            ├── routes.py
            ├── __pycache__/
            ├── static/
            │   ├── css/
            │   │   ├── camera.css
            │   │   ├── login.css
            │   │   ├── result.css
            │   │   └── styles.css
            │   └── js/
            │       ├── camera.js
            │       ├── main.js
            │       └── result.js
            └── templates/
                ├── camera.html
                ├── index.html
                ├── login.html
                └── result.html

## Screenshots

## Usage
- Login with configured id and password.
- Select event images for upload
- Upload in Database Providing Unique Name.
- Provide a Password to tie shareable link with it preventing for unauthorized access to images.
- Then Press Generate Button and wait for processing.
- When Processing Complete Copy the link and open in another device/tab/browser.
- Enter the Password Correctly.
- Accept the Camera and Privacy Permissions.
- Enter Your Mobile Number and Tolerance(Optinal).
- Upload an image or use the camera to capture an image.
- The application will process the image and perform face detection and recognition.
- Now on result page you can adjust Tolerance to get Best Results.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.