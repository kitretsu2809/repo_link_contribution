"""
Extractive AI summarizer for GitHub issues.
Uses spaCy sentence segmentation + TF-IDF style word frequency scoring
to pick the most informative sentences from an issue's title + body.
No external API required — runs fully offline.
"""
import re
from collections import Counter


def _clean(text: str) -> str:
    """Strip markdown, code blocks, and URLs."""
    text = re.sub(r'```[\s\S]*?```', '', text)      # fenced code blocks
    text = re.sub(r'`[^`]+`', '', text)              # inline code
    text = re.sub(r'https?://\S+', '', text)         # URLs
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)      # images
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)       # links
    text = re.sub(r'#{1,6}\s', '', text)             # headings
    text = re.sub(r'[*_~]{1,2}', '', text)           # bold/italic
    text = re.sub(r'\s+', ' ', text)                 # collapse whitespace
    return text.strip()


def _split_sentences(text: str):
    """Simple sentence splitter — works without spaCy."""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
        nlp.add_pipe('sentencizer')
        doc = nlp(text[:5000])
        return [s.text.strip() for s in doc.sents if len(s.text.strip()) > 20]
    except Exception:
        # Fallback: split on common sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]


def _score_sentences(sentences, word_freq):
    """Score each sentence by the sum of word frequencies it contains."""
    scores = {}
    for i, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-z]{3,}\b', sentence.lower())
        scores[i] = sum(word_freq.get(w, 0) for w in words)
    return scores


def summarize_issue(title: str, body: str, max_sentences: int = 3) -> str:
    """
    Generate a concise AI summary of a GitHub issue.

    Args:
        title: The issue title.
        body: The issue body (markdown).
        max_sentences: Number of sentences to include in the summary.

    Returns:
        A plain-text summary string.
    """
    if not body or len(body.strip()) < 50:
        # Body is too short — just return the title as summary
        return title.strip()

    # Combine title + cleaned body
    full_text = f"{title}. {_clean(body)}"

    sentences = _split_sentences(full_text)
    if not sentences:
        return title.strip()

    if len(sentences) <= max_sentences:
        return ' '.join(sentences)

    # Build word frequency map (stopwords excluded)
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'is', 'it', 'this', 'that', 'are', 'was',
        'be', 'by', 'from', 'as', 'not', 'have', 'has', 'had', 'when',
        'i', 'we', 'you', 'he', 'she', 'they', 'my', 'your', 'our',
        'which', 'what', 'how', 'if', 'so', 'do', 'did', 'will', 'would',
        'can', 'could', 'should', 'would', 'also', 'just', 'more', 'than',
    }
    all_words = re.findall(r'\b[a-z]{3,}\b', full_text.lower())
    word_freq = Counter(w for w in all_words if w not in STOPWORDS)

    # Normalise frequencies to 0-1
    max_freq = max(word_freq.values()) if word_freq else 1
    word_freq = {w: c / max_freq for w, c in word_freq.items()}

    scores = _score_sentences(sentences, word_freq)

    # Always include the first sentence (usually most context-rich)
    top_indices = sorted(scores, key=scores.get, reverse=True)[:max_sentences]
    top_indices = sorted(set([0] + top_indices))[:max_sentences]

    summary = ' '.join(sentences[i] for i in top_indices)
    return summary.strip()
