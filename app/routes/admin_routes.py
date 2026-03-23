from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from app.models.user_model import User
from app.models.document_model import Document
from app.services.backup_service import create_backup, list_backups, restore_backup, cleanup_old_backups
from app import db
from datetime import datetime, timedelta
import os

admin_bp = Blueprint('admin', __name__)

def is_admin():
    """Check if current user is admin"""
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if not is_admin():
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('search.home'))
    
    # Get statistics
    total_users = User.query.count()
    total_documents = Document.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_documents = Document.query.order_by(Document.upload_date.desc()).limit(10).all()
    
    # Activity in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = Document.query.filter(Document.upload_date >= week_ago).count()
    
    # Get backup info
    backups = list_backups()
    
    return render_template('admin.html',
                         total_users=total_users,
                         total_documents=total_documents,
                         recent_activity=recent_activity,
                         recent_users=recent_users,
                         recent_documents=recent_documents,
                         backups=backups[:5])  # Show only 5 most recent backups

@admin_bp.route('/admin/users')
@login_required
def manage_users():
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'document_count': len(user.documents)
        })
    
    return jsonify({'users': users_data})

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_user(user_id):
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        if 'role' in data:
            user.role = data['role']
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    
    elif request.method == 'DELETE':
        # Don't allow deleting own account
        if user.id == current_user.id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        # Delete user's documents first
        Document.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

@admin_bp.route('/admin/activities')
@login_required
def user_activities():
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    # Get recent document uploads as activities
    recent_docs = Document.query.order_by(Document.upload_date.desc()).limit(50).all()
    activities = []
    
    for doc in recent_docs:
        activities.append({
            'user': doc.uploader.username if doc.uploader else 'Unknown',
            'action': 'uploaded',
            'document': doc.filename,
            'timestamp': doc.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'document_upload'
        })
    
    return jsonify({'activities': activities})

@admin_bp.route('/admin/backup', methods=['POST', 'GET'])
@login_required
def backup_management():
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    if request.method == 'POST':
        data = request.get_json()
        backup_type = data.get('type', 'full')
        
        result = create_backup(backup_type)
        return jsonify(result)
    
    elif request.method == 'GET':
        backups = list_backups()
        return jsonify({'backups': backups})

@admin_bp.route('/admin/backup/<path:backup_name>', methods=['DELETE', 'POST'])
@login_required
def manage_backup(backup_name):
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    backup_dir = os.path.join(current_app.root_path, '..', 'backups')
    backup_path = os.path.join(backup_dir, backup_name)
    
    if request.method == 'DELETE':
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return jsonify({'success': True, 'message': f'Backup {backup_name} deleted'})
            else:
                return jsonify({'success': False, 'message': 'Backup not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        # Restore backup
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404
        
        result = restore_backup(backup_path)
        return jsonify(result)

@admin_bp.route('/admin/backup/cleanup', methods=['POST'])
@login_required
def cleanup_backups():
    if not is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    max_backups = data.get('max_backups', 10)
    
    result = cleanup_old_backups(max_backups)
    return jsonify(result)

@admin_bp.route('/admin/backup/download/<path:backup_name>')
@login_required
def download_backup(backup_name):
    if not is_admin():
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('search.home'))
    
    backup_dir = os.path.join(current_app.root_path, '..', 'backups')
    backup_path = os.path.join(backup_dir, backup_name)
    
    if not os.path.exists(backup_path):
        flash("Backup file not found.", "error")
        return redirect(url_for('admin.admin_dashboard'))
    
    return send_file(backup_path, as_attachment=True)