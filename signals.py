# signals.py
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List

@dataclass
class TextSignals:
    # Volume
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    total_chars: int

    # Lexical richness
    unique_word_ratio: float          # type-token ratio
    filler_word_ratio: float          # filler words per total words
    content_word_ratio: float         # non-stopword proportion

    # Repetition
    repeated_phrases: List[str]       # bigrams/trigrams appearing 2+ times
    phrase_repetition_score: float    # 0-1, higher = more repetitive

    # Coherence / structure
    avg_sentence_length_variance: float
    incomplete_sentences: int         # sentences < 4 words
    question_marks: int
    exclamation_marks: int

    # Hesitation / uncertainty
    pause_markers: int                # ellipsis, dashes, um, uh
    uncertainty_markers: int          # "I think", "maybe", "I don't know"
    negation_count: int

    # Temporal orientation
    past_tense_ratio: float
    present_tense_ratio: float

    # Computed risk score (0-100, algorithmic)
    risk_score: float


STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","was","i","it","he","she","they","we","you","my","his","her","its",
    "this","that","these","those","be","been","being","have","has","had",
    "do","does","did","will","would","could","should","may","might","am","are","were"
}

FILLER_RE = re.compile(
    r'\b(um|uh|like|you know|kind of|sort of|basically|literally|actually|'
    r'i mean|you see|right|okay|so|well|just)\b', re.IGNORECASE
)
UNCERTAINTY_RE = re.compile(
    r'\b(i think|i guess|maybe|perhaps|not sure|i don\'t know|i forget|'
    r'i can\'t remember|i don\'t remember|i\'m not sure|i\'m trying|'
    r'what was it|hard to say|i believe|i suppose)\b', re.IGNORECASE
)
NEGATION_RE = re.compile(
    r'\b(no|not|never|nothing|nobody|nowhere|neither|nor|none|'
    r'didn\'t|don\'t|doesn\'t|wasn\'t|weren\'t|can\'t|couldn\'t|'
    r'wouldn\'t|shouldn\'t|won\'t|hadn\'t|isn\'t|aren\'t)\b', re.IGNORECASE
)
PAST_TENSE_RE = re.compile(
    r'\b(was|were|had|went|did|said|got|came|saw|made|took|knew|'
    r'thought|felt|seemed|looked|used|walked|talked|ate|drank|slept|'
    r'woke|drove|called|helped|tried|worked|played|visited|remembered)\b', re.IGNORECASE
)
PRESENT_TENSE_RE = re.compile(
    r'\b(is|are|am|have|has|go|do|does|say|says|get|gets|come|comes|'
    r'see|sees|make|makes|take|takes|know|knows|think|thinks|feel|feels|'
    r'walk|walks|talk|talks|eat|eats|drink|drinks|sleep|sleeps)\b', re.IGNORECASE
)


def compute_signals(text: str) -> TextSignals:
    text = text.strip()
    if not text:
        return _empty_signals()

    words_raw = re.sub(r"[^a-z0-9'\s]", " ", text.lower()).split()
    words = [w for w in words_raw if w]
    word_count = len(words)
    if word_count == 0:
        return _empty_signals()

    # Sentences
    raw_sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentences = raw_sentences if raw_sentences else [text]
    sentence_count = len(sentences)
    sent_lengths = [len(s.split()) for s in sentences]
    avg_wps = round(sum(sent_lengths) / sentence_count, 1)
    incomplete = sum(1 for l in sent_lengths if l < 4)
    variance = round(
        sum((l - avg_wps) ** 2 for l in sent_lengths) / sentence_count, 1
    ) if sentence_count > 1 else 0.0

    # Lexical richness
    unique_ratio = round(len(set(words)) / word_count, 3)
    content_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    content_word_ratio = round(len(content_words) / word_count, 3)
    filler_hits = FILLER_RE.findall(text)
    filler_ratio = round(len(filler_hits) / word_count, 3)

    # Repetition
    phrase_counts = Counter()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            chunk = words[i:i+n]
            if sum(1 for w in chunk if w not in STOP_WORDS) >= 1:
                phrase_counts[" ".join(chunk)] += 1
    repeated = [p for p, c in phrase_counts.most_common(8) if c >= 2]
    repetition_score = round(min(len(repeated) / max(word_count / 5, 1), 1.0), 3)

    # Markers
    pauses = len(re.findall(r'…|\.{3}|—|--|um\b|uh\b', text, re.IGNORECASE))
    uncertainty = len(UNCERTAINTY_RE.findall(text))
    negations = len(NEGATION_RE.findall(text))

    # Punctuation
    q_marks = text.count('?')
    e_marks = text.count('!')

    # Tense
    past_hits = len(PAST_TENSE_RE.findall(text))
    pres_hits = len(PRESENT_TENSE_RE.findall(text))
    verb_total = max(past_hits + pres_hits, 1)
    past_ratio = round(past_hits / verb_total, 3)
    pres_ratio = round(pres_hits / verb_total, 3)

    risk = _compute_risk_score(
        unique_ratio, filler_ratio, repetition_score, pauses,
        uncertainty, negations, incomplete, sentence_count, word_count
    )

    return TextSignals(
        word_count=word_count,
        sentence_count=sentence_count,
        avg_words_per_sentence=avg_wps,
        total_chars=len(text),
        unique_word_ratio=unique_ratio,
        filler_word_ratio=filler_ratio,
        content_word_ratio=content_word_ratio,
        repeated_phrases=repeated,
        phrase_repetition_score=repetition_score,
        avg_sentence_length_variance=variance,
        incomplete_sentences=incomplete,
        question_marks=q_marks,
        exclamation_marks=e_marks,
        pause_markers=pauses,
        uncertainty_markers=uncertainty,
        negation_count=negations,
        past_tense_ratio=past_ratio,
        present_tense_ratio=pres_ratio,
        risk_score=risk,
    )


