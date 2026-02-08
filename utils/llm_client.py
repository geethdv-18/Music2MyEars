import io
import os
import json
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def ask_json(prompt):
    """Send a prompt to Gemini and parse the JSON response."""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return json.loads(_strip_json_fences(response.text))


def _strip_json_fences(text):
    """Strip markdown code fences from JSON text."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return text


def ask_json_with_image(prompt, image_bytes):
    """Send a prompt + image to Gemini and parse the JSON response."""
    client = _get_client()
    image = Image.open(io.BytesIO(image_bytes))
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, image],
    )
    return json.loads(_strip_json_fences(response.text))


def ask_text(prompt):
    """Send a prompt to Gemini and return raw text response."""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()
