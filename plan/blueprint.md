# MUSIC2MYEARS — HACKATHON BLUEPRINT v3

## 1. Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     STREAMLIT  UI  (app.py)                         │
│                                                                      │
│  ┌────────────── INPUT SECTION ──────────────────────────────────┐   │
│  │                                                                │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐                   │   │
│  │  │  Image    │   │  Text    │   │  Voice   │  ← any combo     │   │
│  │  │  Upload   │   │  Input   │   │  Upload  │                   │   │
│  │  └──────────┘   └──────────┘   └──────────┘                   │   │
│  │                                                                │   │
│  ├────────────── ADVANCED OPTIONS (collapsed) ───────────────────┤   │
│  │  ▶ Advanced Options                                            │   │
│  │  ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │   │
│  │  │  Energy:  ○──────────●───────○  [__]                     │  │   │
│  │  │           0         50     100                           │  │   │
│  │  │                                                          │  │   │
│  │  │  Style:   ○──●───────────────○  [__]   Lo-fi ↔ Cinematic│  │   │
│  │  │                                                          │  │   │
│  │  │  Warmth:  ○──────────────●───○  [__]   Warm ↔ Bright    │  │   │
│  │  │                                                          │  │   │
│  │  │  Arc:     ○──────────────────●  [__]   Steady ↔ Big Build│  │   │
│  │  └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │   │
│  │                                                                │   │
│  │                   [ Generate Music ]                           │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                             │                                        │
│                             │  ONE click triggers entire pipeline    │
│                             ▼                                        │
│  ┌────────────── RESULTS SECTION (appears after generation) ─────┐   │
│  │                                                                │   │
│  │  "We detected: melancholy"                                     │   │
│  │  AI read:  Energy 72 │ Style 40 │ Warmth 65 │ Arc 55          │   │
│  │  Final:    Energy 72 │ Style 15 │ Warmth 65 │ Arc 88          │   │
│  │           (highlights overrides)                                │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │  Audio Player (variation 1)    Audio Player (variation 2)│  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │  Explanation: "Your rainy window photo and the word       │  │   │
│  │  │  'longing' created a bittersweet lo-fi piece. You shifted │  │   │
│  │  │  the arc toward Big Build, so it swells to a climax..."   │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │  Emotion Timeline (Plotly bar chart)                      │  │   │
│  │  │  ████ intro:calm  ██████ build:hope  ████████ peak:joy    │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                │   │
│  │  ⭐ Rating (1-5)    🔁 Would replay?    [ Submit Feedback ]   │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Backend Pipeline

```
[ Generate Music ] clicked
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      INPUT  ANALYZERS                                │
│                                                                      │
│  image_analyzer.py   text_analyzer.py   voice_analyzer.py            │
│  (Claude Vision)     (Claude)           (Whisper + Claude)           │
│       │                   │                   │                      │
│       ▼                   ▼                   ▼                      │
│  {caption, mood,    {summary, mood,     {transcript, mood,           │
│   energy, source}    energy, source}     energy, source}             │
│                                                                      │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │  list[dict]  (mood signals)
                           ▼
                 ┌──────────────────────┐
                 │   EMOTION  FUSER     │  ← Claude API
                 │   emotion_fuser.py   │
                 │                      │
                 │  merge mood signals  │
                 │  into ai_profile     │
                 └──────────┬───────────┘
                            │
                            │  ai_profile dict
                            ▼
                 ┌──────────────────────┐
                 │  SLIDER OVERRIDE     │  ← app.py logic (no module)
                 │                      │
                 │  if Advanced Options │
                 │  was opened and user │
                 │  moved sliders:      │
                 │    merge overrides   │
                 │  else:               │
                 │    final = ai_profile│
                 └──────────┬───────────┘
                            │
                            │  final_profile dict
                            ▼
                 ┌──────────────────────┐
                 │  MUSIC ORCHESTRATOR  │  ← Claude API
                 │ music_orchestrator.py│
                 │                      │
                 │  final_profile →     │
                 │  MusicGen prompt     │
                 └──────────┬───────────┘
                            │
                            │  prompt string
                            ▼
                 ┌──────────────────────┐
                 │   MUSIC GENERATOR   │  ← HF Inference API
                 │  music_generator.py  │     (remote, not local)
                 │                      │
                 │  POST prompt to HF   │
                 │  → receive audio     │
                 │  → return wav bytes  │
                 │  + 1 variation       │
                 └──────────┬───────────┘
                            │
                            │  list[wav bytes]
                            ▼
                 ┌──────────────────────┐
                 │     EXPLAINER        │  ← Claude API
                 │   explainer.py       │
                 │                      │
                 │  profiles → text +   │
                 │  timeline data       │
                 └──────────┬───────────┘
                            │
                            ▼
                      Results Section
                  (audio, explanation,
                   timeline, feedback)
```

