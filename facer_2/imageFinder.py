import cv2
import numpy as np
import sqlite3
import os
import torch
from retinaface import RetinaFace
from facenet_pytorch import InceptionResnetV1

# Initialize FaceNet for face recognition
facenet = InceptionResnetV1(pretrained='vggface2').eval()

def preprocess_image(image, face_box):
    """
    Preprocess the face image for FaceNet input.

    Args:
        image (ndarray): Input RGB image.
        face_box (tuple): Bounding box coordinates (x1, y1, x2, y2).

    Returns:
        ndarray: Preprocessed image suitable for FaceNet.
    """
    x1, y1, x2, y2 = face_box
    face = image[y1:y2, x1:x2]
    face = cv2.resize(face, (160, 160))  # Resize to FaceNet input size
    face = np.transpose(face, (2, 0, 1))  # Change to (C, H, W)
    face = (face / 255.0).astype(np.float32)  # Normalize
    face = np.expand_dims(face, axis=0)  # Add batch dimension
    return face

def get_face_features(image, face_box):
    """
    Extract 512D facial features using FaceNet.

    Args:
        image (ndarray): Input RGB image.
        face_box (tuple): Bounding box coordinates (x1, y1, x2, y2).

    Returns:
        ndarray: 512D facial features.
    """
    face = preprocess_image(image, face_box)
    face_features = facenet(torch.from_numpy(face)).detach().numpy()
    return face_features.flatten()

def find_matching_images(features, cursor, tolerance):
    """
    Find all images in the database that match the given facial features.

    Args:
        features (ndarray): 512D facial feature vector.
        cursor (sqlite3.Cursor): Database cursor for querying.
        tolerance (float): Threshold for feature matching.

    Returns:
        list: List of matching image paths.
    """
    cursor.execute('SELECT id, features, image_paths FROM Faces')
    matching_images = []

    for row in cursor.fetchall():
        _, db_features, image_paths = row
        db_features = np.frombuffer(db_features, dtype=np.float32)
        distance = np.linalg.norm(features - db_features)
        if distance < tolerance:
            matching_images.extend(image_paths.split(','))

    return matching_images

def save_matches_to_event_db(event_id, matched_image_paths, mobile_number):
    """
    Save the matched image paths to the database named 'Matched_Faces_event-id.db'.
    Existing entries for the given mobile number are overwritten.

    Args:
        event_id (int): The event ID for the matched images.
        matched_image_paths (list): List of matched image file paths.
        mobile_number (str): Mobile number associated with the matched images.
    """
    db_name = f"Matched_Faces_event_{event_id}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the Matches table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            image_path TEXT,
            mobile_number TEXT
        )
    ''')

    # Delete existing entries for the given mobile number
    print(f"Deleting previous matches for mobile number: {mobile_number}")
    cursor.execute('DELETE FROM Matches WHERE mobile_number = ?', (mobile_number,))

    # Verify deletion
    conn.commit()
    cursor.execute('SELECT * FROM Matches WHERE mobile_number = ?', (mobile_number,))
    deleted_entries = cursor.fetchall()
    if not deleted_entries:
        print(f"Successfully deleted all previous entries for mobile number: {mobile_number}")
    else:
        print(f"Failed to delete some entries: {deleted_entries}")

    # Insert new matched image paths and names into the database
    print(f"Saving new matches for mobile number: {mobile_number}")
    for image_path in matched_image_paths:
        image_name = os.path.basename(image_path)  # Extract the image file name from the path
        cursor.execute('INSERT INTO Matches (image_name, image_path, mobile_number) VALUES (?, ?, ?)',
                       (image_name, image_path, mobile_number))

    conn.commit()
    conn.close()
    print(f"Matched images for mobile number {mobile_number} saved to {db_name}")



# def process_input_image(temp_image_path, db_path, event_id, mobile_number, tolerance):
#     """
#     Process the input image to find all matching images in the specified database.

#     Args:
#         image_path (str): Path to the input selfie image.
#         db_path (str): Path to the facial features database for the event.
#         event_id (int): Event ID for the current operation.
#         mobile_number (str): Mobile number associated with the matched images.

#     Returns:
#         list: List of matching image paths.
#     """
#     try:
#         if not os.path.exists(db_path):
#             print(f"Database not found: {db_path}")
#             return []

#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()

#         print(f"Tolerance value being used: {tolerance}")
        
#         # Read the input selfie image
#         image = cv2.imread(temp_image_path)
#         if image is None:
#             print(f"Failed to load image: {temp_image_path}")
#             return []

#         # Convert BGR to RGB for RetinaFace
#         rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#         # Detect faces using RetinaFace
#         faces = RetinaFace.detect_faces(rgb_image)

#         if not faces:
#             print(f"No faces found in {temp_image_path}")
#             return []

#         all_matching_images = set()
#         for face_id, face_data in faces.items():
#             face_box = face_data['facial_area']
#             features = get_face_features(rgb_image, face_box)
#             matching_images = find_matching_images(features, cursor, tolerance)
#             all_matching_images.update(matching_images)

#         conn.close()

#         # Save matched images to a new database
#         save_matches_to_event_db(event_id, list(all_matching_images), mobile_number)

#         return list(all_matching_images)

#     except Exception as e:
#         print(f"Error in process_input_image: {e}")
#         return []


def process_input_image(temp_image_path, db_path, event_id, mobile_number, tolerance):
    """
    Process the input image to find all matching images in the specified database.

    Args:
        temp_image_path (str): Path to the input selfie image.
        db_path (str): Path to the facial features database for the event.
        event_id (int): Event ID for the current operation.
        mobile_number (str): Mobile number associated with the matched images.
        tolerance (float): Matching tolerance threshold.

    Returns:
        list: List of matching image paths.
    """
    try:
        # Ensure database exists
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            return []

        # Ensure the input image path is updated dynamically using mobile_number
        temp_image_path = os.path.join("temp", f"temp_selfie_{mobile_number}.png")
        if not os.path.exists(temp_image_path):
            print(f"No selfie image found for mobile number: {mobile_number}")
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Tolerance value being used: {tolerance}")

        # Read the input selfie image
        image = cv2.imread(temp_image_path)
        if image is None:
            print(f"Failed to load image: {temp_image_path}")
            return []

        # Convert BGR to RGB for RetinaFace
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces using RetinaFace
        faces = RetinaFace.detect_faces(rgb_image)

        if not faces:
            print(f"No faces found in {temp_image_path}")
            return []

        all_matching_images = set()
        for face_id, face_data in faces.items():
            face_box = face_data['facial_area']
            features = get_face_features(rgb_image, face_box)
            matching_images = find_matching_images(features, cursor, tolerance)
            all_matching_images.update(matching_images)

        conn.close()

        # Save matched images to the database
        save_matches_to_event_db(event_id, list(all_matching_images), mobile_number)

        return list(all_matching_images)

    except Exception as e:
        print(f"Error in process_input_image: {e}")
        return []
