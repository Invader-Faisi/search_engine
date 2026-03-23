from app import db
from datetime import datetime

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous users
    activity_type = db.Column(db.String(50), nullable=False)  # 'search', 'view', 'download', 'upload', 'login'
    description = db.Column(db.String(500), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='activities')
    document = db.relationship('Document', backref='activities')
    
    def __repr__(self):
        return f"<UserActivity {self.activity_type} by {self.user_id} at {self.timestamp}>"


class DocumentHistory(db.Model):
    __tablename__ = 'document_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'view', 'download', 'search'
    search_query = db.Column(db.String(500), nullable=True)
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='document_history')
    document = db.relationship('Document', backref='access_history')
    
    def __repr__(self):
        return f"<DocumentHistory {self.action} doc:{self.document_id} by user:{self.user_id}>"