---

## 2. Emotional Profile Schema

### ai_profile (output of Emotion Fuser)

```
{
  "emotion":  str,     # dominant emotion label, e.g. "melancholy", "joy"
  "energy":   int,     # 0–100, overall intensity
  "style":    int,     # 0–100, 0=lo-fi intimate / 100=cinematic epic
  "warmth":   int,     # 0–100, 0=warm analog / 100=bright digital
  "arc":      int,     # 0–100, 0=steady constant / 100=big dramatic build
  "sources":  list     # ["text", "image"] — which inputs contributed
}
```

### final_profile (after slider override)

```
{
  "emotion":     str,     # unchanged from ai_profile (not slider-controlled)
  "energy":      int,     # slider value (or ai_profile default)
  "style":       int,     # slider value (or ai_profile default)
  "warmth":      int,     # slider value (or ai_profile default)
  "arc":         int,     # slider value (or ai_profile default)
  "sources":     list,    # unchanged from ai_profile
  "overrides":   list     # e.g. ["style", "arc"] — which sliders user moved
}
```

The `overrides` list tracks which sliders the user intentionally changed. This is passed to the Explainer so it can say things like *"You shifted the style toward lo-fi, so we swapped orchestral strings for a Rhodes piano."*

---

## 3. Module Breakdown

| # | Module | File | Responsibility | Input | Output |
|---|--------|------|---------------|-------|--------|
| **A** | **UI / App Shell** | `app.py` | Single-screen Streamlit page: input uploaders, collapsible Advanced Options expander with 4 sliders, Generate button, results section (audio player, explanation, timeline, feedback). On Generate: runs full pipeline, applies slider overrides if any, displays results. | User interactions | Raw inputs to analyzers; final_profile to orchestrator |
| **B** | **Image Analyzer** | `modules/image_analyzer.py` | Caption + mood + energy from image via Claude Vision | `bytes` (image) | `{caption, mood, energy, source: "image"}` |
| **C** | **Text Analyzer** | `modules/text_analyzer.py` | Summary + mood + energy from text via Claude | `str` | `{summary, mood, energy, source: "text"}` |
| **D** | **Voice Analyzer** | `modules/voice_analyzer.py` | Transcribe with Whisper, then tone/mood via Claude | `bytes` (audio) | `{transcript, mood, energy, source: "voice"}` |
| **E** | **Emotion Fuser** | `modules/emotion_fuser.py` | Merge N mood dicts into one ai_profile with all 4 slider dimensions (energy, style, warmth, arc) plus emotion label | `list[dict]` | `ai_profile dict` (see schema above) |
| **F** | **Music Orchestrator** | `modules/music_orchestrator.py` | Convert final_profile (with slider values) into a vivid MusicGen prompt. Maps numeric slider values to musical parameters (see mapping table). | `final_profile dict` | `str` (music prompt) |
| **G** | **Music Generator** | `modules/music_generator.py` | Send prompt to HF Inference API, receive audio bytes, return wav. Produces original + 1 variation (second call with tweaked prompt). No local model. | `str` (prompt) | `list[bytes]` (wav buffers) |
| **H** | **Explainer** | `modules/explainer.py` | Generate "why this music" explanation referencing both AI-detected emotion and any user overrides. Produce timeline data for visualization. | `ai_profile, final_profile, music_prompt` | `{explanation: str, timeline: list}` |
| **I** | **Feedback Store** | `modules/feedback.py` | Save rating, replay intent, ai_profile, final_profile, overrides to JSON | `feedback dict` | appended to `data/feedback.json` |
| **-** | **Claude Client** | `utils/claude_client.py` | Shared Anthropic client initialization from .env | - | `anthropic.Anthropic` instance |

---

## 4. Module G — Music Generator (HF Inference API)

### What changed from v2

Local MusicGen is gone. Module G now makes HTTP POST requests to the
Hugging Face Inference API. No torch, no transformers, no GPU required.

### How it works

