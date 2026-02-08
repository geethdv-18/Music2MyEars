# CLAUDE.md — Project Context for Claude Code Sessions

## What This Project Is
Music2MyEars — a Streamlit app that turns text, images, and voice into AI-generated music based on detected emotions.

## Tech Stack
- **Streamlit** — UI (app.py)
- **Google Gemini 2.0 Flash** — Text/image emotion analysis, prompt generation
- **OpenAI Whisper (base)** — Voice-to-text transcription
- **MusicGen (facebook/musicgen-small)** — Local music generation via transformers
- **Plotly** — Pipeline visualization chart
- **ffmpeg** — Required system dependency for Whisper

## Module Map

| Module | File | Does |
|--------|------|------|
| UI | `app.py` | Streamlit app — tabs, sliders, parallel analysis, results display |
| Text Analyzer | `modules/text_analyzer.py` | Gemini text emotion → {mood, energy, source} |
| Image Analyzer | `modules/image_analyzer.py` | Gemini vision → {caption, mood, energy, source} |
| Voice Analyzer | `modules/voice_analyzer.py` | Whisper transcription + Gemini mood → {transcript, mood, energy, source} |
| Emotion Fuser | `modules/emotion_fuser.py` | Merges multi-source moods into one profile (energy/style/warmth/arc 0-100) |
| Music Orchestrator | `modules/music_orchestrator.py` | Converts profile → vivid MusicGen prompt via Gemini |
| Music Generator | `modules/music_generator.py` | Local MusicGen model → WAV bytes (singleton pattern) |
| Explainer | `modules/explainer.py` | Gemini generates narrative + 5-step timeline for Plotly chart |
| Feedback | `modules/feedback.py` | Saves ratings to data/feedback.json, learns defaults from past sessions |
| LLM Client | `utils/llm_client.py` | Gemini helpers: ask_json(), ask_json_with_image(), ask_text() |

## Key Patterns
- **Singleton model loading** — MusicGen and Whisper models loaded once, reused across requests
- **Parallel analysis** — ThreadPoolExecutor runs text/image/voice analyzers simultaneously
- **JSON fence stripping** — `_strip_json_fences()` in llm_client.py handles Gemini's markdown wrapping
- **Feedback loop** — High-rated sessions influence future slider defaults and prompt generation

## Git Worktree Setup
This project uses git worktrees for parallel Claude Code sessions:

| Directory | Branch | Scope |
|-----------|--------|-------|
| `Music2myears/` | `master` | Main app, UI, integration |
| `Music2myears-analyzers/` | `feature/analyzers` | text_analyzer, image_analyzer, voice_analyzer |
| `Music2myears-music/` | `feature/music-engine` | music_orchestrator, music_generator |
| `Music2myears-feedback/` | `feature/feedback-loop` | feedback, explainer, emotion_fuser |

**Rule: each worktree only edits its own modules.** Merge via PR into master.

## Environment
- API key in `.env` (never commit) — needs `GEMINI_API_KEY`
- Python venv at `venv/` (gitignored)
- MusicGen model cached at `~/.cache/huggingface/`
- Whisper model cached at `~/.cache/whisper/`
- Feedback data at `data/feedback.json` (gitignored)

## Running Locally
```bash
source venv/bin/activate
streamlit run app.py
```
First run downloads MusicGen (~2.5GB). Generation takes ~20-30s on M1 Mac.

## Known Decisions
- MusicGen runs locally because HuggingFace Inference API is dead (410 Gone as of Feb 2026)
- Voice input uses `st_audiorec` for in-browser recording with start/stop buttons
- Style/warmth mappings were diversified to avoid lo-fi bias in generated music
