from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import plotly.graph_objects as go
from modules.text_analyzer import analyze_text
from modules.image_analyzer import analyze_image
from modules.voice_analyzer import analyze_voice, transcribe_audio
from modules.emotion_fuser import fuse_emotions
from modules.music_orchestrator import create_music_prompt
from modules.music_generator import generate_music
from modules.explainer import explain_music
from modules.feedback import save_feedback, get_feedback_summary, get_learned_rules
from st_audiorec import st_audiorec

st.set_page_config(page_title="Music2MyEars", page_icon="🎵", layout="centered")

# ---------------------------------------------------------------------------
# Midnight Studio CSS
# ---------------------------------------------------------------------------
MIDNIGHT_CSS = """
<style>
/* ── Google Fonts ───────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Source+Sans+3:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ── Root variables ─────────────────────────────────────────────────────── */
:root {
    --midnight-bg: #0D0D0F;
    --surface: #16161A;
    --glass-bg: rgba(30, 30, 36, 0.65);
    --glass-border: rgba(255, 255, 255, 0.06);
    --amber: #E8945A;
    --amber-glow: rgba(232, 148, 90, 0.25);
    --amber-dim: rgba(232, 148, 90, 0.12);
    --coral: #FF6B6B;
    --teal: #4ECDC4;
    --text-primary: #E8E6E3;
    --text-secondary: #8A8A8E;
    --text-dim: #55555A;
}

/* ── App background + grain ─────────────────────────────────────────────── */
.stApp {
    background-color: var(--midnight-bg) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ── Typography ─────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em;
}

.stMarkdown p, .stMarkdown li, .stMarkdown span {
    font-family: 'Source Sans 3', sans-serif !important;
    color: var(--text-primary);
}

/* Captions */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Text areas ─────────────────────────────────────────────────────────── */
.stTextArea textarea {
    background-color: var(--surface) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.stTextArea textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-glow) !important;
}

.stTextArea textarea::placeholder {
    color: var(--text-dim) !important;
}

/* ── Text inputs ────────────────────────────────────────────────────────── */
.stTextInput input {
    background-color: var(--surface) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.stTextInput input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-glow) !important;
}

.stTextInput input::placeholder {
    color: var(--text-dim) !important;
}

/* ── File uploader ──────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background-color: var(--surface) !important;
    border: 1.5px dashed var(--glass-border) !important;
    border-radius: 12px !important;
    transition: border-color 0.3s, box-shadow 0.3s;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--amber) !important;
    box-shadow: 0 0 12px var(--amber-dim);
}

/* ── Generate button (primary) ──────────────────────────────────────────── */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #E8945A 0%, #D4783E 100%) !important;
    color: #0D0D0F !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.65rem 1.8rem !important;
    letter-spacing: 0.02em;
    transition: transform 0.2s, box-shadow 0.3s !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px var(--amber-glow), 0 0 40px var(--amber-dim) !important;
}

/* ── Secondary & download buttons ───────────────────────────────────────── */
.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
.stDownloadButton > button {
    background-color: transparent !important;
    color: var(--amber) !important;
    border: 1.5px solid var(--amber) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    transition: background-color 0.2s, transform 0.2s !important;
}

.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover,
.stDownloadButton > button:hover {
    background-color: var(--amber-dim) !important;
    transform: translateY(-1px) !important;
}

/* ── Sliders ────────────────────────────────────────────────────────────── */
.stSlider label {
    font-family: 'Source Sans 3', sans-serif !important;
    color: var(--text-secondary) !important;
}

.stSlider [data-testid="stThumbValue"] {
    font-family: 'Outfit', sans-serif !important;
    color: var(--amber) !important;
    font-weight: 600 !important;
}

[data-testid="stSlider"] [role="slider"] {
    background-color: var(--amber) !important;
}

/* ── Radio buttons ──────────────────────────────────────────────────────── */
.stRadio [role="radiogroup"] {
    gap: 0.4rem;
}

.stRadio [role="radiogroup"] label {
    font-family: 'Source Sans 3', sans-serif !important;
    border-radius: 20px !important;
    padding: 0.25rem 0.75rem !important;
    transition: background-color 0.2s;
}

.stRadio [role="radiogroup"] label[data-checked="true"] {
    background-color: var(--amber-dim) !important;
}

/* ── Expanders ──────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: var(--surface) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] summary {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    transition: color 0.2s;
}

[data-testid="stExpander"] summary:hover {
    color: var(--amber) !important;
}

/* ── Metric cards ───────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    padding: 0.8rem !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

[data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-size: 0.7rem !important;
    color: var(--text-secondary) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Dividers ───────────────────────────────────────────────────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent 0%, var(--amber-dim) 50%, transparent 100%) !important;
    margin: 1.5rem 0 !important;
}

/* ── Alert / info boxes ─────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

.stAlert [data-testid="stAlertContentInfo"] {
    background-color: rgba(78, 205, 196, 0.08) !important;
    border-left: 3px solid var(--teal) !important;
}

/* ── Toggle ─────────────────────────────────────────────────────────────── */
[data-testid="stToggle"] label {
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Audio players ──────────────────────────────────────────────────────── */
audio {
    border-radius: 10px !important;
    width: 100%;
}

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--midnight-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--glass-border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-dim);
}

/* ── Image preview ──────────────────────────────────────────────────────── */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    border: 1px solid var(--glass-border) !important;
}

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 20px var(--amber-dim); }
    50%      { box-shadow: 0 0 36px var(--amber-glow); }
}

.fade-in-up {
    animation: fadeInUp 0.5s ease-out both;
}

/* staggered delays for results sections */
.fade-delay-1 { animation-delay: 0.1s; }
.fade-delay-2 { animation-delay: 0.2s; }
.fade-delay-3 { animation-delay: 0.3s; }
.fade-delay-4 { animation-delay: 0.4s; }

/* ── Custom header ──────────────────────────────────────────────────────── */
.midnight-header {
    text-align: center;
    padding: 1.2rem 0 0.6rem 0;
}

.midnight-header h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.8rem !important;
    background: linear-gradient(135deg, #E8945A 0%, #F0B27A 50%, #E8945A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem !important;
    letter-spacing: -0.02em;
}

.midnight-header p {
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 300 !important;
    font-size: 1.15rem !important;
    color: var(--text-secondary) !important;
    margin-top: 0 !important;
}

/* ── Source badges ───────────────────────────────────────────────────────── */
.source-badge {
    display: inline-block;
    padding: 0.15rem 0.65rem;
    border-radius: 20px;
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-right: 0.4rem;
    background-color: rgba(78, 205, 196, 0.12);
    color: #4ECDC4;
    border: 1px solid rgba(78, 205, 196, 0.2);
}

/* ── Version labels ─────────────────────────────────────────────────────── */
.version-label {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.version-a { color: #4ECDC4; }
.version-b { color: #FF6B6B; }

/* ── Pipeline card headers ──────────────────────────────────────────────── */
.pipeline-header {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #E8945A;
    margin-bottom: 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid rgba(232, 148, 90, 0.15);
}

/* ── Section header ─────────────────────────────────────────────────────── */
.section-header {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    font-size: 1.35rem !important;
    margin-bottom: 0.6rem !important;
}

/* ── Success message ────────────────────────────────────────────────────── */
[data-testid="stAlert"] [data-testid="stAlertContentSuccess"] {
    background-color: rgba(78, 205, 196, 0.08) !important;
    border-left: 3px solid var(--teal) !important;
}

/* ── Warning message ────────────────────────────────────────────────────── */
[data-testid="stAlert"] [data-testid="stAlertContentWarning"] {
    background-color: rgba(232, 148, 90, 0.08) !important;
    border-left: 3px solid var(--amber) !important;
}

/* ── Error message ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] [data-testid="stAlertContentError"] {
    background-color: rgba(255, 107, 107, 0.08) !important;
    border-left: 3px solid var(--coral) !important;
}

/* ── st_audiorec widget ─────────────────────────────────────────────────── */
iframe[title="st_audiorec.st_audiorec"] {
    border-radius: 10px;
}

/* ── Learned rules expander content ─────────────────────────────────────── */
[data-testid="stExpander"] .stMarkdown strong {
    color: var(--amber) !important;
}
</style>
"""