```
generate_music(prompt, duration_sec=10)
│
├─ Load HF_TOKEN and HF_MODEL_ID from environment
│
├─ POST to https://api-inference.huggingface.co/models/{HF_MODEL_ID}
│   Headers: Authorization: Bearer {HF_TOKEN}
│   Body:    {"inputs": prompt}
│
├─ Response = raw audio bytes (HF returns audio/flac or audio/wav)
│
├─ For variation: tweak the prompt slightly
│   (e.g. append "with subtle variation in rhythm")
│   POST again with tweaked prompt
│
├─ Return list of 2 audio byte buffers
│
└─ If HF returns 503 (model loading): retry after wait
   If HF returns error: raise with clear message
```

### Environment variables consumed

```
HF_TOKEN       — Hugging Face API token (required)
HF_MODEL_ID    — model to call (default: facebook/musicgen-small)
```

### Error handling

- **503 Model Loading**: HF cold-starts models. Retry up to 3 times with
  increasing wait (5s, 15s, 30s). Show "Model is warming up..." in UI.
- **401 Unauthorized**: Bad token. Raise immediately with helpful message.
- **Rate limit**: Surface to user. Suggest waiting.

---

## 5. Environment & Dependencies

### .env.example

```
ANTHROPIC_API_KEY=your-anthropic-key-here
HF_TOKEN=your-huggingface-token-here
HF_MODEL_ID=facebook/musicgen-small
```

### requirements.txt

```
streamlit
anthropic
requests
python-dotenv
Pillow
plotly
openai-whisper
```

### What was removed (vs v2)

| Removed | Why |
|---------|-----|
| `torch` | No local model inference |
| `transformers` | No local model loading |
| `torchaudio` | No local audio processing |
| `scipy` | Was only needed for local wav writing |
| `soundfile` | Was only needed for local wav handling |

### What was added

| Added | Why |
|-------|-----|
| `requests` | HTTP calls to HF Inference API |

### What stays

| Package | Used by |
|---------|---------|
| `streamlit` | UI (Module A) |
| `anthropic` | Claude API calls (Modules B, C, D, E, F, H) |
| `python-dotenv` | Load .env (utils/claude_client.py, Module G) |
| `Pillow` | Image handling (Module B) |
| `plotly` | Emotion timeline chart (Module H / app.py) |
| `openai-whisper` | Voice transcription (Module D) — still runs locally |

**Note**: `openai-whisper` will pull in `torch` as its own dependency.
This is fine — torch is needed for Whisper, just not for music generation.
The key win is we no longer download or run MusicGen locally.

---

## 6. UI Responsibilities — Single-Screen Flow (Module A)

### Screen Layout (top to bottom, one page)

```
┌─────────────────────────────────────────┐
│  Title: Music2MyEars                    │
│  Subtitle: Turn expression into music   │
├─────────────────────────────────────────┤
│  IMAGE UPLOAD  │  TEXT INPUT  │  VOICE  │
├─────────────────────────────────────────┤
│  ▶ Advanced Options  (collapsed)        │  ← st.expander, closed by default
│    ┌─────────────────────────────────┐  │
│    │ Sliders appear here only when   │  │
│    │ the expander is opened. Values  │  │
│    │ start at midpoint defaults      │  │
│    │ until pipeline runs.            │  │
│    └─────────────────────────────────┘  │
├─────────────────────────────────────────┤
│           [ Generate Music ]            │  ← single button
├─────────────────────────────────────────┤
│  (Results section — hidden until        │
│   generation completes)                 │
│                                         │
│  Detected emotion + AI vs Final profile │
│  Audio players                          │
│  Explanation                            │
│  Emotion timeline chart                 │
│  Feedback form                          │
└─────────────────────────────────────────┘
```

### Interaction Flow (what happens on Generate click)

```
User clicks [ Generate Music ]
│
├─ Validate: at least one input provided
│  (if not → show error, stop)
│
├─ Step A: ANALYZE
│  ├─ Run active analyzers
│  │   image_analyzer(img)  →  mood_dict
│  │   text_analyzer(txt)   →  mood_dict
│  │   voice_analyzer(aud)  →  mood_dict
│  │
│  └─ Run emotion_fuser(mood_list) → ai_profile
│
├─ Step B: APPLY OVERRIDES
│  ├─ Read current slider values from Advanced Options expander
│  ├─ For each of the 4 dimensions (energy, style, warmth, arc):
│  │     if user_opened_advanced AND slider_value != default:
│  │       → final_profile[dim] = slider_value
│  │       → add dim to overrides list
│  │     else:
│  │       → final_profile[dim] = ai_profile[dim]
│  ├─ If Advanced Options was never opened:
│  │     → final_profile = ai_profile (copy)
│  │     → overrides = []
│  └─ final_profile["overrides"] = overrides
│
├─ Step C: GENERATE
│  ├─ music_orchestrator(final_profile)  → prompt string
│  ├─ music_generator(prompt)            → list[wav bytes]  (HF API)
│  └─ explainer(ai_profile, final_profile, prompt) → explanation + timeline
│
└─ Step D: DISPLAY RESULTS
   ├─ Show: "We detected: {emotion}"
   ├─ Show: AI profile vs Final profile (highlight overrides)
   ├─ Show: audio players for each variation
   ├─ Show: explanation text in callout
   ├─ Show: Plotly emotion timeline chart
   └─ Show: feedback form (rating + replay + submit)
```

