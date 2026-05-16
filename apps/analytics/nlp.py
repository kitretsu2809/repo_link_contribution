import spacy
from collections import Counter
import re
import nltk
from nltk.tokenize import word_tokenize

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spacy en_core_web_sm not found.")

def analyze_readme_quality(readme_text):
    if not readme_text:
        return 0.0

    score = 0.0
    text_lower = readme_text.lower()
    
    # 1. Check for code blocks (indicates examples/usage)
    if "```" in readme_text:
        score += 30.0

    # 2. Check for key sections
    key_sections = ["install", "usage", "contribut", "license", "documentation", "getting started"]
    found_sections = sum(1 for section in key_sections if section in text_lower)
    score += (found_sections / len(key_sections)) * 40.0

    # 3. Readability / Length check (not too short)
    try:
        tokens = word_tokenize(readme_text)
        if len(tokens) > 200:
            score += 15.0
        elif len(tokens) > 50:
            score += 5.0
    except Exception:
        if len(readme_text) > 1000:
            score += 15.0

    # 4. Check for badges
    if "[!" in readme_text or "<img src=" in readme_text:
        score += 15.0

    return min(100.0, score)

def extract_topics(readme_text):
    if not readme_text:
        return []
    
    # Basic keyword extraction using spaCy
    try:
        doc = nlp(readme_text[:5000]) # Limit to 5000 chars for speed
        keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop and len(token) > 2]
        common = Counter(keywords).most_common(5)
        return [k[0] for k in common]
    except Exception:
        return []