st.markdown(MIDNIGHT_CSS, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="midnight-header">
    <h1>Music2MyEars</h1>
    <p>Turn your expression into personalized music</p>
</div>
""", unsafe_allow_html=True)

# --- INPUT SECTION ---
text_input = st.text_area(
    "What's on your mind?",
    placeholder="Describe a feeling, a memory, a scene... anything.",
    height=100,
)

col_image, col_voice = st.columns(2)

with col_image:
    image_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
    )
    if image_file:
        st.image(image_file, use_container_width=True)

with col_voice:
    st.write("Record your feelings")
    voice_bytes_recorded = st_audiorec()

    # Initialize transcript in session state
    if "voice_transcript" not in st.session_state:
        st.session_state["voice_transcript"] = ""

    # Transcribe when new audio is recorded
    if voice_bytes_recorded:
        st.audio(voice_bytes_recorded, format="audio/wav")
        with st.spinner("Transcribing..."):
            transcript = transcribe_audio(voice_bytes_recorded)
        st.session_state["voice_transcript"] = transcript if transcript else ""
        if not transcript:
            st.warning("Couldn't pick up any words. Try again?")

    # Show transcript
    st.text_area(
        "What we heard",
        value=st.session_state["voice_transcript"],
        height=80,
        disabled=True,
        placeholder="Your speech will appear here...",
    )

    # Reset button
    if st.button("Reset recording"):
        st.session_state["voice_transcript"] = ""
        st.rerun()

# --- DURATION ---
DURATION_TOKENS = {"5 sec": 250, "10 sec": 500, "20 sec": 1000}
duration = st.radio("Duration", list(DURATION_TOKENS.keys()), index=0, horizontal=True)

# --- ADVANCED OPTIONS ---
with st.expander("Advanced Options", expanded=False):
    st.caption("Defaults are set by AI after analysis. Move sliders to override.")
    defaults = st.session_state.get("ai_profile", {})
    col1, col2 = st.columns(2)
    with col1:
        slider_energy = st.slider("Energy", 0, 100, defaults.get("energy", 50))
        slider_style = st.slider("Style: Lo-fi ↔ Cinematic", 0, 100, defaults.get("style", 50))
    with col2:
        slider_warmth = st.slider("Warmth: Warm ↔ Bright", 0, 100, defaults.get("warmth", 50))
        slider_arc = st.slider("Arc: Steady ↔ Big Build", 0, 100, defaults.get("arc", 50))

# --- WHAT I'VE LEARNED ---
rules = get_learned_rules()
if rules.get("reflection_count", 0) > 0:
    with st.expander("What I've learned", expanded=False):
        global_pos = rules.get("global_rules", {}).get("positive", [])
        global_neg = rules.get("global_rules", {}).get("negative", [])
        emotion_profiles = rules.get("emotion_profiles", {})

        if global_pos:
            st.markdown("**What works well:**")
            for r in global_pos:
                st.markdown(f"- {r}")
        if global_neg:
            st.markdown("**What to avoid:**")
            for r in global_neg:
                st.markdown(f"- {r}")
        if emotion_profiles:
            st.markdown(f"**Emotions with specific knowledge:** {', '.join(emotion_profiles.keys())}")
            for emo, profile in emotion_profiles.items():
                principles = profile.get("prompt_principles", [])
                if principles:
                    st.markdown(f"*{emo}*: {'; '.join(principles[:2])}")

        st.caption(f"Based on {rules.get('reflection_count', 0)} reflection(s) analyzing {rules.get('entries_analyzed', 0)} sessions")

# --- GENERATE ---
if st.button("Generate Music", type="primary", use_container_width=True):
    has_text = bool(text_input and text_input.strip())
    has_image = image_file is not None
    has_voice = voice_bytes_recorded is not None

    if not (has_text or has_image or has_voice):
        st.error("Please provide at least one input (text, image, or voice).")
        st.stop()

    # Read file bytes upfront (before threads)
    image_bytes = image_file.getvalue() if has_image else None
    voice_bytes = voice_bytes_recorded if has_voice else None

    # Step A: Analyze inputs in parallel
    mood_list = []
    with st.spinner("Analyzing your inputs..."):
        tasks = {}
        with ThreadPoolExecutor() as executor:
            if has_text:
                tasks[executor.submit(analyze_text, text_input.strip())] = "text"
            if has_image:
                tasks[executor.submit(analyze_image, image_bytes)] = "image"
            if has_voice:
                tasks[executor.submit(analyze_voice, voice_bytes)] = "voice"
            for future in as_completed(tasks):
                mood_list.append(future.result())

    # Step B: Fuse emotions
    with st.spinner("Building emotional profile..."):
        ai_profile = fuse_emotions(mood_list)

    st.session_state["ai_profile"] = ai_profile

    # Step C: Apply slider overrides
    final_profile = dict(ai_profile)
    overrides = []
    slider_vals = {"energy": slider_energy, "style": slider_style, "warmth": slider_warmth, "arc": slider_arc}

    for dim, slider_val in slider_vals.items():
        ai_val = ai_profile.get(dim, 50)
        if slider_val != defaults.get(dim, 50):
            final_profile[dim] = slider_val
            overrides.append(dim)
        else:
            final_profile[dim] = ai_val

    final_profile["overrides"] = overrides

    # Step D: Orchestrate + Generate
    with st.spinner("Composing your soundtrack..."):
        music_prompt = create_music_prompt(final_profile)

    with st.spinner("Generating music... (this takes ~20-30s)"):
        audio_list = generate_music(music_prompt, max_new_tokens=DURATION_TOKENS[duration])

    # Step E: Explain
    with st.spinner("Writing the story of your music..."):
        explanation = explain_music(
            text_input or "", ai_profile, final_profile, overrides, music_prompt
        )

    # Store everything in session state so results survive reruns
    st.session_state["music_prompt"] = music_prompt
    st.session_state["final_profile"] = final_profile
    st.session_state["audio_list"] = audio_list
    st.session_state["ai_profile_result"] = ai_profile
    st.session_state["overrides_result"] = overrides
    st.session_state["mood_list_result"] = mood_list
    st.session_state["explanation"] = explanation
    st.session_state["gen_params"] = {
        "max_new_tokens": DURATION_TOKENS[duration],
        "temperature": 1.0,
        "guidance_scale": 3.0,
    }
    st.session_state["has_results"] = True

# --- RESULTS (persisted via session_state) ---
if st.session_state.get("has_results"):
    audio_list = st.session_state["audio_list"]
    ai_profile = st.session_state["ai_profile_result"]
    final_profile = st.session_state["final_profile"]
    overrides = st.session_state["overrides_result"]
    mood_list = st.session_state["mood_list_result"]
    music_prompt = st.session_state["music_prompt"]
    explanation = st.session_state["explanation"]

    st.divider()

    # Emotions detected
    emotions = ai_profile.get("emotions", [ai_profile.get("emotion", "?")])
    st.markdown(f'<div class="section-header fade-in-up">We sensed: {" + ".join(emotions)}</div>', unsafe_allow_html=True)

    # Source badges
    sources_used = [m.get("source", "?") for m in mood_list]
    badge_html = " ".join(f'<span class="source-badge">{s.upper()}</span>' for s in sources_used)
    st.markdown(f'<div class="fade-in-up fade-delay-1">{badge_html}</div>', unsafe_allow_html=True)

    # Profile comparison
    col_ai, col_final = st.columns(2)
    with col_ai:
        st.caption("AI detected")
        st.write(f"Energy **{ai_profile.get('energy')}** | Style **{ai_profile.get('style')}** | Warmth **{ai_profile.get('warmth')}** | Arc **{ai_profile.get('arc')}**")
    with col_final:
        st.caption("Final (with your overrides)" if overrides else "Final (AI defaults)")
        st.write(f"Energy **{final_profile.get('energy')}** | Style **{final_profile.get('style')}** | Warmth **{final_profile.get('warmth')}** | Arc **{final_profile.get('arc')}**")

    if overrides:
        st.info(f"You adjusted: {', '.join(overrides)}")

    # Audio player — A/B comparison
    if len(audio_list) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="version-label version-a">VERSION A</div>', unsafe_allow_html=True)
            st.audio(audio_list[0], format="audio/wav")
            st.download_button("Download A", audio_list[0], file_name="music2myears_A.wav", mime="audio/wav")
        with col_b:
            st.markdown('<div class="version-label version-b">VERSION B</div>', unsafe_allow_html=True)
            st.audio(audio_list[1], format="audio/wav")
            st.download_button("Download B", audio_list[1], file_name="music2myears_B.wav", mime="audio/wav")
        preferred = st.radio("Which version do you prefer?", ["A", "B", "No preference"], horizontal=True, key="ab_pref")
        st.session_state["preferred_version"] = preferred
    else:
        st.audio(audio_list[0], format="audio/wav")
        st.download_button("Download", audio_list[0], file_name="music2myears.wav", mime="audio/wav")

    # Music prompt used
    with st.expander("See the music prompt"):
        st.text_area("Prompt", music_prompt, height=150, disabled=True, label_visibility="collapsed")

    # --- EXPLAINER ---
    st.divider()
    st.markdown('<div class="section-header fade-in-up">How your input became music</div>', unsafe_allow_html=True)

    narrative = explanation.get("narrative", "")
    if narrative:
        st.info(narrative)

    # Radar chart: AI Profile vs Final Profile — Midnight Studio style
    dims = ["Energy", "Style", "Warmth", "Arc"]
    ai_vals = [ai_profile.get(d.lower(), 50) for d in dims]
    final_vals = [final_profile.get(d.lower(), 50) for d in dims]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=ai_vals + [ai_vals[0]],
        theta=dims + [dims[0]],
        name="AI Detected",
        fill="toself",
        fillcolor="rgba(78, 205, 196, 0.12)",
        opacity=0.9,
        line=dict(color="#4ECDC4", width=2),
        marker=dict(size=5, color="#4ECDC4"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=final_vals + [final_vals[0]],
        theta=dims + [dims[0]],
        name="Final",
        fill="toself",
        fillcolor="rgba(232, 148, 90, 0.12)",
        opacity=0.9,
        line=dict(color="#E8945A", width=2),
        marker=dict(size=5, color="#E8945A"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(family="Source Sans 3", size=10, color="#55555A"),
                gridcolor="rgba(255, 255, 255, 0.05)",
                linecolor="rgba(255, 255, 255, 0.04)",
            ),
            angularaxis=dict(
                tickfont=dict(family="Outfit", size=12, color="#8A8A8E"),
                gridcolor="rgba(255, 255, 255, 0.05)",
                linecolor="rgba(255, 255, 255, 0.04)",
            ),
        ),
        height=350,
        margin=dict(t=30, b=30, l=50, r=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(family="Source Sans 3", size=12, color="#8A8A8E"),
        ),
        font=dict(family="Source Sans 3"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Pipeline flow cards
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown('<div class="pipeline-header">Inputs</div>', unsafe_allow_html=True)
        for s in sources_used:
            st.write(f"- {s}")
    with p2:
        st.markdown('<div class="pipeline-header">Emotions</div>', unsafe_allow_html=True)
        detected = ai_profile.get("emotions", [ai_profile.get("emotion", "?")])
        for e in detected:
            st.write(f"- {e}")
    with p3:
        st.markdown('<div class="pipeline-header">Profile</div>', unsafe_allow_html=True)
        for d in dims:
            ai_v = ai_profile.get(d.lower(), 50)
            final_v = final_profile.get(d.lower(), 50)
            delta = final_v - ai_v
            st.metric(d, final_v, delta=delta if delta != 0 else None)
    with p4:
        st.markdown('<div class="pipeline-header">Music</div>', unsafe_allow_html=True)
        key_desc = explanation.get("key_descriptors", [])
        if key_desc:
            for kd in key_desc:
                st.write(f"- {kd}")
        else:
            st.write("*(no descriptors)*")

    st.divider()

    # --- FEEDBACK ---
    st.markdown('<div class="section-header">Rate this track</div>', unsafe_allow_html=True)
    rating = st.slider("How well does this music match your feeling?", 1, 5, 3, key="rating")
    would_replay = st.toggle("Would you listen to this again?", key="replay")
    user_note = st.text_input("Any specific feedback?", placeholder="e.g. 'Too slow for the energy I wanted'", key="user_note")

    if st.button("Submit Feedback"):
        save_feedback(
            rating=rating,
            would_replay=would_replay,
            ai_profile=ai_profile,
            final_profile=final_profile,
            music_prompt=music_prompt,
            preferred_version=st.session_state.get("preferred_version", "N/A"),
            gen_params=st.session_state.get("gen_params"),
            user_note=user_note if user_note else None,
        )
        st.success("Thanks! Your feedback improves future generations.")

        summary = get_feedback_summary()
        if summary:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.caption(
                    f"Learning from {summary['total_sessions']} sessions | "
                    f"Avg rating: {summary['avg_rating']}/5 | "
                    f"Replay rate: {summary['replay_rate']}%"
                )
            with col_s2:
                if summary["reflections_completed"] > 0:
                    st.caption(
                        f"Reflections: {summary['reflections_completed']} | "
                        f"Rules active: {summary['rules_active']} | "
                        f"Emotions learned: {', '.join(summary['emotions_learned']) or 'none'}"
                    )
                elif summary["next_reflection_in"] > 0:
                    st.caption(f"Next learning cycle in {summary['next_reflection_in']} more ratings")
