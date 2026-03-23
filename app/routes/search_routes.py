from flask import Blueprint, render_template, request, send_file, abort, current_app
from app.services.search_service import search_documents
import os

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET', 'POST'])
def home():
    results = []

    if request.method == 'POST':
        query = request.form['query']
        results = search_documents(query)

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

    return send_file(filepath, as_attachment=True)
