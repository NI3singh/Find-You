

import logging
import os
import cv2
import numpy as np
import sqlite3
import sys
from retinaface import RetinaFace
from facenet_pytorch import InceptionResnetV1
import torch

# Initialize FaceNet for face recognition
facenet = InceptionResnetV1(pretrained='vggface2').eval()

# Initialize logging
logging.basicConfig(
    filename='facegrouper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_face_features(image, face_box):
    """
    Extract 512D facial features using FaceNet.

    Args:
        image (ndarray): Input RGB image.
        face_box (tuple): Bounding box coordinates (x1, y1, x2, y2).

    Returns:
        ndarray: 512D facial features.
    """
    x1, y1, x2, y2 = face_box
    face = image[y1:y2, x1:x2]
    face = cv2.resize(face, (160, 160))  # Resize to FaceNet input size
    face = np.transpose(face, (2, 0, 1))  # Change to (C, H, W)
    face = (face / 255.0).astype(np.float32)  # Normalize
    face = np.expand_dims(face, axis=0)  # Add batch dimension
    face_features = facenet(torch.from_numpy(face)).detach().numpy()
    return face_features.flatten()

def match_face(cursor, features, tolerance=0.8):
    """
    Check if the face features match any in the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor for querying.
        features (ndarray): 512D facial feature vector.
        tolerance (float): Threshold for feature matching.

    Returns:
        tuple: (bool, int) indicating match status and matched face ID.
    """
    cursor.execute('SELECT id, features FROM Faces')
    for row in cursor.fetchall():
        db_id, db_features = row
        db_features = np.frombuffer(db_features, dtype=np.float32)
        distance = np.linalg.norm(features - db_features)
        if distance < tolerance:
            return True, db_id
    return False, -1

def store_face_in_db(cursor, conn, features, image_path):
    """
    Store the new face features and image path in the database.
    """
    features_blob = features.tobytes()
    cursor.execute('INSERT INTO Faces (features, image_paths) VALUES (?, ?)', (features_blob, image_path))
    conn.commit()

def update_image_paths(cursor, conn, db_id, image_path):
    """
    Update the image paths for an existing face in the database.
    """
    cursor.execute('SELECT image_paths FROM Faces WHERE id = ?', (db_id,))
    existing_paths = cursor.fetchone()[0]
    new_paths = existing_paths + "," + image_path
    cursor.execute('UPDATE Faces SET image_paths = ? WHERE id = ?', (new_paths, db_id))
    conn.commit()

def process_image(cursor, conn, image_path):
    """
    Process a single image to detect and identify faces.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return 0

    # Convert BGR to RGB for RetinaFace
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect faces using RetinaFace
    faces = RetinaFace.detect_faces(rgb_image)

    if not faces:
        print(f"No faces found in {image_path}")
        return 0

    new_faces = 0
    for face_id, face_data in faces.items():
        face_box = face_data['facial_area']
        features = get_face_features(rgb_image, face_box)

        match, db_id = match_face(cursor, features)
        if match:
            print(f"Match found in {image_path}")
            update_image_paths(cursor, conn, db_id, image_path)
        else:
            print(f"New face found in {image_path}")
            store_face_in_db(cursor, conn, features, image_path)
            new_faces += 1

    return new_faces

def process_images_from_folder(image_folder, db_name="facial_features.db"):
    """
    Process images from a local folder and store facial features in a database.

    Args:
        image_folder (str): Path to the folder containing the images.
        db_name (str): Name of the SQLite database to store facial features.
    """
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the Faces table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Faces (
        id INTEGER PRIMARY KEY,
        features BLOB,
        image_paths TEXT
    )
    ''')
    conn.commit()

    # Get list of images in the folder
    images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png','.JPG'))]

    if not images:
        logging.info(f"No images found in folder: {image_folder}")
        print(f"No images found in folder: {image_folder}")
        return

    logging.info(f"Processing images from folder: {image_folder}, Total images: {len(images)}")
    print(f"Processing images from folder: {image_folder}, Total images: {len(images)}")

    for image_path in images:
        logging.info(f"Processing image: {image_path}")
        process_image(cursor, conn, image_path)

    conn.close()
    logging.info(f"Processing completed for folder: {image_folder}")
    print(f"Processing completed for folder: {image_folder}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Image folder path is required as a command-line argument.")
        sys.exit(1)

    image_folder = sys.argv[1]
    print(f"Processing images from folder: {image_folder}")
    process_images_from_folder(image_folder)