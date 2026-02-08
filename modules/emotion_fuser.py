from utils.llm_client import ask_json
from modules.feedback import get_learned_defaults


def fuse_emotions(mood_list):
    """Merge mood signals into one ai_profile with 4 slider dimensions."""
    sources = [m.get("source", "unknown") for m in mood_list]

    mood_descriptions = "\n".join(
        f"- Source: {m.get('source')}, Mood: {m.get('mood')}, Energy: {m.get('energy')}"
        for m in mood_list
    )

    prompt = f"""You are an emotion analyst for a music generation system.

Given these mood signals from user inputs:
{mood_descriptions}

Produce ONE unified emotional profile as JSON:
{{
  "emotion": "<dominant emotion word>",
  "energy": <0-100 integer>,
  "style": <0-100 integer, 0=lo-fi intimate, 100=cinematic epic>,
  "warmth": <0-100 integer, 0=warm analog, 100=bright digital>,
  "arc": <0-100 integer, 0=steady constant, 100=big dramatic build>
}}

Rules:
- A sad quiet poem → low energy, lo-fi style, warm, steady arc
- An action photo with excited text → high energy, cinematic, bright, big build
- Base values on the actual emotional content, not random guesses

Return ONLY the JSON object."""

    result = ask_json(prompt)
    result["sources"] = sources

    # Apply learned defaults from past feedback if available
    learned = get_learned_defaults(result.get("emotion", ""))
    if learned:
        for key in ["energy", "style", "warmth", "arc"]:
            if key in learned:
                result[key] = learned[key]

    return result
