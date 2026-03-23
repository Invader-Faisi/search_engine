from spellchecker import SpellChecker
import os
import json

# Initialize spell checker
spell = SpellChecker()

# File to store custom words
CUSTOM_WORDS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'custom_words.json')

def load_custom_words():
    """Load custom words from file"""
    custom_words = []
    try:
        if os.path.exists(CUSTOM_WORDS_FILE):
            with open(CUSTOM_WORDS_FILE, 'r') as f:
                data = json.load(f)
                custom_words = data.get('words', [])
                for word in custom_words:
                    spell.word_frequency.add(word)
    except Exception as e:
        print(f"Error loading custom words: {e}")
    return custom_words

def save_custom_words(custom_words):
    """Save custom words to file"""
    try:
        os.makedirs(os.path.dirname(CUSTOM_WORDS_FILE), exist_ok=True)
        with open(CUSTOM_WORDS_FILE, 'w') as f:
            json.dump({'words': custom_words}, f)
    except Exception as e:
        print(f"Error saving custom words: {e}")

# Load existing custom words on startup
custom_words = load_custom_words()

def add_custom_words(words):
    """Add new custom words to dictionary"""
    global custom_words
    for w in words:
        w_lower = w.lower().strip()
        if w_lower and w_lower not in custom_words:
            spell.word_frequency.add(w_lower)
            custom_words.append(w_lower)
    save_custom_words(custom_words)
    return custom_words

def get_custom_words():
    """Get list of all custom words"""
    return custom_words

def remove_custom_word(word):
    """Remove a custom word from dictionary"""
    global custom_words
    word_lower = word.lower().strip()
    if word_lower in custom_words:
        custom_words.remove(word_lower)
        # Note: spellchecker doesn't support removing words from frequency
        # We'll reload the spellchecker without this word
        spell.word_frequency.remove(word_lower)
        save_custom_words(custom_words)
    return custom_words

def check_text(text):
    """
    Returns a dictionary of misspelled words -> suggestions (as lists)
    """
    if not text:
        return {}

    words = text.split()
    misspelled = spell.unknown(words)

    suggestions = {}
    for word in misspelled:
        # convert set to list for JSON
        suggestions[word] = list(spell.candidates(word))

    return suggestions