def _compute_risk_score(unique_ratio, filler_ratio, repetition_score,
                        pauses, uncertainty, negations, incomplete,
                        sentence_count, word_count) -> float:
    score = 0.0

    # Low vocabulary diversity
    if unique_ratio < 0.45:   score += 28
    elif unique_ratio < 0.55: score += 16
    elif unique_ratio < 0.65: score += 8

    # High filler word usage
    if filler_ratio > 0.10:  score += 22
    elif filler_ratio > 0.06: score += 13
    elif filler_ratio > 0.03: score += 6

    # Phrase repetition
    score += repetition_score * 22

    # Hesitations / pauses
    if pauses >= 5:   score += 16
    elif pauses >= 3: score += 9
    elif pauses >= 1: score += 4

    # Uncertainty markers
    if uncertainty >= 3:   score += 16
    elif uncertainty >= 2: score += 10
    elif uncertainty >= 1: score += 5

    # Negation (elevated negative framing)
    if negations >= 6:   score += 8
    elif negations >= 3: score += 4

    # Very short or fragmented responses
    if word_count < 15:   score += 12
    elif word_count < 25: score += 6
    if incomplete >= 3:   score += 8
    elif incomplete >= 1: score += 4

    return round(min(score, 100), 1)


def _empty_signals() -> TextSignals:
    return TextSignals(
        word_count=0, sentence_count=0, avg_words_per_sentence=0,
        total_chars=0, unique_word_ratio=0, filler_word_ratio=0,
        content_word_ratio=0, repeated_phrases=[], phrase_repetition_score=0,
        avg_sentence_length_variance=0, incomplete_sentences=0,
        question_marks=0, exclamation_marks=0, pause_markers=0,
        uncertainty_markers=0, negation_count=0, past_tense_ratio=0,
        present_tense_ratio=0, risk_score=0
    )


def compare_to_baseline(signals: TextSignals, baseline: dict) -> dict:
    base_words = max(baseline["avg_word_count"], 1)

    wc_delta       = round(((signals.word_count - baseline["avg_word_count"]) / base_words) * 100, 1)
    ur_delta       = round(signals.unique_word_ratio - baseline["avg_unique_ratio"], 3)
    sl_delta       = round(signals.avg_words_per_sentence - baseline["avg_words_per_sentence"], 1)
    filler_delta   = round(signals.filler_word_ratio - baseline.get("avg_filler_ratio", 0), 3)
    rep_delta      = round(signals.phrase_repetition_score - baseline.get("avg_repetition_score", 0), 3)
    risk_delta     = round(signals.risk_score - baseline.get("avg_risk_score", 0), 1)
    uncert_delta   = signals.uncertainty_markers - round(baseline.get("avg_uncertainty_markers", 0))
    pause_delta    = signals.pause_markers - round(baseline.get("avg_pause_markers", 0))

    caution_hint = _compute_caution_hint(
        wc_delta, ur_delta, filler_delta, rep_delta,
        risk_delta, uncert_delta, pause_delta, signals
    )

    return {
        "word_count_delta":    wc_delta,
        "unique_ratio_delta":  ur_delta,
        "sentence_length_delta": sl_delta,
        "filler_ratio_delta":  filler_delta,
        "repetition_delta":    rep_delta,
        "risk_score_delta":    risk_delta,
        "uncertainty_delta":   uncert_delta,
        "pause_delta":         pause_delta,
        "caution_hint":        caution_hint,
    }


