import os
import shutil
import zipfile
from datetime import datetime
from flask import current_app
import sqlite3

def create_backup(backup_type='full'):
    """
    Create a backup of the system
    backup_type: 'full' (database + uploads + index) or 'db' (database only)
    """
    try:
        # Create backup directory
        backup_dir = os.path.join(current_app.root_path, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{backup_type}_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        if backup_type == 'full':
            # Create zip file with all data
            zip_path = backup_path + '.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup database
                db_path = os.path.join(current_app.root_path, '..', 'database', 'app.db')
                if os.path.exists(db_path):
                    zipf.write(db_path, 'database/app.db')
                
                # Backup uploads directory
                uploads_path = os.path.join(current_app.root_path, '..', 'data', 'uploads')
                if os.path.exists(uploads_path):
                    for root, dirs, files in os.walk(uploads_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.join(current_app.root_path, '..'))
                            zipf.write(file_path, arcname)
                
                # Backup index directory
                index_path = os.path.join(current_app.root_path, '..', 'data', 'index')
                if os.path.exists(index_path):
                    for root, dirs, files in os.walk(index_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.join(current_app.root_path, '..'))
                            zipf.write(file_path, arcname)
                
                # Backup custom words
                custom_words_path = os.path.join(current_app.root_path, '..', 'data', 'custom_words.json')
                if os.path.exists(custom_words_path):
                    zipf.write(custom_words_path, 'data/custom_words.json')
            
            backup_size = os.path.getsize(zip_path)
            return {
                'success': True,
                'message': f'Full backup created: {backup_name}.zip',
                'path': zip_path,
                'size': backup_size,
                'type': 'full'
            }
        
        elif backup_type == 'db':
            # Database backup only
            db_path = os.path.join(current_app.root_path, '..', 'database', 'app.db')
            backup_db_path = backup_path + '.db'
            
            # Copy database file
            shutil.copy2(db_path, backup_db_path)
            
            backup_size = os.path.getsize(backup_db_path)
            return {
                'success': True,
                'message': f'Database backup created: {backup_name}.db',
                'path': backup_db_path,
                'size': backup_size,
                'type': 'db'
            }
        
        else:
            return {
                'success': False,
                'message': f'Unknown backup type: {backup_type}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Backup failed: {str(e)}'
        }

def list_backups():
    """List all available backups"""
    backup_dir = os.path.join(current_app.root_path, '..', 'backups')
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            backups.append({
                'name': filename,
                'path': filepath,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'full' if filename.endswith('.zip') else 'db'
            })
    
    # Sort by creation time (newest first)
    backups.sort(key=lambda x: x['created'], reverse=True)
    return backups

def restore_backup(backup_path):
    """Restore from a backup file"""
    try:
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'message': 'Backup file not found'
            }
        
        if backup_path.endswith('.zip'):
            # Full backup restore
            backup_dir = os.path.dirname(backup_path)
            extract_dir = os.path.join(backup_dir, 'temp_restore')
            
            # Extract zip
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Restore database
            db_backup_path = os.path.join(extract_dir, 'database', 'app.db')
            if os.path.exists(db_backup_path):
                db_target_path = os.path.join(current_app.root_path, '..', 'database', 'app.db')
                shutil.copy2(db_backup_path, db_target_path)
            
            # Restore uploads
            uploads_backup_dir = os.path.join(extract_dir, 'data', 'uploads')
            if os.path.exists(uploads_backup_dir):
                uploads_target_dir = os.path.join(current_app.root_path, '..', 'data', 'uploads')
                # Clear existing uploads
                if os.path.exists(uploads_target_dir):
                    shutil.rmtree(uploads_target_dir)
                shutil.copytree(uploads_backup_dir, uploads_target_dir)
            
            # Restore index
            index_backup_dir = os.path.join(extract_dir, 'data', 'index')
            if os.path.exists(index_backup_dir):
                index_target_dir = os.path.join(current_app.root_path, '..', 'data', 'index')
                # Clear existing index
                if os.path.exists(index_target_dir):
                    shutil.rmtree(index_target_dir)
                shutil.copytree(index_backup_dir, index_target_dir)
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
            return {
                'success': True,
                'message': 'Full backup restored successfully'
            }
        
        elif backup_path.endswith('.db'):
            # Database backup restore
            db_target_path = os.path.join(current_app.root_path, '..', 'database', 'app.db')
            shutil.copy2(backup_path, db_target_path)
            
            return {
                'success': True,
                'message': 'Database backup restored successfully'
            }
        
        else:
            return {
                'success': False,
                'message': 'Unsupported backup file format'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Restore failed: {str(e)}'
        }

def cleanup_old_backups(max_backups=10):
    """Keep only the most recent backups, delete older ones"""
    backups = list_backups()
    if len(backups) <= max_backups:
        return {
            'success': True,
            'message': f'No cleanup needed. Current backups: {len(backups)}'
        }
    
    # Sort by creation time (oldest first)
    backups.sort(key=lambda x: x['created'])
    
    deleted = 0
    for i in range(len(backups) - max_backups):
        try:
            os.remove(backups[i]['path'])
            deleted += 1
        except Exception as e:
            print(f"Error deleting backup {backups[i]['name']}: {e}")
    
    return {
        'success': True,
        'message': f'Deleted {deleted} old backups. Kept {max_backups} most recent.',
        'deleted': deleted
    }