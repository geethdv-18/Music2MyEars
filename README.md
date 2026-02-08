# Music2MyEars

Turn your expression into personalized music. Describe a feeling, upload an image, or record your voice — and get an AI-generated soundtrack that matches your emotion.

## How It Works

1. **Input** — Text, image, or voice (or any combination)
2. **Analyze** — AI detects emotion, mood, and energy from each input (in parallel)
3. **Fuse** — Multiple signals merge into one emotional profile
4. **Tune** — Adjust energy, style, warmth, and arc with sliders (or let AI decide)
5. **Generate** — A local MusicGen model creates a unique audio track
6. **Explain** — See how your input became music, step by step

## Architecture

```
modules/
  text_analyzer.py      # Gemini text emotion analysis
  image_analyzer.py     # Gemini vision image emotion analysis
  voice_analyzer.py     # Whisper transcription + Gemini mood analysis
  emotion_fuser.py      # Merges multi-source moods into one profile
  music_orchestrator.py # Converts profile into a MusicGen prompt
  music_generator.py    # Local MusicGen (facebook/musicgen-small)
  explainer.py          # Narrative + timeline of the creation process
  feedback.py           # User ratings + learning loop
utils/
  llm_client.py         # Gemini API helpers (text, JSON, multimodal)
app.py                  # Streamlit UI
```

## Setup

```bash
# Clone the repo
git clone https://github.com/geethdv-18/Music2MyEars.git
cd Music2MyEars

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your Gemini API key

# Run the app
streamlit run app.py
```

## Requirements

- Python 3.10+
- Gemini API key (get one at [Google AI Studio](https://aistudio.google.com))
- ~2.5 GB disk space for the MusicGen model (downloads on first run)

## Tech Stack

- **Streamlit** — UI
- **Google Gemini** — Text/image emotion analysis
- **OpenAI Whisper** — Voice transcription
- **MusicGen** (facebook/musicgen-small) — Local music generation
- **Plotly** — Pipeline visualization
