# SilentGuardian

A web application for tracking emotional and cognitive patterns through daily check-ins, powered by AI analysis. SilentGuardian helps monitor mental health indicators by analyzing language patterns in daily responses.

##  Features

### Clarity Tracking
- **Daily Check-ins**: Short voice-of-the-day responses to build emotional baselines
- **Pattern Recognition**: AI-powered analysis of language patterns, sentiment, and emotional indicators
- **Risk Assessment**: Automatic caution level detection (Low/Moderate/Watch) based on baseline comparisons
- **Historical Insights**: Track changes over time with detailed analysis

### Focus Tracking
- **Multi-step Analysis**: 3-question focus assessments to understand current mental state
- **Focus Mode Detection**: Identifies Flow State, Check-in, or Support needed
- **Signal Breakdown**: Detailed metrics on task switching, avoidance, urgency, and emotional spikes
- **Start Mode**: Actionable next steps with built-in timers and strategies

### Key Capabilities
- **Baseline Establishment**: 5-day onboarding to create personalized reference points
- **Real-time Analysis**: Instant feedback on current mental state
- **Historical Trends**: Visual tracking of patterns over time
- **Safety-First Design**: Non-diagnostic tool with clear disclaimers

##  Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key (for AI analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SilentGuardian
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env  # If .env.example exists, otherwise create .env
   ```
   
   Add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

##  Usage Guide

### First Time Setup

1. **Create Account**: Register with email and password
2. **Clarity Onboarding**: Complete 5 daily check-ins to establish your baseline
3. **Focus Onboarding**: Complete 5 focus assessments to establish focus patterns

### Daily Workflow

#### Clarity Check-in
- Navigate to the home page
- Answer the daily prompt (rotates weekly)
- Receive instant analysis with caution level and insights
- View historical trends in the History tab

#### Focus Check-in
- Click "Focus" in the navigation
- Answer 3 sequential questions about current focus state
- Get comprehensive analysis including:
  - Focus mode (Flow/Check-in/Support)
  - Signal breakdown (task switches, avoidance, etc.)
  - Next actionable steps
  - Start Mode with timers and strategies

### Navigation
- **Clarity**: Daily emotional check-ins and analysis
- **Focus**: Multi-step focus pattern assessment
- **History**: View past analyses with filtering options

##  Technical Architecture

### Backend
- **Flask**: Web framework with session management
- **PostgreSQL**: Database storage with user isolation
- **Anthropic Claude**: AI-powered text analysis
- **Dataclasses**: Structured data models for signals and analysis

### Frontend
- **Jinja2 Templates**: Server-side rendering
- **Vanilla JavaScript**: Interactive UI components
- **CSS Variables**: Consistent theming system
- **Responsive Design**: Mobile-friendly interface

### Data Processing
- **Signal Extraction**: Linguistic pattern analysis (word count, sentiment, repetition, etc.)
- **Baseline Comparison**: Statistical comparison against personal norms
- **Risk Scoring**: Weighted algorithm for caution level determination
- **Focus Analysis**: Specialized metrics for attention and productivity patterns

##  Analysis Features

### Clarity Signals
- Word count and vocabulary diversity
- Sentence structure and complexity
- Emotional word usage (positive/negative)
- Hesitation markers and uncertainty
- Past vs present tense usage

### Focus Signals
- Task switching frequency
- Avoidance language patterns
- Urgency indicators
- Emotional spike detection
- Hyperfocus and scatter cues
- Focus/momentum/scatter scores

### AI Analysis
- **Summary**: Concise overview of current state
- **Insights**: Detailed explanations of patterns
- **Recommendations**: Actionable next steps
- **Safety Notes**: Important disclaimers and context

##  Privacy & Security

- **Database Storage**: All data stored in PostgreSQL database
- **User Isolation**: Data completely separated between users
- **No External Sharing**: Analysis stays on your device
- **API Security**: Anthropic API calls are secure and temporary

##  Important Disclaimers

- **Not a Medical Tool**: This application is for informational purposes only
- **Not Diagnostic**: Cannot diagnose mental health conditions
- **Professional Advice**: Consult healthcare professionals for medical concerns
- **Data Limitations**: Analysis based on text patterns, not clinical assessment

##  Development

### Project Structure
```
SilentGuardian/
├── app.py              # Main Flask application
├── auth.py             # User authentication
├── claude_client.py    # Anthropic API integration
├── signals.py          # Text analysis and signal processing
├── storage.py          # Data persistence layer
├── templates/          # Jinja2 HTML templates
├── data/               # User data storage
└── requirements.txt    # Python dependencies
```

### Key Components

#### Signal Processing (`signals.py`)
- Text analysis algorithms
- Baseline computation and comparison
- Risk scoring and caution levels

#### AI Integration (`claude_client.py`)
- Prompt engineering for different analysis types
- Response parsing and structured output
- Error handling and fallbacks

#### Data Storage (`storage.py`)
- User data isolation
- JSON-based persistence
- Baseline and history management

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- Built with Anthropic's Claude for AI analysis
- Inspired by cognitive behavioral techniques
- Designed for mental health awareness and self-monitoring
