# # import cv2
# # import dlib
# # import numpy as np
# # import sqlite3

# # # Load the detector and facial landmark predictor
# # detector = dlib.get_frontal_face_detector()
# # predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
# # face_rec_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

# # # Initialize SQLite database
# # conn = sqlite3.connect('facial_features.db')
# # cursor = conn.cursor()

# # def get_face_features(image, face_rect):
# #     """Extract the 128D facial features from a face rectangle."""
# #     shape = predictor(image, face_rect)
# #     face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
# #     return np.array(face_descriptor)

# # def find_matching_images(features, tolerance=0.45): #previous tolerance value is 0.53
# #     """Find all images in the database that match the given facial features."""
# #     cursor.execute('SELECT id, features, image_paths FROM Faces')
# #     matching_images = []
    
# #     for row in cursor.fetchall():
# #         db_id, db_features, image_paths = row
# #         db_features = np.frombuffer(db_features, dtype=np.float64)
# #         distance = np.linalg.norm(features - db_features)
# #         if distance < tolerance:
# #             matching_images.extend(image_paths.split(','))
    
# #     return matching_images

# # def process_input_image(image_path):
# #     """Process the input image to find all matching images in the database."""
# #     image = cv2.imread(image_path)
# #     if image is None:
# #         print(f"Failed to load image: {image_path}")
# #         return []

# #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #     faces = detector(gray)
    
# #     if len(faces) == 0:
# #         print(f"No faces found in {image_path}")
# #         return []
    
# #     all_matching_images = set()
# #     for face in faces:
# #         features = get_face_features(image, face)
# #         matching_images = find_matching_images(features)
# #         all_matching_images.update(matching_images)
    
# #     return list(all_matching_images)

# # # Path to the input image
# # input_image_path = r'C:\Users\itsni\Desktop\Known_People-org\Nitin_Image1.jpg'

# # matching_images = process_input_image(input_image_path)

# # if matching_images:
# #     print(f"Matching images found for {input_image_path}:")
# #     for img_path in matching_images:
# #         print(img_path)
# # else:
# #     print(f"No matching images found for {input_image_path}")

# # # Close the database connection when done
# # conn.close()



# import cv2
# import dlib
# import numpy as np
# import sqlite3

# # Load the detector and facial landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\shape_predictor_68_face_landmarks.dat')
# face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\dlib_face_recognition_resnet_model_v1.dat')

# def get_face_features(image, face_rect):
#     """Extract the 128D facial features from a face rectangle."""
#     shape = predictor(image, face_rect)
#     face_descriptor = face_rec_model.compute_face_descriptor(image, shape, num_jitters=10)
#     return np.array(face_descriptor)

# def process_input_image(image_path, db_path):
#     """Process the input image to find all matching images in the specified database."""
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"Failed to load image: {image_path}")
#         return []

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     faces = detector(gray)

#     if len(faces) == 0:
#         print(f"No faces found in {image_path}")
#         return []

#     all_matching_images = set()
#     for face in faces:
#         features = get_face_features(image, face)
#         matching_images = find_matching_images(features, cursor)
#         all_matching_images.update(matching_images)

#     conn.close()
#     return list(all_matching_images)

# def find_matching_images(features, cursor, tolerance=0.45):
#     """Find all images in the database that match the given facial features."""
#     cursor.execute('SELECT id, features, image_paths FROM Faces')
#     matching_images = []

#     for row in cursor.fetchall():
#         db_id, db_features, image_paths = row
#         db_features = np.frombuffer(db_features, dtype=np.float64)
#         distance = np.linalg.norm(features - db_features)
#         if distance < tolerance:
#             matching_images.extend(image_paths.split(','))

#     return matching_images



# import cv2
# import dlib
# import numpy as np
# import sqlite3
# import os

# # Load the detector and facial landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\shape_predictor_68_face_landmarks.dat')
# face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\dlib_face_recognition_resnet_model_v1.dat')

# def get_face_features(image, face_rect):
#     """Extract the 128D facial features from a face rectangle."""
#     shape = predictor(image, face_rect)
#     face_descriptor = face_rec_model.compute_face_descriptor(image, shape, num_jitters=10)
#     return np.array(face_descriptor)

