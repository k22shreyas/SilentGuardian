# app.py
from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from signals import compute_signals, compare_to_baseline, compute_baseline, score_caution
from storage import load_history, save_entry, load_baseline, save_baseline, reset_all
from claude_client import analyze

app = Flask(__name__)

PROMPTS = [
    "Tell me about your morning so far.",
    "What is something you enjoyed recently?",
    "How are you feeling today and what have you been up to?",
    "Describe something that made you smile this week.",
    "What did you do this morning?",
]

# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    baseline = load_baseline()
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    today_done = any(e["date"][:10] == today for e in history)
    prompt = PROMPTS[datetime.now().weekday() % len(PROMPTS)]
    return render_template("index.html",
        baseline=baseline, history=history[-3:],
        today_done=today_done, prompt=prompt)

@app.route("/onboarding")
def onboarding():
    collected = request.args.get("collected", "0")
    step = int(collected) + 1
    prompt = PROMPTS[(step - 1) % len(PROMPTS)]
    return render_template("onboarding.html", step=step,
                           total=5, prompt=prompt, collected=collected)

@app.route("/history")
def history_page():
    history = load_history()
    return render_template("history.html", history=list(reversed(history)))

# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/baseline", methods=["POST"])
def api_baseline():
    data = request.json
    texts = data.get("texts", [])
    if len(texts) < 5:
        return jsonify({"error": "Need at least 5 samples"}), 400
    baseline = compute_baseline(texts)
    save_baseline(baseline)
    return jsonify({"ok": True, "baseline": baseline})

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.json
    text = data.get("text", "").strip()
    if len(text.split()) < 10:
        return jsonify({"error": "Response too short — please enter at least 10 words"}), 400

    baseline = load_baseline()
    if not baseline:
        return jsonify({"error": "No baseline found — please complete setup first"}), 400

    history = load_history()

    # 1. Compute language signals
    signals = compute_signals(text)

    # 2. Compare to baseline (returns dict)
    deltas = compare_to_baseline(signals, baseline)

    # 3. Deterministic caution scoring — Claude does NOT decide this
    caution_level, flags, score = score_caution(signals, deltas)

    try:
        from dataclasses import asdict

        # 4. Claude explains the pre-determined level
        analysis = analyze(text, signals, baseline, deltas, history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    entry = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "date": datetime.now().isoformat(),
        "text": text,
        "signals": asdict(signals),
        "deltas": deltas,
        "score": score,
        "flags": flags,
        "analysis": analysis,
    }
    save_entry(entry)

    return jsonify(entry)

@app.route("/api/reset", methods=["POST"])
def api_reset():
    reset_all()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
