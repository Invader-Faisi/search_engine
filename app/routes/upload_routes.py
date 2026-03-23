from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.file_service import save_file, get_user_files
from app.services.indexing_service import index_document
from app.models.document_model import Document

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    message = ""
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected!", "error")
            return redirect(url_for("upload.upload"))

        existing_file = Document.query.filter_by(user_id=current_user.id, filename=file.filename).first()
        if existing_file:
            flash(f"A file named '{file.filename}' already exists!", "error")
            return redirect(url_for("upload.upload"))

        document = save_file(file, user_id=current_user.id)
        if document:
            index_document(document.filename, document.filepath)
            flash("File uploaded and indexed successfully!", "success")
        else:
            flash("Invalid file type! Only CSV and TXT are allowed.", "error")

        return redirect(url_for("upload.upload"))

    files = get_user_files(current_user.id)
    return render_template("upload.html", files=files)