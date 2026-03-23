from flask import Blueprint, render_template, request, send_file, abort, current_app
from flask_login import current_user
from app.services.search_service import search_documents
from app.services.activity_service import log_activity, log_document_access
from app.models.document_model import Document
import os

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET', 'POST'])
def home():
    results = []

    if request.method == 'POST':
        query = request.form['query']
        results = search_documents(query)
        
        # Log search activity
        if current_user.is_authenticated:
            log_activity(
                activity_type='search',
                description=f'Searched for: {query}',
                user_id=current_user.id
            )
            
            # Log document accesses for search results
            for result in results:
                # Find document by path
                doc = Document.query.filter_by(filepath=result['path']).first()
                if doc:
                    log_document_access(
                        user_id=current_user.id,
                        document_id=doc.id,
                        action='search',
                        search_query=query
                    )
        else:
            # Log anonymous search
            log_activity(
                activity_type='search',
                description=f'Anonymous search: {query}',
                user_id=None
            )

    return render_template('index.html', results=results)


@search_bp.route("/view")
def view_document():
    rel_path = request.args.get("path")
    if not rel_path:
        abort(400, "Missing file path")

    project_root = os.path.dirname(current_app.root_path)
    filepath = os.path.join(project_root, rel_path)
    filepath = os.path.abspath(filepath)

    upload_folder = os.path.abspath(os.path.join(project_root, "data", "uploads"))
    if not filepath.startswith(upload_folder + os.sep):
        abort(403, "Unauthorized access")

    if not os.path.exists(filepath):
        abort(404, "File not found")
    
    # Log document view activity
    if current_user.is_authenticated:
        # Find document by path
        doc = Document.query.filter_by(filepath=rel_path).first()
        if doc:
            log_activity(
                activity_type='view',
                description=f'Viewed document: {doc.filename}',
                document_id=doc.id,
                user_id=current_user.id
            )
            log_document_access(
                user_id=current_user.id,
                document_id=doc.id,
                action='view'
            )

    return send_file(filepath, as_attachment=False)


@search_bp.route("/download")
def download_document():
    rel_path = request.args.get("path")
    if not rel_path:
        abort(400, "Missing file path")

    project_root = os.path.dirname(current_app.root_path)
    filepath = os.path.join(project_root, rel_path)
    filepath = os.path.abspath(filepath)

    upload_folder = os.path.abspath(os.path.join(project_root, "data", "uploads"))
    if not filepath.startswith(upload_folder + os.sep):
        abort(403, "Unauthorized access")

    if not os.path.exists(filepath):
        abort(404, "File not found")
    
    # Log document download activity
    if current_user.is_authenticated:
        doc = Document.query.filter_by(filepath=rel_path).first()
        if doc:
            log_activity(
                activity_type='download',
                description=f'Downloaded document: {doc.filename}',
                document_id=doc.id,
                user_id=current_user.id
            )
            log_document_access(
                user_id=current_user.id,
                document_id=doc.id,
                action='download'
            )

    return send_file(filepath, as_attachment=True)
