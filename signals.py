# signals.py
import re
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class TextSignals:
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    unique_word_ratio: float
    repeated_phrases: List[str]
    pause_markers: int
    total_chars: int

def compute_signals(text: str) -> TextSignals:
    text = text.strip()
    words = re.sub(r"[^a-z0-9'\s]", " ", text.lower()).split()
    words = [w for w in words if w]

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 3]
    sentence_count = max(len(sentences), 1)
    word_count = len(words)
    avg_wps = round(word_count / sentence_count, 1)

    unique_ratio = round(len(set(words)) / word_count, 2) if word_count > 0 else 0

    # Repeated bigrams/trigrams (stop-word filtered)
    stop = {"the","a","an","and","or","but","in","on","at","to","for","of","with","is","was","i","it"}
    phrase_counts = Counter()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            chunk = words[i:i+n]
            if any(w not in stop for w in chunk):
                phrase_counts[" ".join(chunk)] += 1
    repeated = [p for p, c in phrase_counts.most_common(5) if c >= 2]

    pauses = len(re.findall(r'…|\.{3}|—|--|um|uh', text, re.IGNORECASE))

    return TextSignals(word_count, sentence_count, avg_wps,
                       unique_ratio, repeated, pauses, len(text))

def compare_to_baseline(signals: TextSignals, baseline: dict) -> dict:
    base_words = max(baseline["avg_word_count"], 1)
    return {
        "word_count_delta": round(((signals.word_count - baseline["avg_word_count"]) / base_words) * 100, 1),
        "unique_ratio_delta": round(signals.unique_word_ratio - baseline["avg_unique_ratio"], 2),
        "sentence_length_delta": round(signals.avg_words_per_sentence - baseline["avg_words_per_sentence"], 1),
    }

def compute_baseline(texts: list) -> dict:
    all_signals = [compute_signals(t) for t in texts]
    n = len(all_signals)
    return {
        "avg_word_count": round(sum(s.word_count for s in all_signals) / n),
        "avg_sentence_count": round(sum(s.sentence_count for s in all_signals) / n),
        "avg_unique_ratio": round(sum(s.unique_word_ratio for s in all_signals) / n, 2),
        "avg_words_per_sentence": round(sum(s.avg_words_per_sentence for s in all_signals) / n, 1),
        "sample_count": n,
    }