### Slider Behavior Inside the Expander

```
BEFORE first generation:
  - Sliders exist inside st.expander("Advanced Options")
  - Initialized to neutral midpoints (50, 50, 50, 50)
  - Label reads: "Defaults will be set by AI after analysis"

DURING generation (Step B):
  - ai_profile is computed from fuser
  - For each slider dimension:
      if slider == 50 (untouched midpoint default):
        → use ai_profile value (user didn't express preference)
      if slider != 50:
        → user moved it → treat as override
  - Build final_profile accordingly

AFTER generation (on re-run):
  - Sliders update to show ai_profile values from PREVIOUS run
  - Stored in st.session_state so sliders reflect actual AI output
  - User can now make informed adjustments for next generation
```

### Override Detection Logic

```
FIRST run (no prior ai_profile exists):
  slider_defaults = {energy: 50, style: 50, warmth: 50, arc: 50}
  user_interacted = slider_value != 50

SUBSEQUENT runs (ai_profile from last run in session_state):
  slider_defaults = ai_profile from previous run
  user_interacted = slider_value != ai_profile[dimension]

In both cases:
  if user never opened the expander:
    → overrides = []
    → final_profile = ai_profile

  if user opened expander but moved nothing:
    → overrides = []
    → final_profile = ai_profile

  if user opened expander and moved slider(s):
    → overrides = [list of moved dimension names]
    → final_profile merges ai_profile with slider values
```

---

## 7. Slider → Music Parameter Mapping

The orchestrator uses this mapping to translate slider integers into musical language for the MusicGen prompt.

### Energy (0–100)

| Range | Tempo Feel | Dynamics | Prompt Words |
|-------|-----------|----------|-------------|
| 0–20 | ~60 BPM | very soft, sparse | "quiet, minimal, ambient, whisper-soft" |
| 21–40 | ~80 BPM | soft, gentle | "gentle, relaxed, easy-going, mellow" |
| 41–60 | ~100 BPM | moderate | "moderate energy, steady, flowing" |
| 61–80 | ~120 BPM | strong, driving | "energetic, driving, powerful, upbeat" |
| 81–100 | ~140 BPM | intense, maximal | "intense, explosive, soaring, maximum energy" |

### Style: Lo-fi (0) ↔ Cinematic (100)

| Range | Instruments | Production | Prompt Words |
|-------|------------|-----------|-------------|
| 0–20 | Rhodes, tape piano, vinyl | lo-fi, warm hiss, mono | "lo-fi hip-hop, vinyl crackle, tape warble, bedroom" |
| 21–40 | acoustic guitar, soft keys | indie, understated | "indie, acoustic, intimate, small-room" |
| 41–60 | piano, light strings, pads | balanced, polished | "polished, balanced, clean production" |
| 61–80 | full strings, brass hints | cinematic, wide stereo | "cinematic, orchestral swell, wide stereo, dramatic" |
| 81–100 | full orchestra, choir, percussion | epic, Hans Zimmer | "epic orchestral, massive, soaring strings, choir, blockbuster" |

### Warmth: Warm (0) ↔ Bright (100)

| Range | Tone | Textures | Prompt Words |
|-------|------|---------|-------------|
| 0–20 | dark, round, analog | tape saturation, sub bass | "warm analog, dark tone, round bass, vintage" |
| 21–40 | warm, smooth | soft reverb, muted highs | "warm, smooth, soft, muted, cozy" |
| 41–60 | neutral, balanced | natural room tone | "natural, balanced tone, clear" |
| 61–80 | bright, clear | crisp highs, shimmer | "bright, crisp, shimmering, airy, sparkling" |
| 81–100 | very bright, digital | synthetic sparkle, glass | "crystalline, digital, glass-like, ultra-bright, neon" |

### Arc: Steady (0) ↔ Big Build (100)

