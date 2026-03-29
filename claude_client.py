# claude_client.py
import anthropic, json, os
from dataclasses import asdict
from signals import TextSignals

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def build_prompt(text, signals, baseline, deltas, recent_history):
    history_lines = "\n".join(
        f"- {e['date'][:10]}: {e['signals']['word_count']} words, "
        f"variety {e['signals']['unique_word_ratio']}"
        for e in recent_history[-7:]
    ) or "No previous history."

    return f"""You are a compassionate assistant helping a family track subtle language patterns
in a loved one's daily check-ins. You are NOT a clinician and must NOT provide any diagnosis.

TODAY'S CHECK-IN:
"{text}"

LANGUAGE SIGNALS TODAY:
- Word count: {signals.word_count} (baseline avg: {baseline['avg_word_count']})
- Vocabulary variety: {signals.unique_word_ratio} (baseline: {baseline['avg_unique_ratio']})
- Avg words/sentence: {signals.avg_words_per_sentence} (baseline: {baseline['avg_words_per_sentence']})
- Repeated phrases: {signals.repeated_phrases or 'none'}
- Hesitation markers: {signals.pause_markers}

CHANGE FROM BASELINE:
- Word count: {deltas['word_count_delta']:+}%
- Vocabulary: {deltas['unique_ratio_delta']:+}
- Sentence length: {deltas['sentence_length_delta']:+} words/sentence

RECENT HISTORY:
{history_lines}

BASELINE SAMPLES: {baseline['sample_count']}

Respond ONLY with valid JSON, no preamble:
{{
  "summary": "1-2 warm sentences summarising today vs baseline",
  "what_changed": "specific language signals that differ, plain English",
  "why_it_matters": "why a pattern like this might be worth watching (1-2 sentences)",
  "caution_level": "low|moderate|watch",
  "next_step": "one practical family action, non-medical",
  "safety_note": "brief reminder this is not a diagnosis",
  "flag_for_review": false,
  "single_day_note": "one sentence: one unusual day is completely normal"
}}

RULES:
- "watch" ONLY if word count down >40% AND unique ratio down >0.15 AND repeated phrases present
- NEVER use: dementia, Alzheimer's, cognitive decline, symptom, disorder, diagnosis
- flag_for_review = true only when caution_level is "watch"
- Return raw JSON only"""

def analyze(text, signals, baseline, deltas, recent_history) -> dict:
    prompt = build_prompt(text, signals, baseline, deltas, recent_history)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text
    # Extract JSON safely
    start, end = raw.find("{"), raw.rfind("}") + 1
    return json.loads(raw[start:end])