from utils.llm_client import ask_json


def analyze_text(text):
    """Analyze text input and return mood dict."""
    prompt = f"""Analyze the following text for its emotional content.
Return ONLY a JSON object with these keys:
- summary: one sentence summary
- mood: one word describing the dominant mood
- energy: float 0.0 to 1.0 (0=very calm, 1=very intense)

Text: "{text}"

Return ONLY valid JSON, no other text."""

    result = ask_json(prompt)
    result["source"] = "text"
    return result
