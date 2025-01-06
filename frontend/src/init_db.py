from app import app, db, user_datastore
from flask_security.utils import hash_password

def init_database():
    with app.app_context():
        # First drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Create test user
        user_datastore.create_user(
            username="admin",
            email="admin@example.com", 
            name="Administrator",
            password=hash_password("admin123")
        )
        db.session.commit()

if __name__ == "__main__":
    init_database()