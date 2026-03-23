from spellchecker import SpellChecker

spell = SpellChecker()
custom_words = []

def add_custom_words(words):
    for w in words:
        spell.word_frequency.add(w)
        custom_words.append(w)

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