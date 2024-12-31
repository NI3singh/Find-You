# database.py
import sqlite3
from sqlite3 import Binary
import os

def init_db():
    conn = sqlite3.connect('face.db')
    c = conn.cursor()
    
    # Create tables
    c.executescript('''
        CREATE TABLE IF NOT EXISTS galleries (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS photos (
            id TEXT PRIMARY KEY,
            gallery_id TEXT,
            original_filename TEXT,
            image_data BLOB,
            face_encodings BLOB,
            FOREIGN KEY (gallery_id) REFERENCES galleries (id)
        );
        
        CREATE TABLE IF NOT EXISTS results (
            id TEXT PRIMARY KEY,
            gallery_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gallery_id) REFERENCES galleries (id)
        );
        
        CREATE TABLE IF NOT EXISTS matched_photos (
            result_id TEXT,
            photo_id TEXT,
            FOREIGN KEY (result_id) REFERENCES results (id),
            FOREIGN KEY (photo_id) REFERENCES photos (id)
        );
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('face.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
init_db()