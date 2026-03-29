# claude_client.py
import anthropic, json, os
from dataclasses import asdict
from signals import TextSignals

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _trend_summary(recent_history: list) -> str:
    if not recent_history:
        return "No previous history — this is the first entry."
    lines = []
    for e in recent_history[-7:]:
        s = e["signals"]
        caution = e.get("analysis", {}).get("caution_level", "?")
        lines.append(
            f"  {e['date'][:10]}: {s['word_count']} words, "
            f"vocab={s['unique_word_ratio']}, "
            f"fillers={s.get('filler_word_ratio','?')}, "
            f"risk={s.get('risk_score','?')}, "
            f"level={caution}"
        )
    return "\n".join(lines)


def _risk_band(score: float) -> str:
    if score >= 55: return "HIGH"
    if score >= 35: return "MODERATE"
    if score >= 15: return "LOW-MODERATE"
    return "LOW"


def build_prompt(text, signals: TextSignals, baseline: dict, deltas: dict, recent_history: list) -> str:
    trend = _trend_summary(recent_history)
    caution_hint = deltas.get("caution_hint", "low")
    risk_band = _risk_band(signals.risk_score)

    interpretations = []

    wc = deltas["word_count_delta"]
    if wc <= -40:   interpretations.append(f"Word count DOWN {abs(wc):.0f}% vs baseline — major drop in verbal output.")
    elif wc <= -20: interpretations.append(f"Word count down {abs(wc):.0f}% vs baseline — noticeably less speech than usual.")
    elif wc >= 30:  interpretations.append(f"Word count up {wc:.0f}% vs baseline — more verbal than usual.")
    else:           interpretations.append(f"Word count near baseline ({wc:+.0f}%).")

    ur = deltas["unique_ratio_delta"]
    if ur <= -0.12:   interpretations.append(f"Vocabulary diversity dropped sharply ({ur:+.3f}) — fewer distinct words, possible narrowing of expression.")
    elif ur <= -0.06: interpretations.append(f"Vocabulary diversity somewhat lower than baseline ({ur:+.3f}).")
    elif ur >= 0.06:  interpretations.append(f"Vocabulary diversity higher than baseline ({ur:+.3f}) — richer language today.")
    else:             interpretations.append(f"Vocabulary diversity close to baseline ({ur:+.3f}).")

    fr = deltas.get("filler_ratio_delta", 0)
    if fr >= 0.07:    interpretations.append(f"Filler words spiked significantly (+{fr:.3f}) — 'um', 'uh', 'you know', 'like' much more than usual.")
    elif fr >= 0.03:  interpretations.append(f"Filler word usage moderately elevated (+{fr:.3f}).")
    elif fr <= -0.03: interpretations.append(f"Filler word usage lower than baseline — more fluent than usual.")

    rep = deltas.get("repetition_delta", 0)
    if rep >= 0.20:   interpretations.append(f"Phrase repetition is high (+{rep:.2f}) — same phrases appearing repeatedly.")
    elif rep >= 0.10: interpretations.append(f"Some increase in phrase repetition ({rep:+.2f}).")

    ud = deltas.get("uncertainty_delta", 0)
    if ud >= 3:    interpretations.append(f"Uncertainty language spiked (+{ud}) — 'I think', 'I forget', 'I'm not sure' much more frequent.")
    elif ud >= 1:  interpretations.append(f"Slight increase in uncertainty language (+{ud}).")

    pd = deltas.get("pause_delta", 0)
    if pd >= 3:   interpretations.append(f"Hesitation markers spiked (+{pd}) — more pauses or fillers than usual.")
    elif pd >= 1: interpretations.append(f"Slightly more hesitation markers than baseline (+{pd}).")

    if signals.risk_score >= 55:
        interpretations.append(f"Absolute risk score {signals.risk_score}/100 is HIGH on its own.")
    elif signals.risk_score >= 35:
        interpretations.append(f"Absolute risk score {signals.risk_score}/100 is moderately elevated.")

    if signals.repeated_phrases:
        interpretations.append(f"Repeated phrases detected: {', '.join(signals.repeated_phrases[:5])}")

    interp_block = "\n".join(f"  • {i}" for i in interpretations)

    flag_value = "true" if caution_hint == "watch" else "false"

    return f"""You are a compassionate, precise language analyst helping a family track subtle communication
patterns in a loved one's daily spoken check-ins. You are NOT a clinician and must never diagnose.

TODAY'S CHECK-IN:
"{text}"

RAW SIGNALS:
  Word count:             {signals.word_count}  (baseline: {baseline['avg_word_count']})
  Vocabulary diversity:   {signals.unique_word_ratio}  (baseline: {baseline['avg_unique_ratio']})
  Filler word ratio:      {signals.filler_word_ratio}  (baseline: {baseline.get('avg_filler_ratio', 'N/A')})
  Phrase repetition:      {signals.phrase_repetition_score}  (baseline: {baseline.get('avg_repetition_score', 'N/A')})
  Avg words/sentence:     {signals.avg_words_per_sentence}  (baseline: {baseline['avg_words_per_sentence']})
  Uncertainty markers:    {signals.uncertainty_markers}  (baseline: {baseline.get('avg_uncertainty_markers', 'N/A')})
  Pause markers:          {signals.pause_markers}  (baseline: {baseline.get('avg_pause_markers', 'N/A')})
  Incomplete sentences:   {signals.incomplete_sentences}
  Negation count:         {signals.negation_count}
  Risk score:             {signals.risk_score}/100  [{risk_band}]

SIGNAL INTERPRETATIONS:
{interp_block}

ALGORITHMIC CAUTION LEVEL: {caution_hint.upper()}

RECENT HISTORY:
{trend}

Return ONLY valid JSON. The caution_level MUST be "{caution_hint}" unless you have a specific textual
reason to override — if so, set override_reason. Otherwise override_reason is null.
Your summary and what_changed MUST reference specific numbers and actual patterns from today's data.
Do not write generic positive/wellness text when signals show deviation.

{{
  "summary": "specific 1-2 sentences referencing actual signal values",
  "what_changed": "specific changed signals with values",
  "why_it_matters": "why this is worth tracking, non-clinical (1-2 sentences)",
  "caution_level": "{caution_hint}",
  "override_reason": null,
  "next_step": "one concrete practical family action",
  "safety_note": "brief reminder this is not a diagnosis",
  "flag_for_review": {flag_value},
  "single_day_note": "one sentence: one unusual day is normal"
}}

RULES:
  - caution_level must be exactly: "low", "moderate", or "watch"
  - NEVER say: dementia, Alzheimer's, cognitive decline, symptom, disorder, diagnosis, disease
  - flag_for_review = true only when caution_level is "watch"
  - Raw JSON only, no markdown or preamble
"""


def analyze(text, signals: TextSignals, baseline: dict, deltas: dict, recent_history: list) -> dict:
    prompt = build_prompt(text, signals, baseline, deltas, recent_history)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in Claude response: {raw[:300]}")

    result = json.loads(raw[start:end])

    # Hard-enforce: caution_level must match algorithmic hint unless overridden
    hint = deltas.get("caution_hint", "low")
    if result.get("caution_level") != hint and not result.get("override_reason"):
        result["caution_level"] = hint

    # Enforce flag_for_review consistency
    result["flag_for_review"] = result.get("caution_level") == "watch"

    return result
