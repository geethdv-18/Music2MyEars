from utils.llm_client import ask_json_with_image


def analyze_image(image_bytes):
    """Analyze an image for emotional content. Returns mood dict."""
    prompt = """Analyze this image for its emotional content.
Return ONLY a JSON object with these keys:
- caption: one sentence describing what you see
- mood: one word describing the dominant mood
- energy: float 0.0 to 1.0 (0=very calm, 1=very intense)

Return ONLY valid JSON, no other text."""

    result = ask_json_with_image(prompt, image_bytes)
    result["source"] = "image"
    return result
