import json
import os
from datetime import datetime

FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.json")


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


def save_feedback(rating, would_replay, ai_profile, final_profile, music_prompt):
    """Append a feedback entry."""
    entries = _load_feedback()
    entries.append({
        "timestamp": datetime.now().isoformat(),
        "rating": rating,
        "would_replay": would_replay,
        "ai_profile": ai_profile,
        "final_profile": final_profile,
        "music_prompt": music_prompt,
    })
    _save_feedback(entries)


def get_learned_defaults(emotion):
    """Return averaged slider values from high-rated sessions with similar emotion.

    This is the feedback loop: past ratings shift future defaults.
    Returns None if not enough data.
    """
    entries = _load_feedback()
    # Filter for high-rated entries (4-5 stars) with matching emotion
    good = [
        e for e in entries
        if e.get("rating", 0) >= 4
        and e.get("final_profile", {}).get("emotion", "").lower() == emotion.lower()
    ]

    if len(good) < 2:
        return None

    # Average the slider values from high-rated sessions
    result = {}
    for key in ["energy", "style", "warmth", "arc"]:
        values = [e["final_profile"][key] for e in good if key in e.get("final_profile", {})]
        if values:
            result[key] = round(sum(values) / len(values))

    return result


def get_top_prompts(emotion, min_rating=4, limit=3):
    """Return music prompts from high-rated sessions with similar emotion.

    Used by the orchestrator for few-shot prompt improvement.
    """
    entries = _load_feedback()
    good = [
        e for e in entries
        if e.get("rating", 0) >= min_rating
        and e.get("final_profile", {}).get("emotion", "").lower() == emotion.lower()
        and e.get("music_prompt")
    ]

    # Sort by rating descending, then most recent
    good.sort(key=lambda e: (e.get("rating", 0), e.get("timestamp", "")), reverse=True)
    return [e["music_prompt"] for e in good[:limit]]


def get_feedback_summary():
    """Return a summary of collected feedback for display."""
    entries = _load_feedback()
    if not entries:
        return None

    ratings = [e.get("rating", 0) for e in entries]
    replays = [e.get("would_replay", False) for e in entries]

    return {
        "total_sessions": len(entries),
        "avg_rating": round(sum(ratings) / len(ratings), 1),
        "replay_rate": round(sum(replays) / len(replays) * 100),
        "high_rated": len([r for r in ratings if r >= 4]),
    }