def _compute_caution_hint(wc_delta, ur_delta, filler_delta, rep_delta,
                          risk_delta, uncert_delta, pause_delta, signals) -> str:
    """
    Returns 'low', 'moderate', or 'watch'.
    Uses a weighted flag system — 1 watch_flag OR 2 moderate_flags = moderate,
    2 watch_flags = watch.
    """
    watch_flags = 0
    moderate_flags = 0

    # Word count change
    if wc_delta <= -40:    watch_flags += 1
    elif wc_delta <= -20:  moderate_flags += 1

    # Vocabulary drop
    if ur_delta <= -0.12:   watch_flags += 1
    elif ur_delta <= -0.06: moderate_flags += 1

    # Filler word spike
    if filler_delta >= 0.07:   watch_flags += 1
    elif filler_delta >= 0.03: moderate_flags += 1

    # Repetition spike
    if rep_delta >= 0.20:   watch_flags += 1
    elif rep_delta >= 0.10: moderate_flags += 1

    # Risk score jump vs baseline
    if risk_delta >= 25:   watch_flags += 1
    elif risk_delta >= 12: moderate_flags += 1

    # Uncertainty markers spike
    if uncert_delta >= 3:   watch_flags += 1
    elif uncert_delta >= 1: moderate_flags += 1

    # Pause markers spike
    if pause_delta >= 3:   watch_flags += 1
    elif pause_delta >= 1: moderate_flags += 1

    # Absolute: high raw risk regardless of baseline comparison
    if signals.risk_score >= 55:   watch_flags += 1
    elif signals.risk_score >= 30: moderate_flags += 1

    if watch_flags >= 2:
        return "watch"
    elif watch_flags == 1 or moderate_flags >= 2:
        return "moderate"
    else:
        return "low"


def score_caution(signals: TextSignals, deltas: dict):
    """Return (caution_level, flags, score).

    - caution_level: low/moderate/watch (from deltas with fallback to algorithm)
    - flags: list of active caution flags
    - score: raw risk score 0-100
    """
    caution_level = deltas.get("caution_hint") or _compute_caution_hint(
        deltas.get("word_count_delta", 0),
        deltas.get("unique_ratio_delta", 0),
        deltas.get("filler_ratio_delta", 0),
        deltas.get("repetition_delta", 0),
        deltas.get("risk_score_delta", 0),
        deltas.get("uncertainty_delta", 0),
        deltas.get("pause_delta", 0),
        signals
    )

    flags = []
    if deltas.get("word_count_delta", 0) <= -40:
        flags.append("word_count_drop_40")
    if deltas.get("unique_ratio_delta", 0) <= -0.12:
        flags.append("unique_ratio_drop_0_12")
    if deltas.get("filler_ratio_delta", 0) >= 0.07:
        flags.append("filler_spike_0_07")
    if deltas.get("repetition_delta", 0) >= 0.20:
        flags.append("repetition_spike_0_20")
    if deltas.get("risk_score_delta", 0) >= 25:
        flags.append("risk_score_jump_25")
    if deltas.get("uncertainty_delta", 0) >= 3:
        flags.append("uncertainty_spike_3")
    if deltas.get("pause_delta", 0) >= 3:
        flags.append("pause_spike_3")
    if signals.risk_score >= 55:
        flags.append("high_risk_score")

    return caution_level, flags, round(signals.risk_score, 1)


def compute_baseline(texts: list) -> dict:
    all_signals = [compute_signals(t) for t in texts]
    n = len(all_signals)

    def avg(fn):
        return round(sum(fn(s) for s in all_signals) / n, 3)

    return {
        "avg_word_count":           round(avg(lambda s: s.word_count)),
        "avg_sentence_count":       round(avg(lambda s: s.sentence_count)),
        "avg_unique_ratio":         avg(lambda s: s.unique_word_ratio),
        "avg_words_per_sentence":   avg(lambda s: s.avg_words_per_sentence),
        "avg_filler_ratio":         avg(lambda s: s.filler_word_ratio),
        "avg_content_ratio":        avg(lambda s: s.content_word_ratio),
        "avg_repetition_score":     avg(lambda s: s.phrase_repetition_score),
        "avg_pause_markers":        avg(lambda s: s.pause_markers),
        "avg_uncertainty_markers":  avg(lambda s: s.uncertainty_markers),
        "avg_risk_score":           avg(lambda s: s.risk_score),
        "sample_count":             n,
    }
