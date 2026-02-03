from werkzeug.security import generate_password_hash
from app import app, db
from app import User

with app.app_context():
    # ADMIN USER
    admin = User(
        name="Admin",
        email="admin@school.com",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    # STUDENT USER
    student = User(
        name="Student One",
        email="student@school.com",
        password=generate_password_hash("student123"),
        role="student"
    )

    db.session.add(admin)
    db.session.add(student)
    db.session.commit()

    print("✅ Users created successfully")