# def find_matching_images(features, cursor, tolerance=0.45):
#     """Find all images in the database that match the given facial features."""
#     cursor.execute('SELECT id, features, image_paths FROM Faces')
#     matching_images = []

#     for row in cursor.fetchall():
#         db_id, db_features, image_paths = row
#         db_features = np.frombuffer(db_features, dtype=np.float64)
#         distance = np.linalg.norm(features - db_features)
#         if distance < tolerance:
#             matching_images.extend(image_paths.split(','))  # Add matching image paths

#     return matching_images

# def process_input_image(image_path, db_path):
#     """
#     Process the input image to find all matching images in the specified database.

#     Args:
#         image_path (str): Path to the input selfie image.
#         db_path (str): Path to the facial features database for the event.
    
#     Returns:
#         list: List of matching image paths.
#     """
#     try:
#         # Check if the database exists
#         if not os.path.exists(db_path):
#             print(f"Database not found: {db_path}")
#             return []

#         # Connect to the database
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()

#         # Read the image
#         image = cv2.imread(image_path)
#         if image is None:
#             print(f"Failed to load image: {image_path}")
#             return []

#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         faces = detector(gray)

#         if len(faces) == 0:
#             print(f"No faces found in {image_path}")
#             return []

#         all_matching_images = set()
#         for face in faces:
#             features = get_face_features(image, face)
#             matching_images = find_matching_images(features, cursor)
#             all_matching_images.update(matching_images)

#         conn.close()
#         return list(all_matching_images)

#     except Exception as e:
#         print(f"Error in process_input_image: {e}")
#         return []

# import cv2
# import dlib
# import numpy as np
# import sqlite3
# import os

# # Load the detector and facial landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\shape_predictor_68_face_landmarks.dat')
# face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\dlib_face_recognition_resnet_model_v1.dat')

# def get_face_features(image, face_rect):
#     """Extract the 128D facial features from a face rectangle."""
#     shape = predictor(image, face_rect)
#     face_descriptor = face_rec_model.compute_face_descriptor(image, shape, num_jitters=10)
#     return np.array(face_descriptor)

# def find_matching_images(features, cursor, tolerance=0.45):
#     """Find all images in the database that match the given facial features."""
#     cursor.execute('SELECT id, features, image_paths FROM Faces')
#     matching_images = []

#     for row in cursor.fetchall():
#         _, db_features, image_paths = row
#         db_features = np.frombuffer(db_features, dtype=np.float64)
#         distance = np.linalg.norm(features - db_features)
#         if distance < tolerance:
#             matching_images.extend(image_paths.split(','))  # Add matching image paths

#     return matching_images

# def save_matches_to_event_db(event_id, matched_image_paths):
#     """
#     Save the matched image paths to a database named 'Matched_Faces_event-id.db'.

#     Args:
#         event_id (int): The event ID for the matched images.
#         matched_image_paths (list): List of matched image file paths.
#     """
#     db_name = f"Matched_Faces_event_{event_id}.db"
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()

#     # Create the Matches table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS Matches (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             image_name TEXT,
#             image_path TEXT
#         )
#     ''')

#     # Insert matched image paths and names into the database
#     for image_path in matched_image_paths:
#         image_name = os.path.basename(image_path)  # Extract the image file name from the path
#         cursor.execute('INSERT INTO Matches (image_name, image_path) VALUES (?, ?)', (image_name, image_path))

#     conn.commit()
#     conn.close()
#     print(f"Matched images saved to {db_name}")


# # def process_input_image(image_path, db_path):
# #     """
# #     Process the input image to find all matching images in the specified database.

# #     Args:
# #         image_path (str): Path to the input selfie image.
# #         db_path (str): Path to the facial features database for the event.
    
# #     Returns:
# #         list: List of matching image paths.
# #     """
# #     try:
# #         if not os.path.exists(db_path):
# #             print(f"Database not found: {db_path}")
# #             return []