| Range | Structure | Dynamics Over Time | Prompt Words |
|-------|----------|-------------------|-------------|
| 0–20 | single section, no change | flat dynamics | "steady, unchanging, ambient loop, constant" |
| 21–40 | subtle swell | gentle variation | "gentle variation, subtle breathing, light swell" |
| 41–60 | verse-chorus feel | moderate dynamics | "evolving, verse-chorus, moderate build" |
| 61–80 | clear build + climax | rising to peak | "building, rising intensity, crescendo, climax" |
| 81–100 | slow intro → massive peak | extreme contrast | "starts quiet, massive build, explosive climax, drop" |

---

## 8. Emotion Fuser (Module E)

### Fuser System Prompt

```
You are an emotion analyst for a music generation system.

Given mood signals from one or more inputs (image, text, voice),
produce ONE unified emotional profile as JSON:

{
  "emotion": "<dominant emotion word>",
  "energy": <0-100 integer>,
  "style": <0-100 integer, 0=lo-fi intimate, 100=cinematic epic>,
  "warmth": <0-100 integer, 0=warm analog, 100=bright digital>,
  "arc": <0-100 integer, 0=steady constant, 100=big dramatic build>
}

Base your values on the emotional content of the inputs.
A sad quiet poem → low energy, lo-fi style, warm, steady arc.
An action photo with excited text → high energy, cinematic, bright, big build.

Return ONLY the JSON object.
```

---

## 9. Music Orchestrator (Module F)

### Responsibilities

1. **Receive** `final_profile` dict (includes slider values + emotion + overrides list)
2. **Map** each slider value to musical descriptors using the mapping table from section 7
3. **Compose** a Claude prompt that asks for a MusicGen-ready text prompt incorporating all mapped parameters
4. **Return** the prompt string

### Orchestrator System Prompt

```
You are a music director creating a prompt for an AI music generator.

Given this emotional profile:
- Emotion: {emotion}
- Energy: {energy}/100 → {energy_descriptors}
- Style: {style}/100 → {style_descriptors}
- Warmth: {warmth}/100 → {warmth_descriptors}
- Arc: {arc}/100 → {arc_descriptors}

Write a vivid 2-3 sentence music generation prompt that blends ALL
of these qualities naturally. Include specific instruments, tempo feel,
production style, and structural arc.

The listener's dominant emotion is "{emotion}" — the music should
honor that feeling while respecting the parameter settings above.

Output ONLY the prompt text. No labels, no JSON, no explanation.
```

### Orchestrator Internal Logic

```
1. Look up energy value in energy mapping table → get descriptors
2. Look up style value in style mapping table → get descriptors
3. Look up warmth value in warmth mapping table → get descriptors
4. Look up arc value in arc mapping table → get descriptors
5. Inject all descriptors + emotion into Claude system prompt
6. Return Claude's response as the music prompt string
```

---

## 10. Folder Structure

```
Music2myears/
├── app.py                        # Streamlit entry point (single-screen UI)
├── requirements.txt
├── .env                          # ANTHROPIC_API_KEY, HF_TOKEN, HF_MODEL_ID
├── .env.example                  # Template for env vars
├── modules/
│   ├── __init__.py
│   ├── image_analyzer.py         # B: image → mood dict
│   ├── text_analyzer.py          # C: text → mood dict
│   ├── voice_analyzer.py         # D: voice → mood dict
│   ├── emotion_fuser.py          # E: mood dicts → ai_profile (4 dimensions)
│   ├── music_orchestrator.py     # F: final_profile → music prompt
│   ├── music_generator.py        # G: prompt → HF API → wav bytes
│   ├── explainer.py              # H: profiles → explanation + timeline
│   └── feedback.py               # I: save ratings + profiles
├── utils/
│   ├── __init__.py
│   └── claude_client.py          # Shared Anthropic client
├── data/
│   └── feedback.json             # Auto-created ratings log
└── plan/
    ├── spec.md
    ├── project_plan.md
    └── blueprint.md              # This file
```

---

## 11. Six-Hour Hackathon Build Plan

Module G is now an API call instead of a local model install. This is
faster to build and eliminates the GPU/memory risk entirely. The biggest
demo risk shifts to HF API cold-start latency and rate limits.

