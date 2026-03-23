from app.models.activity_model import UserActivity, DocumentHistory
from app.models.document_model import Document
from app import db
from datetime import datetime, timedelta
from flask import request
from flask_login import current_user

def log_activity(activity_type, description, document_id=None, user_id=None):
    """Log user activity"""
    try:
        activity = UserActivity(
            user_id=user_id or (current_user.id if current_user.is_authenticated else None),
            activity_type=activity_type,
            description=description,
            document_id=document_id,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string[:500] if request and request.user_agent else None,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        return activity
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()
        return None

def log_document_access(user_id, document_id, action, search_query=None):
    """Log document access (view, download, search)"""
    try:
        # Check if document exists
        document = Document.query.get(document_id)
        if not document:
            return None
            
        history = DocumentHistory(
            user_id=user_id,
            document_id=document_id,
            action=action,
            search_query=search_query,
            accessed_at=datetime.utcnow()
        )
        db.session.add(history)
        
        # Keep only last 50 history entries per user to prevent DB bloat
        old_entries = DocumentHistory.query.filter_by(user_id=user_id)\
            .order_by(DocumentHistory.accessed_at.desc())\
            .offset(50).all()
        for entry in old_entries:
            db.session.delete(entry)
            
        db.session.commit()
        return history
    except Exception as e:
        print(f"Error logging document access: {e}")
        db.session.rollback()
        return None

def get_recent_activities(user_id=None, limit=20):
    """Get recent activities for a user or all users"""
    query = UserActivity.query.order_by(UserActivity.timestamp.desc())
    if user_id:
        query = query.filter_by(user_id=user_id)
    return query.limit(limit).all()

def get_recent_document_history(user_id, limit=10):
    """Get recent document access history for a user"""
    return DocumentHistory.query.filter_by(user_id=user_id)\
        .order_by(DocumentHistory.accessed_at.desc())\
        .limit(limit).all()

def get_user_statistics(user_id):
    """Get user activity statistics"""
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Count activities in last week
    recent_activities = UserActivity.query.filter(
        UserActivity.user_id == user_id,
        UserActivity.timestamp >= week_ago
    ).count()
    
    # Count document views
    document_views = DocumentHistory.query.filter(
        DocumentHistory.user_id == user_id,
        DocumentHistory.action == 'view'
    ).count()
    
    # Count searches
    searches = DocumentHistory.query.filter(
        DocumentHistory.user_id == user_id,
        DocumentHistory.action == 'search'
    ).count()
    
    # Most accessed documents
    from sqlalchemy import func
    popular_docs = db.session.query(
        DocumentHistory.document_id,
        Document.filename,
        func.count(DocumentHistory.id).label('access_count')
    ).join(Document, DocumentHistory.document_id == Document.id)\
     .filter(DocumentHistory.user_id == user_id)\
     .group_by(DocumentHistory.document_id, Document.filename)\
     .order_by(func.count(DocumentHistory.id).desc())\
     .limit(5).all()
    
    return {
        'recent_activities': recent_activities,
        'document_views': document_views,
        'searches': searches,
        'popular_documents': [
            {'filename': doc.filename, 'access_count': doc.access_count}
            for doc in popular_docs
        ]
    }

def cleanup_old_activities(days_to_keep=30):
    """Clean up activities older than specified days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        old_activities = UserActivity.query.filter(
            UserActivity.timestamp < cutoff_date
        ).delete()
        db.session.commit()
        return old_activities
    except Exception as e:
        print(f"Error cleaning up old activities: {e}")
        db.session.rollback()
        return 0