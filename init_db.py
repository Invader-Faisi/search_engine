from app import create_app, db
from app.models.user_model import User
from app.models.document_model import Document
from app.models.activity_model import UserActivity, DocumentHistory

app = create_app()

with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        from app.utils.security import hash_password
        admin = User(
            username='admin',
            email='admin@search.com',
            password_hash=hash_password('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username='admin', password='admin123'")
    
    print("Database created successfully!")