```
HOUR 0:00–0:30  ▸ Setup & Skeleton
─────────────────────────────────────
- Create folder structure, venv, install requirements.txt
- Create .env with ANTHROPIC_API_KEY, HF_TOKEN, HF_MODEL_ID
- Create utils/claude_client.py
- Stub every module with hardcoded returns
- Verify `streamlit run app.py` shows a blank page

HOUR 0:30–1:15  ▸ MODULE G — Music Generator (HF API)  ⚠️ HIGHEST RISK
─────────────────────────────────────
- Implement music_generator.py:
  POST to HF Inference API with prompt, get audio bytes back
- Handle 503 cold-start (retry with backoff)
- Test with hardcoded prompt: call HF → save response → play wav
- Confirm audio plays in Python and in Streamlit st.audio
- WHY FIRST: if HF API is down, rate-limited, or returns
  garbage, you need to know NOW. Pivot options: different
  HF model, Replicate API, or pre-recorded fallback audio.
- NOTE: faster than v2 (no model download, no GPU debugging).
  Budget shrinks from 60min to 45min.

HOUR 1:15–2:15  ▸ MODULE E+F — Fuser + Orchestrator (with slider schema)
─────────────────────────────────────
- Implement emotion_fuser.py with prompt that returns
  all 4 numeric dimensions (energy, style, warmth, arc)
- Implement music_orchestrator.py with slider mapping table
  (hardcode the 4 mapping lookups, feed to Claude prompt)
- Test end-to-end: hardcoded mood dicts → ai_profile →
  final_profile (simulate slider override) → music prompt →
  send to HF API → confirm audio quality matches prompt intent
- WHY SECOND: bad mapping = bad music. Validate the full
  slider→prompt→HF→audio chain before building UI.

HOUR 2:15–3:00  ▸ MODULE C — Text Analyzer + End-to-End
─────────────────────────────────────
- Implement text_analyzer.py (Claude call → mood dict)
- Test full chain: text → analyzer → fuser → orchestrator
  → HF API → wav
- This proves the pipeline works with real input.

HOUR 3:00–4:00  ▸ MODULE A — Single-Screen UI with Advanced Options
─────────────────────────────────────
- Text input area at top
- st.expander("Advanced Options", expanded=False) with 4 sliders
  initialized to midpoint 50 defaults
- Single [ Generate Music ] button below expander
- On click: full pipeline with spinner
  → analyze → fuse → apply slider overrides → orchestrate
  → call HF API → display audio
- Show ai_profile vs final_profile comparison in results
- Show music prompt in expander
- Store ai_profile in session_state for subsequent runs
- Handle HF cold-start: show "Model warming up..." message
- 🎯 CHECKPOINT: working demo with text + optional sliders + audio

HOUR 4:00–4:45  ▸ MODULES B+D — Image + Voice Analyzers
─────────────────────────────────────
- Image analyzer: Claude Vision API → mood dict
- Voice analyzer: Whisper transcribe → Claude tone → mood dict
- Add uploaders to input section of UI, wire into mood_list
- All inputs now feed the AI profile (and therefore slider defaults)

HOUR 4:45–5:15  ▸ MODULE H — Explainer + Timeline
─────────────────────────────────────
- Explainer receives both ai_profile and final_profile
- Generates explanation that references user overrides if any
- If no overrides: "The AI read your inputs and crafted..."
- Plotly bar chart for emotion/energy timeline
- Display in results section below audio player

HOUR 5:15–5:45  ▸ MODULE I — Feedback
─────────────────────────────────────
- Feedback: star rating + replay toggle → save to JSON
  (saves ai_profile + final_profile + overrides)
- Submit button wired up

HOUR 5:45–6:00  ▸ Polish + Safety Net
─────────────────────────────────────
- Loading spinners with status messages
- Error handling for missing inputs, HF failures
- Title, branding, st.divider()
- Pre-warm HF model (one throwaway request at app start)
- Record backup demo video
```

### Demo Safety Net

| After Hour | What You Can Demo |
|-----------|------------------|
| 1:15 | HF API works (hardcoded prompt → audio) |
| 2:15 | Full pipeline works (hardcoded input → audio) |
| 3:00 | Real text → real audio |
| **4:00** | **Full demo: text + Advanced Options sliders → personalized music** |
| 4:45 | All 3 input types working |
| 5:15 | Explanation + visualization |
| 5:45 | Feedback collection |
| 6:00 | Polished, branded, backup recorded |

### Demo Story

> "Drop in a photo, some text, or a voice note. Hit Generate — the
> AI reads your emotions and creates a soundtrack in seconds. Want
> more control? Open Advanced Options and fine-tune the energy, style,
> warmth, and arc. Trust the AI, or shape it yourself."

