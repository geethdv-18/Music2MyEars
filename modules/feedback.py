import json
import os
from datetime import datetime
from utils.llm_client import ask_json

FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.json")
LEARNED_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "learned_rules.json")

REFLECTION_THRESHOLD = 5  # Run reflection every N new ratings

_DEFAULT_RULES = {
    "version": 1,
    "last_reflection": None,
    "reflection_count": 0,
    "entries_analyzed": 0,
    "global_rules": {"positive": [], "negative": []},
    "emotion_profiles": {},
    "param_insights": {
        "best_temperature": 1.0,
        "best_guidance_scale": 3.0,
        "best_max_new_tokens": 256,
        "param_history": [],
    },
}


# --- Feedback I/O ---

def _load_feedback():
    """Load all feedback entries from disk."""
    path = os.path.abspath(FEEDBACK_PATH)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_feedback(entries):
    """Write all feedback entries to disk."""
    path = os.path.abspath(FEEDBACK_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


# --- Learned Rules I/O ---

def _load_learned_rules():
    """Load learned rules from disk, returning defaults if missing."""
    path = os.path.abspath(LEARNED_RULES_PATH)
    if not os.path.exists(path):
        return dict(_DEFAULT_RULES)
    with open(path, "r") as f:
        return json.load(f)


def _save_learned_rules(rules):
    """Write learned rules to disk."""
    path = os.path.abspath(LEARNED_RULES_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(rules, f, indent=2)


def get_learned_rules():
    """Public accessor for the full knowledge base."""
    return _load_learned_rules()


# --- Core Feedback Functions ---

def save_feedback(rating, would_replay, ai_profile, final_profile, music_prompt,
                  preferred_version="N/A", gen_params=None, user_note=None):
    """Append a feedback entry, then maybe trigger reflection."""
    entries = _load_feedback()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "would_replay": would_replay,
        "ai_profile": ai_profile,
        "final_profile": final_profile,
        "music_prompt": music_prompt,
        "preferred_version": preferred_version,
    }
    if gen_params:
        entry["gen_params"] = gen_params
    if user_note:
        entry["user_note"] = user_note
    entries.append(entry)
    _save_feedback(entries)

    # Check if we should run a reflection cycle
    _maybe_trigger_reflection(entries)


def get_negative_examples(emotion, max_rating=2, limit=3):
    """Return prompts from low-rated sessions — used as 'avoid this' guidance."""
    entries = _load_feedback()
    bad = [
        e for e in entries
        if e.get("rating", 5) <= max_rating
        and e.get("final_profile", {}).get("emotion", "").lower() == emotion.lower()
        and e.get("music_prompt")
    ]
    bad.sort(key=lambda e: (e.get("rating", 5), e.get("timestamp", "")))
    return [e["music_prompt"] for e in bad[:limit]]


def get_emotion_profile(emotion):
    """Return per-emotion learned data from rules file, or None."""
    rules = _load_learned_rules()
    profiles = rules.get("emotion_profiles", {})
    return profiles.get(emotion.lower())


def get_optimal_gen_params():
    """Return best MusicGen params from correlation analysis."""
    rules = _load_learned_rules()
    insights = rules.get("param_insights", {})
    return {
        "temperature": insights.get("best_temperature", 1.0),
        "guidance_scale": insights.get("best_guidance_scale", 3.0),
        "max_new_tokens": insights.get("best_max_new_tokens", 256),
    }


def get_learned_defaults(emotion):
    """Return slider defaults, preferring learned range midpoints over simple averaging.

    Falls back to averaging high-rated sessions if no learned ranges exist.
    """
    # First, try learned range midpoints
    profile = get_emotion_profile(emotion)
    if profile:
        result = {}
        for key in ["energy", "style", "warmth", "arc"]:
            range_key = f"{key}_range"
            pref = profile.get("preferred_params", {})
            if range_key in pref:
                lo, hi = pref[range_key]
                result[key] = round((lo + hi) / 2)
        if result:
            return result

    # Fallback: average high-rated sessions
    entries = _load_feedback()
    good = [
        e for e in entries
        if e.get("rating", 0) >= 4
        and e.get("final_profile", {}).get("emotion", "").lower() == emotion.lower()
    ]

    if len(good) < 2:
        return None

    result = {}
    for key in ["energy", "style", "warmth", "arc"]:
        values = [e["final_profile"][key] for e in good if key in e.get("final_profile", {})]
        if values:
            result[key] = round(sum(values) / len(values))

    return result


def get_top_prompts(emotion, min_rating=4, limit=3):
    """Return music prompts from high-rated sessions with similar emotion."""
    entries = _load_feedback()
    good = [
        e for e in entries
        if e.get("rating", 0) >= min_rating
        and e.get("final_profile", {}).get("emotion", "").lower() == emotion.lower()
        and e.get("music_prompt")
    ]
    good.sort(key=lambda e: (e.get("rating", 0), e.get("timestamp", "")), reverse=True)
    return [e["music_prompt"] for e in good[:limit]]


def get_feedback_summary():
    """Return a summary of collected feedback including learning status."""
    entries = _load_feedback()
    if not entries:
        return None

    ratings = [e.get("rating", 0) for e in entries]
    replays = [e.get("would_replay", False) for e in entries]

    rules = _load_learned_rules()
    entries_since = len(entries) - rules.get("entries_analyzed", 0)

    return {
        "total_sessions": len(entries),
        "avg_rating": round(sum(ratings) / len(ratings), 1),
        "replay_rate": round(sum(replays) / len(replays) * 100),
        "high_rated": len([r for r in ratings if r >= 4]),
        "reflections_completed": rules.get("reflection_count", 0),
        "emotions_learned": list(rules.get("emotion_profiles", {}).keys()),
        "rules_active": len(rules.get("global_rules", {}).get("positive", []))
                      + len(rules.get("global_rules", {}).get("negative", [])),
        "next_reflection_in": max(0, REFLECTION_THRESHOLD - entries_since),
    }


# --- Reflection Engine ---

def _format_entries_for_reflection(entries):
    """Format feedback entries into a readable block for Gemini."""
    lines = []
    for e in entries:
        fp = e.get("final_profile", {})
        lines.append(
            f"- Rating: {e.get('rating')}/5 | Emotion: {fp.get('emotion', '?')} | "
            f"Energy: {fp.get('energy')} | Style: {fp.get('style')} | "
            f"Warmth: {fp.get('warmth')} | Arc: {fp.get('arc')}\n"
            f"  Prompt: \"{e.get('music_prompt', '')[:200]}\""
        )
        if e.get("user_note"):
            lines.append(f"  User note: \"{e['user_note']}\"")
    return "\n".join(lines)


def _format_slider_ranges(entries):
    """Summarize slider value distributions from entries."""
    by_emotion = {}
    for e in entries:
        fp = e.get("final_profile", {})
        emotion = fp.get("emotion", "unknown").lower()
        if emotion not in by_emotion:
            by_emotion[emotion] = {"energy": [], "style": [], "warmth": [], "arc": [], "ratings": []}
        for key in ["energy", "style", "warmth", "arc"]:
            if key in fp:
                by_emotion[emotion][key].append(fp[key])
        by_emotion[emotion]["ratings"].append(e.get("rating", 0))

    lines = []
    for emotion, data in by_emotion.items():
        parts = []
        for key in ["energy", "style", "warmth", "arc"]:
            vals = data[key]
            if vals:
                parts.append(f"{key}: {min(vals)}-{max(vals)} (avg {round(sum(vals)/len(vals))})")
        avg_r = round(sum(data["ratings"]) / len(data["ratings"]), 1) if data["ratings"] else 0
        lines.append(f"{emotion} ({len(data['ratings'])} sessions, avg rating {avg_r}): {', '.join(parts)}")
    return "\n".join(lines)


def _compute_param_insights(entries):
    """Correlate MusicGen gen_params with ratings."""
    with_params = [e for e in entries if e.get("gen_params")]
    if not with_params:
        return None

    # Group by rating bucket
    high = [e for e in with_params if e.get("rating", 0) >= 4]
    low = [e for e in with_params if e.get("rating", 0) <= 2]

    def avg_param(group, key, default):
        vals = [e["gen_params"].get(key, default) for e in group]
        return round(sum(vals) / len(vals), 2) if vals else default

    return {
        "best_temperature": avg_param(high, "temperature", 1.0) if high else 1.0,
        "best_guidance_scale": avg_param(high, "guidance_scale", 3.0) if high else 3.0,
        "best_max_new_tokens": round(avg_param(high, "max_new_tokens", 256)) if high else 256,
        "param_history": [
            {"rating": e.get("rating"), "params": e.get("gen_params")}
            for e in with_params[-10:]  # Keep last 10
        ],
    }


def _maybe_trigger_reflection(entries):
    """Gate reflection to run every REFLECTION_THRESHOLD new ratings."""
    rules = _load_learned_rules()
    entries_since = len(entries) - rules.get("entries_analyzed", 0)
    if entries_since >= REFLECTION_THRESHOLD:
        run_reflection()


def run_reflection():
    """Core batch learning: analyze feedback to extract reusable rules.

    Phase A: Global rules from high vs. low-rated prompts
    Phase B: Per-emotion analysis
    Phase C: Parameter correlation
    """
    entries = _load_feedback()
    if len(entries) < REFLECTION_THRESHOLD:
        return

    rules = _load_learned_rules()
    formatted = _format_entries_for_reflection(entries)
    slider_summary = _format_slider_ranges(entries)

    high = [e for e in entries if e.get("rating", 0) >= 4]
    low = [e for e in entries if e.get("rating", 0) <= 2]

    # --- Phase A: Global rules ---
    phase_a_prompt = f"""You are a music AI trainer analyzing user feedback on AI-generated music.

Here are all feedback entries (rating 1-5, with the prompt used):

{formatted}

HIGH-RATED prompts ({len(high)} entries): prompts that produced music users loved.
LOW-RATED prompts ({len(low)} entries): prompts that produced music users disliked.

Analyze the patterns. What makes a music generation prompt good vs bad?

Return JSON:
{{
  "positive": ["<rule 1>", "<rule 2>", "<rule 3>"],
  "negative": ["<avoid pattern 1>", "<avoid pattern 2>", "<avoid pattern 3>"]
}}

Rules should be specific and actionable (e.g. "Naming 2-3 specific instruments works better than genre labels").
Return 2-4 rules per category. Return ONLY the JSON."""

    try:
        global_rules = ask_json(phase_a_prompt)
        rules["global_rules"] = {
            "positive": global_rules.get("positive", [])[:4],
            "negative": global_rules.get("negative", [])[:4],
        }
    except Exception:
        pass  # Keep existing rules if Gemini fails

    # --- Phase B: Per-emotion analysis ---
    emotions_seen = set()
    for e in entries:
        emo = e.get("final_profile", {}).get("emotion", "").lower()
        if emo:
            emotions_seen.add(emo)

    for emotion in emotions_seen:
        emo_entries = [
            e for e in entries
            if e.get("final_profile", {}).get("emotion", "").lower() == emotion
        ]
        if len(emo_entries) < 2:
            continue

        emo_formatted = _format_entries_for_reflection(emo_entries)
        emo_high = [e for e in emo_entries if e.get("rating", 0) >= 4]
        emo_ratings = [e.get("rating", 0) for e in emo_entries]

        phase_b_prompt = f"""Analyze feedback for the emotion "{emotion}" in AI music generation.

Entries:
{emo_formatted}

Slider ranges:
{slider_summary}

Return JSON for this emotion:
{{
  "preferred_params": {{
    "energy_range": [<low>, <high>],
    "style_range": [<low>, <high>],
    "warmth_range": [<low>, <high>],
    "arc_range": [<low>, <high>]
  }},
  "prompt_principles": ["<what works for {emotion}>"],
  "anti_patterns": ["<what to avoid for {emotion}>"],
  "best_prompt_template": "<a template like: A slow {{instrument}} melody in a minor key...>"
}}

Base ranges on the actual slider values from high-rated sessions.
Return 1-3 items per list. Return ONLY the JSON."""

        try:
            emo_profile = ask_json(phase_b_prompt)
            emo_profile["sample_count"] = len(emo_entries)
            emo_profile["avg_rating"] = round(sum(emo_ratings) / len(emo_ratings), 1)
            rules.setdefault("emotion_profiles", {})[emotion] = emo_profile
        except Exception:
            pass

    # --- Phase C: Parameter correlation ---
    param_insights = _compute_param_insights(entries)
    if param_insights:
        rules["param_insights"] = param_insights

    # Update metadata
    rules["last_reflection"] = datetime.now().isoformat()
    rules["reflection_count"] = rules.get("reflection_count", 0) + 1
    rules["entries_analyzed"] = len(entries)

    _save_learned_rules(rules)
