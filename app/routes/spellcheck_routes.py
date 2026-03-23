from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.spellcheck_service import check_text, add_custom_words, get_custom_words, remove_custom_word

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

@spell_bp.route('/spellcheck/custom-words', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_custom_words():
    """Manage custom dictionary words for the current user"""
    try:
        if request.method == 'GET':
            # Get all custom words
            words = get_custom_words()
            return jsonify({'words': words})
        
        elif request.method == 'POST':
            # Add new custom words
            data = request.get_json()
            words = data.get('words', [])
            if isinstance(words, str):
                words = [words]
            
            updated_words = add_custom_words(words)
            return jsonify({
                'message': f'Added {len(words)} word(s) to custom dictionary',
                'words': updated_words
            })
        
        elif request.method == 'DELETE':
            # Remove a custom word
            data = request.get_json()
            word = data.get('word', '')
            if not word:
                return jsonify({'error': 'No word provided'}), 400
            
            updated_words = remove_custom_word(word)
            return jsonify({
                'message': f'Removed "{word}" from custom dictionary',
                'words': updated_words
            })
    
    except Exception as e:
        print("Custom words error:", e)
        return jsonify({"error": str(e)}), 500