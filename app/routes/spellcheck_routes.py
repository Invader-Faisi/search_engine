from flask import Blueprint, request, jsonify
from app.services.spellcheck_service import check_text

spell_bp = Blueprint('spell', __name__)

@spell_bp.route('/spellcheck', methods=['POST'])
def spellcheck():
    try:
        data = request.get_json(force=True)  # force=True ensures JSON is parsed
        text = data.get('text', '')

        suggestions = check_text(text)
        print("Suggestions:", suggestions)
        return jsonify(suggestions)
    except Exception as e:
        print("Spellcheck error:", e)
        return jsonify({"error": str(e)}), 500