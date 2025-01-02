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

def process_images_from_event(event_id, db_name="events_data.db", output_db_prefix="facial_features"):
    """
    Process images from an event stored in the database and save facial features to a new database.

    Args:
        event_id (int): Event ID to fetch images for.
        db_name (str): Name of the SQLite database storing events.
        output_db_prefix (str): Prefix for the output SQLite database name.
    """
    # Connect to the events database
    event_conn = sqlite3.connect(db_name)
    event_cursor = event_conn.cursor()

    # Fetch image data for the given event_id
    event_cursor.execute('SELECT image_name, image_data FROM events WHERE event_id = ?', (event_id,))
    images = event_cursor.fetchall()

    if not images:
        logging.info(f"No images found for event_id: {event_id}")
        print(f"No images found for event_id: {event_id}")
        return

    # Create a new database for storing facial features
    output_db_name = f"{output_db_prefix}_{event_id}.db"
    conn = sqlite3.connect(output_db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Faces (
        id INTEGER PRIMARY KEY,
        features BLOB,
        image_paths TEXT
    )
    ''')
    conn.commit()

    logging.info(f"Processing images for event_id: {event_id}, Total images: {len(images)}")
    print(f"Processing images for event_id: {event_id}, Total images: {len(images)}")

    for image_name, image_data in images:
        image_path = os.path.join("temp", image_name)
        os.makedirs("temp", exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(image_data)
        logging.info(f"Processing image: {image_name}")
        process_image(cursor, conn, image_path)
        os.remove(image_path)  # Remove temporary file after processing

    event_conn.close()
    conn.close()
    logging.info(f"Processing completed for event_id: {event_id}")
    print(f"Processing completed for event_id: {event_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Event ID is required as a command-line argument.")
        sys.exit(1)

    try:
        event_id = int(sys.argv[1])
        print(f"Processing event_id: {event_id}")
        process_images_from_event(event_id)
    except ValueError:
        print("Error: Invalid event ID. It must be an integer.")
        sys.exit(1)