### HF API Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Cold-start 503 | Retry with backoff (5s, 15s, 30s). Show "warming up" in UI. Pre-warm at app start. |
| Rate limit | Free tier: ~30 req/hr. Enough for demo. Warn if close. |
| Slow response | Set 60s timeout. Show progress spinner. |
| API down | Have 2-3 pre-generated .wav files as fallback demo audio. |
| Bad audio quality | Test prompts during Hour 0:30. If musicgen-small is poor, try musicgen-medium. |

---

## 12. Exact Prompts for Each Module

### Setup
```
Read plan/blueprint.md for full context. Then create:
1) requirements.txt with: streamlit, anthropic, requests,
   python-dotenv, Pillow, plotly, openai-whisper
2) .env.example with:
   ANTHROPIC_API_KEY=your-anthropic-key-here
   HF_TOKEN=your-huggingface-token-here
   HF_MODEL_ID=facebook/musicgen-small
3) utils/claude_client.py — loads .env, returns Anthropic client
4) Stub app.py showing "Music2MyEars" title in Streamlit
5) Stub all modules in modules/ with functions that return
   hardcoded dicts matching the schemas in blueprint.md
Keep it minimal. No extras.
```

### Module G — Music Generator (HF Inference API)
```
Read plan/blueprint.md sections on Module G (section 4)
and the environment setup (section 5).
Create modules/music_generator.py.
- Load HF_TOKEN and HF_MODEL_ID from environment (.env)
- Function: generate_music(prompt: str, duration_sec=10)
  → POST to https://api-inference.huggingface.co/models/{HF_MODEL_ID}
  → Headers: {"Authorization": "Bearer {HF_TOKEN}"}
  → Body: {"inputs": prompt}
  → Returns list of 2 audio byte buffers:
    - First call with original prompt
    - Second call with prompt + " with subtle variation"
- Handle 503 cold-start: retry up to 3 times with backoff
  (5s, 15s, 30s). Raise clear error if still failing.
- Handle 401: raise with "Check your HF_TOKEN" message.
- Include __main__ block that tests with a hardcoded prompt,
  saves result to test_output.wav, prints success/failure.
Just functions, no classes. Use requests library.
```

### Module E — Emotion Fuser
```
Read plan/blueprint.md sections on Module E (section 8)
and the emotional profile schema (section 2).
Create modules/emotion_fuser.py.
Function: fuse_emotions(mood_list: list[dict]) -> dict
- Calls Claude with the fuser system prompt from the blueprint
- Must return ai_profile with ALL fields: emotion (str),
  energy (int 0-100), style (int 0-100), warmth (int 0-100),
  arc (int 0-100), sources (list)
- Parse JSON response, validate all fields present
- Use utils/claude_client.py
```

### Module F — Music Orchestrator
```
Read plan/blueprint.md sections on Module F (section 9)
and the slider mapping table (section 7).
Create modules/music_orchestrator.py.
Function: create_music_prompt(final_profile: dict) -> str
- Implement the 4 mapping lookups from blueprint section 7:
  energy→tempo/dynamics, style→instruments/production,
  warmth→tone/textures, arc→structure/dynamics
  (use simple if/elif ranges, no over-engineering)
- Inject mapped descriptors into the orchestrator system
  prompt from the blueprint
- Call Claude, return raw prompt string
- Use utils/claude_client.py
```

### Module C — Text Analyzer
```
Read plan/blueprint.md section on Module C.
Create modules/text_analyzer.py.
Function: analyze_text(text: str) -> dict
- Claude call: analyze text, return JSON with summary,
  mood, energy (0.0-1.0)
- Parse response, add source: "text", return dict
- Use utils/claude_client.py
```

### Module A — Single-Screen UI with Advanced Options
```
Read plan/blueprint.md sections on Module A (section 6),
the single-screen layout, interaction flow, and slider
override logic.
Update app.py to build a SINGLE-SCREEN Streamlit app:

TOP OF PAGE:
- Title "Music2MyEars" with subtitle
- Text input area (later: image + voice uploaders)

MIDDLE:
- st.expander("Advanced Options", expanded=False) containing:
  - 4 sliders: Energy (0-100, default 50), Style (0-100, default 50),
    Warmth (0-100, default 50), Arc (0-100, default 50)
  - Labels: "Lo-fi ↔ Cinematic", "Warm ↔ Bright", "Steady ↔ Big Build"
  - Small note: "Defaults will be set by AI after analysis"

BELOW EXPANDER:
- [ Generate Music ] button

ON CLICK (one spinner, full pipeline):
  1. Run text_analyzer → emotion_fuser → get ai_profile
  2. Read slider values. If slider != 50, treat as override.
     Build final_profile with overrides list.
     If no overrides, final_profile = ai_profile.
  3. Run music_orchestrator(final_profile) → music_generator
     (music_generator now calls HF API, not local model)
  4. Show results: detected emotion, AI vs Final profile,
     audio players, music prompt in expander
  5. Store ai_profile in session_state. On next run, sliders
     default to previous ai_profile values instead of 50.

Wire real modules. Must work end-to-end with text input.
```

