# SilentGuardian

**SilentGuardian** is an AI-powered web application designed for people who feel **overwhelmed, stuck, or unable to focus** — helping them understand their mental state and take **clear, immediate action**.

🔗 **Live Demo:** https://silentguardian.onrender.com
*(Try it instantly — no setup required)*

---

## 🚀 Why SilentGuardian?

Many people struggle with:

* Not understanding *what they’re feeling*
* Feeling overwhelmed by too many tasks
* Being unable to start even simple work

SilentGuardian bridges that gap by turning **unclear thoughts → structured insights → actionable steps**.

It doesn’t try to replace therapy — it helps users **gain clarity and move forward in the moment**.

---

## ✨ What It Does

### 🧠 Clarity Tracking

* Daily check-ins to capture your mental state
* AI analyzes emotional tone and language patterns
* Detects shifts from your personal baseline
* Assigns a simple **caution level** (Low / Moderate / Watch)

---

### 🎯 Focus Tracking

* Guided 3-step check-in to assess focus

* Detects:

  * Flow state
  * Distraction / avoidance
  * Need for support

* Breaks down signals like:

  * Task switching
  * Urgency
  * Emotional spikes

---

### ⚡ Start Mode (Core Feature)

When you're stuck, SilentGuardian:

* Reduces overwhelm
* Gives **one small actionable step**
* Helps you **start immediately**

---

## 🧩 Key Capabilities

* **Personal Baselines**
  Learns your patterns over time (5-day onboarding)

* **Real-time AI Feedback**
  Instant analysis of your current state

* **Pattern Awareness**
  See how your mental state evolves

* **Action-Oriented Design**
  Focus on *doing*, not just analyzing

---

## 🛠️ Tech Stack

### Backend

* Flask
* SQLite (local) / PostgreSQL (production-ready)
* Anthropic Claude API

### Frontend

* Jinja2 Templates
* Vanilla JavaScript
* Responsive CSS

---

## ⚙️ Setup (Optional – for local development)

### Prerequisites

* Python 3.10+
* Anthropic API key

---

### Installation

```bash
git clone <repository-url>
cd SilentGuardian
```

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

---

### Environment Variables

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

---

### Run

```bash
python app.py
```

Visit:

```
http://localhost:5000
```

---

## 🧪 How It Works

### 1. Input

User writes a short response about their current state

### 2. Signal Processing

The system extracts:

* Emotional tone
* Language complexity
* Behavioral indicators (avoidance, urgency, etc.)

### 3. AI Analysis

Claude generates:

* Summary
* Insights
* Recommendations

### 4. Output

User receives:

* Clear understanding of their state
* **One actionable next step**

---

## 🔒 Privacy & Ethics

* Data is stored securely per user
* No public data exposure
* No diagnostic claims

SilentGuardian is designed to:

* **Support, not replace** human care
* Encourage **real-world action**
* Maintain **transparency about limitations**

---

## ⚠️ Disclaimer

* Not a medical or diagnostic tool
* For awareness and self-reflection only
* Consult professionals for clinical concerns

---

## 📁 Project Structure

```
SilentGuardian/
├── app.py              # Main application
├── auth.py             # User handling
├── claude_client.py    # AI integration
├── signals.py          # Pattern analysis
├── storage.py          # Data layer
├── templates/          # UI
└── requirements.txt
```

---

## 💡 Vision

SilentGuardian is built around a simple idea:

> People don’t just need insights — they need help taking the **first step**.

---

## 🙌 Acknowledgments

* Powered by Anthropic Claude
* Inspired by cognitive behavioral principles
* Built for mental clarity and action

---