# #         conn = sqlite3.connect(db_path)
# #         cursor = conn.cursor()

# #         image = cv2.imread(image_path)
# #         if image is None:
# #             print(f"Failed to load image: {image_path}")
# #             return []

# #         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #         faces = detector(gray)

# #         if len(faces) == 0:
# #             print(f"No faces found in {image_path}")
# #             return []

# #         all_matching_images = set()
# #         for face in faces:
# #             features = get_face_features(image, face)
# #             matching_images = find_matching_images(features, cursor)
# #             all_matching_images.update(matching_images)

# #         conn.close()
# #         return list(all_matching_images)

# #     except Exception as e:
# #         print(f"Error in process_input_image: {e}")
# #         return []

# def process_input_image(image_path, db_path, event_id):
#     """
#     Process the input image to find all matching images in the specified database.

#     Args:
#         image_path (str): Path to the input selfie image.
#         db_path (str): Path to the facial features database for the event.
#         event_id (int): Event ID for the current operation.

#     Returns:
#         list: List of matching image paths.
#     """
#     try:
#         if not os.path.exists(db_path):
#             print(f"Database not found: {db_path}")
#             return []

#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()

#         image = cv2.imread(image_path)
#         if image is None:
#             print(f"Failed to load image: {image_path}")
#             return []

#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         faces = detector(gray)

#         if len(faces) == 0:
#             print(f"No faces found in {image_path}")
#             return []

#         all_matching_images = set()
#         for face in faces:
#             features = get_face_features(image, face)
#             matching_images = find_matching_images(features, cursor)
#             all_matching_images.update(matching_images)

#         conn.close()

#         # Save matched images to a new database
#         save_matches_to_event_db(event_id, list(all_matching_images))

#         return list(all_matching_images)

#     except Exception as e:
#         print(f"Error in process_input_image: {e}")
#         return []


import cv2
import dlib
import numpy as np
import sqlite3
import os
import sys

# Load the detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1(r'C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\dlib_face_recognition_resnet_model_v1.dat')

def get_face_features(image, face_rect):
    """Extract the 128D facial features from a face rectangle."""
    shape = predictor(image, face_rect)
    face_descriptor = face_rec_model.compute_face_descriptor(image, shape, num_jitters=10)
    return np.array(face_descriptor)

def find_matching_images(features, cursor, tolerance=0.53):
    """Find all images in the database that match the given facial features."""
    cursor.execute('SELECT id, features, image_paths FROM Faces')
    matching_images = []

    for row in cursor.fetchall():
        _, db_features, image_paths = row
        db_features = np.frombuffer(db_features, dtype=np.float64)
        distance = np.linalg.norm(features - db_features)
        if distance < tolerance:
            matching_images.extend(image_paths.split(','))  # Add matching image paths

    return matching_images

def process_input_image(image_path, db_path):
    """
    Process the input image to find all matching images in the specified database.

    Args:
        image_path (str): Path to the input selfie image.
        db_path (str): Path to the facial features database.
    
    Returns:
        list: List of matching image paths.
    """
    try:
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) == 0:
            print(f"No faces found in {image_path}")
            return []

        all_matching_images = set()
        for face in faces:
            features = get_face_features(image, face)
            matching_images = find_matching_images(features, cursor)
            all_matching_images.update(matching_images)

        conn.close()

        return list(all_matching_images)

    except Exception as e:
        print(f"Error in process_input_image: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python imagefinder.py <path_to_selfie_image> <path_to_database>")
        sys.exit(1)

    selfie_image = sys.argv[1]
    database_path = sys.argv[2]

    if not os.path.exists(selfie_image):
        print(f"Error: Selfie image '{selfie_image}' does not exist.")
        sys.exit(1)

    if not os.path.exists(database_path):
        print(f"Error: Database '{database_path}' does not exist.")
        sys.exit(1)

    print(f"Processing selfie image: {selfie_image} against database: {database_path}")
    matched_images = process_input_image(selfie_image, database_path)

    if matched_images:
        print("Matched images:")
        for img in matched_images:
            print(img)
    else:
        print("No matches found.")