### Module B — Image Analyzer
```
Read plan/blueprint.md section on Module B.
Create modules/image_analyzer.py.
Function: analyze_image(image_bytes: bytes) -> dict
- Send image to Claude Vision API
- Prompt: describe image, return JSON with caption, mood,
  energy (0.0-1.0)
- Parse, add source: "image", return dict
Then update app.py: add image uploader in the input section
(above the Advanced Options expander). If image provided,
include its analysis in mood_list passed to fuser.
```

### Module D — Voice Analyzer
```
Read plan/blueprint.md section on Module D.
Create modules/voice_analyzer.py.
Function: analyze_voice(audio_bytes: bytes) -> dict
- Whisper (model="base") to transcribe (still runs locally)
- Claude call on transcript for tone/mood → JSON with
  transcript, mood, energy (0.0-1.0)
- Add source: "voice", return dict
Then update app.py: add audio file uploader (wav/mp3) in the
input section alongside image and text. Wire into mood_list.
```

### Module H — Explainer + Timeline
```
Read plan/blueprint.md section on Module H.
Create modules/explainer.py.
Function: explain_music(ai_profile, final_profile, music_prompt) -> dict
- Takes BOTH profiles to reference overrides
- Claude call: "Given the AI-detected profile and the user's
  final settings (overrides: {overrides}), write 2-3 warm
  sentences explaining why this music was created. If the user
  overrode values, mention how their adjustments shaped the
  result. If no overrides, explain how the AI interpreted
  their input."
- Also return timeline: list of {section, emotion, energy}
Then update app.py: show explanation in st.info callout,
show Plotly bar chart of timeline in results section.
```

### Module I — Feedback + Polish
```
Read plan/blueprint.md section on Module I.
Create modules/feedback.py.
Function: save_feedback(session_id, rating, would_replay,
                        ai_profile, final_profile)
- Append to data/feedback.json (create if missing)
- Include timestamp, all profile data, overrides list
Then update app.py:
- Star rating slider (1-5) in results section
- "Would you listen again?" toggle
- Submit button → save_feedback
- Add st.divider() between sections
- Loading spinner with status messages during generation
  (include "Model warming up..." for HF cold-start)
- Error: require at least one input before Generate
```

---

## Appendix: Key Design Decisions

1. **Why single-screen with collapsible Advanced Options?** Zero friction for the default path — user uploads, clicks Generate, hears music. Power users expand the panel. No phase gates, no extra clicks, no waiting for intermediate results. One screen, one button, one experience.

2. **Why HF Inference API instead of local MusicGen?** No GPU required. No 2GB model download. No torch version hell. Setup drops from 30+ minutes to `pip install requests`. The trade-off is cold-start latency (first request takes ~30s while HF loads the model) and rate limits (~30 req/hr free tier). Both are acceptable for a hackathon demo.

3. **Why integer 0–100 instead of float 0–1?** Sliders with integer steps feel more tactile and readable. "Energy: 72" is more intuitive than "Energy: 0.72" in a demo.

4. **Why track overrides?** The explainer creates a much more compelling narrative when it can say "you chose to..." vs just describing the final values. It makes the user feel heard.

5. **Why map sliders to words, not numbers?** MusicGen is a text-conditioned model. It responds to descriptive language ("soaring orchestral strings") not parameter values ("style=85"). The mapping table bridges that gap.

6. **Why midpoint defaults before first analysis?** The sliders must exist in the expander before the pipeline runs. Starting at 50 (neutral) means untouched sliders are detectable. After the first run, session_state holds the real ai_profile for smarter defaults on re-generation.

7. **Why keep Whisper local but not MusicGen?** Whisper-base is tiny (~150MB), runs fast on CPU, and has no API alternative that's simpler. MusicGen is large, GPU-hungry, and HF Inference API handles it perfectly. Different trade-offs, different choices.

8. **Demo narrative**: "Users can trust the AI — or fine-tune with Advanced Options." The collapsed expander communicates: this is optional. The sliders communicate: you have power.
