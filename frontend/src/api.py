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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from facer_2.imageFinder import process_input_image

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
        
        subprocess.Popen(["python", r"C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\faceGrouper.py", str(event_id)])
        # os.system(r"C:\Users\itsni\Desktop\FRS_ELaunch\facer_2\faceGrouper.py {event_id} &")
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
        data = request.json
        image_data = data.get('image')  # Base64-encoded selfie image
        event_id = data.get('event_id')  # Current event ID

        if not image_data or not event_id:
            return jsonify({"error": "Missing image data or event_id"}), 400

        # Save the selfie temporarily
        temp_image_path = os.path.join(app.config['TEMPORARY_FOLDER'], 'temp_selfie.jpg')
        with open(temp_image_path, 'wb') as temp_image:
            temp_image.write(base64.b64decode(image_data))

        # Process the selfie using imageFinder.py
        from facer_2.imageFinder import process_input_image
        db_path = f"facial_features_{event_id}.db"
        matching_images = process_input_image(temp_image_path, db_path, event_id)

        if not matching_images:
            return jsonify({"photos": [], "message": "No matching photos found"}), 200

        resultId = event_id
        return jsonify({"photos": matching_images, "resultId": resultId}), 200

    except Exception as e:
        print("Error in find_photos:", e)
        return jsonify({"error": "Failed to process the request. Check server logs for details."}), 500

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