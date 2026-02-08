# Music2MyEars

Turn your expression into personalized music. Describe a feeling, upload an image, or record your voice — and get an AI-generated soundtrack that matches your emotion.

## How It Works

1. **Input** — Text, image, or voice (or any combination)
2. **Analyze** — AI detects multiple emotions from each input (in parallel)
3. **Fuse** — All emotion signals blend into one profile, guided by learned knowledge
4. **Tune** — Adjust energy, style, warmth, and arc with sliders (or let AI decide)
5. **Generate** — MusicGen creates two A/B variations in a single batched call
6. **Compare** — Listen to both versions, pick your favorite
7. **Explain** — See how your input became music, step by step
8. **Learn** — Your feedback trains the system to produce better results over time

## Architecture

```
modules/
  text_analyzer.py      # Gemini text → multi-emotion analysis
  image_analyzer.py     # Gemini vision → image emotion analysis
  voice_analyzer.py     # Whisper transcription + Gemini mood analysis
  emotion_fuser.py      # Blends multi-source moods, range-clamped by learned knowledge
  music_orchestrator.py # Converts profile into a vivid MusicGen prompt
  music_generator.py    # Batched MusicGen — 2 variations in one forward pass
  explainer.py          # Narrative + timeline with learning status
  feedback.py           # Ratings, A/B preference, reflection engine
utils/
  llm_client.py         # Gemini API helpers (text, JSON, multimodal)
app.py                  # Streamlit UI
```

## Key Features

- **Multi-emotion detection** — Detects 1-3 emotions per input (e.g. "sad + hopeful + reflective"), blends them into slider values
- **A/B comparison** — Two music variations generated in parallel, side-by-side playback with preference selection
- **Duration control** — Choose 5s, 10s, or 20s track length
- **Reflection engine** — Every 5 ratings, AI analyzes all feedback to extract prompt rules, per-emotion slider ranges, and parameter insights
- **"What I've learned" panel** — Shows discovered rules, emotion-specific knowledge, and anti-patterns
- **Range-clamping** — Learned knowledge nudges AI values toward proven ranges without overwriting contextual judgment
- **User feedback notes** — Free-text feedback field (e.g. "Too slow for the energy I wanted")
- **Download buttons** — Save your generated tracks as WAV files
- **Multimodal parallel analysis** — Text, image, and voice analyzed simultaneously via ThreadPoolExecutor
- **Learning stats** — After submitting feedback, see reflection count, active rules, and countdown to next learning cycle

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

# Install ffmpeg (required for Whisper voice transcription)
brew install ffmpeg

# Configure API key
cp .env.example .env
# Edit .env and add your Gemini API key

# Run the app
streamlit run app.py
```

## How to Use

1. **Open the app** — Run `streamlit run app.py` and open `http://localhost:8501` in your browser

2. **Provide input** (use one or combine all three):
   - **Text** — Type how you're feeling, describe a memory, a scene, anything
   - **Image** — Upload a photo that captures a mood (sunset, city, old photo, etc.)
   - **Voice** — Hit the record button, speak your feelings, then stop when done. Your speech is transcribed and shown in the text box below

3. **Tweak the sliders** (optional) — Expand "Advanced Options" to adjust:
   - **Energy** — Calm ambient to high-intensity
   - **Style** — Minimal/sparse to epic orchestral
   - **Warmth** — Deep and moody to bright and sparkling
   - **Arc** — Steady loop to dramatic build-up

4. **Pick a duration** — Choose 5s, 10s, or 20s for your track

5. **Hit "Generate Music"** — The pipeline runs:
   - Analyzes all your inputs in parallel (detects multiple emotions)
   - Fuses them into one emotional profile (guided by past learning)
   - Creates a tailored music prompt
   - Generates two A/B variations (~30s on M1 Mac, first run slower due to model download)

5. **Listen and compare** — After generation you'll see:
   - All detected emotions (e.g. "nostalgic + hopeful")
   - Two audio players (Version A and B) with download buttons
   - A preference selector (A / B / No preference)
   - The music prompt used (expandable)
   - An explainer showing how your input became music, with a Plotly pipeline chart

7. **Rate and teach** — Rate the track, toggle "would listen again", pick your preferred version, and optionally leave a note. Every 5 ratings the system reflects on all feedback to improve future generations. Check the "What I've learned" panel to see discovered rules.

## Requirements

- Python 3.10+
- ffmpeg (`brew install ffmpeg`)
- Gemini API key (get one at [Google AI Studio](https://aistudio.google.com))
- ~2.5 GB disk space for the MusicGen model (downloads on first run)

## Tech Stack

- **Streamlit** — UI
- **Google Gemini 2.0 Flash** — Text/image emotion analysis, reflection engine
- **OpenAI Whisper** — Voice transcription
- **MusicGen** (facebook/musicgen-small) — Local music generation
- **Plotly** — Pipeline visualization
