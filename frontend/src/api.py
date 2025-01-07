from flask import request, jsonify
import sqlite3
import os
from app import app
import subprocess
import sys 
import base64
import cv2
from flask import send_file
import zipfile
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# MY_ENV_VAR = os.getenv('MY_ENV_VAR')
facegrouper_path = os.getenv('facegrouper_path')
imagefinder_path = os.getenv('imagefinder_path')
event_database_path = os.getenv('event_database_path')
selfie_temp_path = os.getenv('selfie_temp_path')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@app.route('/api/generate_faces', methods=['POST'])
def generate_faces():
    """Trigger facegrouper processing for a specific event_id."""
    event_id = request.json.get('event_id')

    if not event_id:
        # If no event_id is provided, fetch the latest event_id from the database
        db_path = 'events_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(event_id) FROM events')
        event_id = cursor.fetchone()[0]
        conn.close()

    if not event_id:
        return jsonify({"error": f"No images found for event_id {event_id}"}), 404

    try:
        # Run facegrouper.py processing in the background
        
        facegrouper_path = r"C:\Users\itsni\Desktop\frs\facer_2\faceGrouper.py"
        if not os.path.exists(facegrouper_path):
            return jsonify({"error": "faceGrouper.py not found at the specified path"}), 500

        # Use the same Python executable running the Flask app
        python_executable = sys.executable

        # Call the subprocess
        subprocess.Popen([python_executable, facegrouper_path, str(event_id)])
        
        return jsonify({
            "message": f"Face processing started for event_id: {event_id}",
            "event_id": event_id,
            "share_link": f"{request.host_url}camera/{event_id}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_event', methods=['POST'])
def upload_event():
    event_name = request.form.get('event_name')
    images = request.files.getlist('images')

    if not event_name or not images:
        return jsonify({"error": "Event name and images are required"}), 400

    db_path = 'events_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the events table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER,
                        event_name TEXT,
                        image_name TEXT,
                        image_data BLOB
                      )''')

    # Determine the event_id for the current event
    cursor.execute('SELECT MAX(event_id) FROM events')
    max_event_id = cursor.fetchone()[0]
    current_event_id = 1 if max_event_id is None else max_event_id + 1

    try:
        # Insert each image into the database with the same event_id
        for image in images:
            image_name = image.filename
            image_data = image.read()
            cursor.execute('INSERT INTO events (event_id, event_name, image_name, image_data) VALUES (?, ?, ?, ?)',
                           (current_event_id, event_name, image_name, image_data))

        # Commit the transaction
        conn.commit()

        return jsonify({"message": f"Event '{event_name}' uploaded successfully!", "event_id": current_event_id}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/api/check_event_name', methods=['POST'])
def check_event_name():
    """Check if the event_name exists in the database."""
    event_name = request.json.get('event_name')

    if not event_name:
        return jsonify({"error": "Event name is required"}), 400

    db_path = 'events_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the events table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER,
                        event_name TEXT,
                        image_name TEXT,
                        image_data BLOB
                      )''')
    conn.commit()

    # Check if the event_name exists
    cursor.execute('SELECT event_id FROM events WHERE event_name = ?', (event_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200


@app.route('/api/find_photos', methods=['POST'])
def find_photos():
    try:
        print("Processing find_photos API...")
        print(f"Content-Type: {request.content_type}")

        mobile_number = None
        tolerance = None

        if 'multipart/form-data' in request.content_type:
            event_id = request.form.get('event_id')
            mobile_number = request.form.get('mobile_number')
            tolerance = request.form.get('tolerance')

            print(f"Received multipart/form-data: event_id={event_id}, mobile_number={mobile_number}, tolerance={tolerance}")

            if not event_id or not mobile_number:
                return jsonify({"error": "Missing event_id, or mobile_number"}), 400

            temp_image_path = os.path.join(app.config['TEMPORARY_FOLDER'], 'temp_selfie.png')
            print(f"Temp image path: {temp_image_path}")

        elif 'application/json' in request.content_type:
            data = request.json
            event_id = data.get('event_id')
            mobile_number = data.get('mobile_number')
            tolerance = data.get('tolerance')

            print(f"Received JSON: event_id={event_id}, mobile_number={mobile_number}, tolerance={tolerance}")

            if not event_id or not mobile_number:
                return jsonify({"error": "Missing event_id, or mobile_number"}), 400

            temp_image_path = os.path.join(app.config['TEMPORARY_FOLDER'], 'temp_selfie.png')
            print(f"Temp image path: {temp_image_path}")

        else:
            return jsonify({"error": "Unsupported Content-Type. Use 'multipart/form-data' or 'application/json'"}), 415

        try:
            tolerance = float(tolerance) if tolerance is not None else 0.6
        except ValueError:
            tolerance = 0.6
        print(f"Using tolerance: {tolerance}")

        from facer_2.imageFinder import process_input_image
        db_path = f"facial_features_{event_id}.db"
        print(f"Database path: {db_path}")

        if not os.path.exists(db_path):
            return jsonify({"error": f"Database for event_id {event_id} not found"}), 404

        matching_images = process_input_image(temp_image_path, db_path, event_id, mobile_number, tolerance)
        print(f"Matching images: {matching_images}")

        if not matching_images:
            return jsonify({"photos": [], "message": "No matching photos found"}), 200

        resultId = event_id
        return jsonify({"photos": matching_images, "resultId": resultId}), 200

    except Exception as e:
        print("Error in find_photos:", e)
        return jsonify({"error": "Failed to process the request. Check server logs for details."}), 500

    

@app.route('/api/upload_photo', methods=['POST'])
def upload_photo():
    try:
        print("Processing upload_photo API...")
        if 'multipart/form-data' in request.content_type:
            image_file = request.files.get('image')

            if not image_file:
                return jsonify({"error": "No image provided"}), 400

            temp_image_path = os.path.join(app.config['TEMPORARY_FOLDER'], 'temp_selfie.png')
            print(f"Saving image to: {temp_image_path}")
            image_file.save(temp_image_path)

            if os.path.exists(temp_image_path):
                print("Image saved successfully!")
            else:
                print("Image save failed!")

            return jsonify({"message": "Photo uploaded and saved as temp_selfie.png"}), 200

        else:
            return jsonify({"error": "Unsupported Content-Type. Use 'multipart/form-data'"}), 415

    except Exception as e:
        print("Error in upload_photo:", e)
        return jsonify({"error": "Failed to upload the photo. Check server logs for details."}), 500



@app.route('/api/result/<event_id>', methods=['GET'])
def get_event_result(event_id):
    try:
        matched_db_path = f"Matched_Faces_event_{event_id}.db"
        if not os.path.exists(matched_db_path):
            return jsonify({"photos": []}), 200  # Return empty photos if no database

        conn_matched = sqlite3.connect(matched_db_path)
        cursor_matched = conn_matched.cursor()
        cursor_matched.execute("SELECT image_name FROM Matches")
        matched_image_names = [os.path.basename(row[0]) for row in cursor_matched.fetchall()]
        conn_matched.close()
        print(matched_image_names)

        mobile_number = request.args.get("mobile_number")
        print(f"Mobile number: {mobile_number} from result API")

        if not matched_image_names:
            return jsonify({"photos": []}), 200

        event_db_path = "events_data.db"
        conn_events = sqlite3.connect(event_db_path)
        cursor_events = conn_events.cursor()
        placeholders = ', '.join(['?'] * len(matched_image_names))
        query = f"""
            SELECT image_name, image_data FROM events
            WHERE event_id = ? AND image_name IN ({placeholders})
        """
        cursor_events.execute(query, [event_id] + matched_image_names)
        images = []
        for image_name, image_data in cursor_events.fetchall():
            images.append({
                "name": image_name,
                "data": base64.b64encode(image_data).decode('utf-8')
            })

        conn_events.close()
        return jsonify({"photos": images}), 200

    except Exception as e:
        print(f"Error in get_event_results: {e}")
        return jsonify({"error": "Failed to fetch results"}), 500

@app.route('/api/result/<event_id>/download', methods=['GET'])
def download_matched_photos(event_id):
    """
    Create a zip file containing all matched photos for the given event ID.
    """
    try:
        # Step 1: Connect to Matched_Faces_event-id.db to get matched image paths
        matched_db_path = f"Matched_Faces_event_{event_id}.db"
        if not os.path.exists(matched_db_path):
            return jsonify({"error": "Matched database not found"}), 404

        conn_matched = sqlite3.connect(matched_db_path)
        cursor_matched = conn_matched.cursor()
        cursor_matched.execute("SELECT image_name FROM Matches")
        matched_image_names = [row[0] for row in cursor_matched.fetchall()]
        conn_matched.close()

        if not matched_image_names:
            return jsonify({"error": "No matched photos to download"}), 404

        # Step 2: Connect to events_data.db to fetch the actual image data
        event_db_path = "events_data.db"
        if not os.path.exists(event_db_path):
            return jsonify({"error": "Events database not found"}), 404

        conn_events = sqlite3.connect(event_db_path)
        cursor_events = conn_events.cursor()

        # Prepare placeholders for SQL query
        placeholders = ', '.join(['?'] * len(matched_image_names))
        query = f"""
            SELECT image_name, image_data FROM events
            WHERE event_id = ? AND image_name IN ({placeholders})
        """
        cursor_events.execute(query, [event_id] + matched_image_names)

        # Fetch image data
        images = cursor_events.fetchall()
        conn_events.close()

        if not images:
            return jsonify({"error": "No photos found in events database"}), 404

        # Step 3: Create an in-memory zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for image_name, image_data in images:
                # Write each image to the zip file
                zip_file.writestr(image_name, image_data)

        zip_buffer.seek(0)  # Reset buffer to the beginning

        # Step 4: Send the zip file as a response
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='matched_photos.zip'
        )

    except Exception as e:
        print(f"Error in downloading matched photos: {e}")
        return jsonify({"error": "Failed to download matched photos"}), 500