import base64
import io
import json

import requests
from PIL import Image

from config.settings import (
    ANTHROPIC_API_KEY,
    ENABLE_OLLAMA,
    OLLAMA_MODEL,
    OLLAMA_URL,
)

VALID_CATEGORIES = [
    "Pothole",
    "Broken Streetlight",
    "Graffiti",
    "Fly-Tipping / Illegal Dumping",
    "Litter / Overflowing Bin",
    "Damaged Road Sign",
    "Pavement / Footpath Damage",
    "Abandoned Vehicle",
    "Overgrown Vegetation",
    "Flooding / Drainage Issue",
    "Vandalism",
    "Other",
]

VALID_SEVERITIES = ["Low", "Medium", "High", "Critical"]

_PROMPT = (
    "Analyze this image of a community issue. "
    "Reply with ONLY a JSON object, no other text. "
    "Use these exact keys:\n"
    "category (one of: {categories}), "
    "severity (one of: Low, Medium, High, Critical), "
    "title (short headline under 10 words), "
    "description (1-2 sentences about what is wrong), "
    "location_hint (any visible street name or landmark, or null), "
    "recommended_action (what the council should do).\n"
    'Example: {{"category":"Pothole","severity":"High",'
    '"title":"Large pothole on main road",'
    '"description":"Deep pothole causing vehicle damage.",'
    '"location_hint":null,"recommended_action":"Fill and repave pothole."}}'
)


def _empty_result(enabled: bool, error=None):
    return {
        "enabled": enabled,
        "title": None,
        "category": None,
        "severity": None,
        "description": None,
        "location_hint": None,
        "recommended_action": None,
        "raw": None,
        "error": error,
    }


def _parse_ai_response(content: str) -> dict:
    """Parse JSON from AI response text, with fallback bracket search."""
    parsed = {}
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start != -1 and end > start:
            try:
                parsed = json.loads(content[start: end + 1])
            except json.JSONDecodeError:
                pass
    return parsed if isinstance(parsed, dict) else {}


def _normalize(parsed: dict) -> dict:
    raw_cat = str(parsed.get("category") or "Other").strip()
    raw_sev = str(parsed.get("severity") or "Medium").strip()
    return {
        "enabled": True,
        "title": parsed.get("title"),
        "category": raw_cat if raw_cat in VALID_CATEGORIES else "Other",
        "severity": raw_sev if raw_sev in VALID_SEVERITIES else "Medium",
        "description": parsed.get("description"),
        "location_hint": parsed.get("location_hint"),
        "recommended_action": parsed.get("recommended_action"),
        "raw": json.dumps(parsed),
        "error": None,
    }


def _compress_image_if_needed(file_bytes: bytes, max_size_mb: float = 5.0) -> bytes:
    """
    Compress image if it exceeds max_size_mb.
    Claude's API has a 5MB limit for images.
    """
    # Check if compression is needed
    if len(file_bytes) <= (max_size_mb * 1024 * 1024):
        return file_bytes
    
    try:
        # Open image and resize
        img = Image.open(io.BytesIO(file_bytes))
        
        # Convert RGBA to RGB if needed (for JPEG export)
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        
        # Resize to reasonable dimensions (max 2048 pixels on longest side)
        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        
        # Compress and save as JPEG
        output = io.BytesIO()
        quality = 85
        while quality >= 50:
            output.seek(0)
            output.truncate(0)
            img.save(output, format="JPEG", quality=quality, optimize=True)
            if len(output.getvalue()) <= (max_size_mb * 1024 * 1024):
                return output.getvalue()
            quality -= 5
        
        # Fallback: return best effort at quality 50
        return output.getvalue()
    
    except Exception:
        # If compression fails, return original (Claude will error but gracefully)
        return file_bytes



def _analyze_with_claude(file_bytes: bytes, filename: str) -> dict:
    """Use Anthropic Claude (claude-haiku) for vision analysis."""
    try:
        import anthropic

        # Compress image if needed (Claude has 5MB limit)
        compressed_bytes = _compress_image_if_needed(file_bytes, max_size_mb=5.0)

        # Detect media type from filename
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpeg"
        media_type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
        media_type = media_type_map.get(ext, "image/jpeg")

        encoded = base64.standard_b64encode(compressed_bytes).decode("utf-8")
        prompt = _PROMPT.format(categories=", ".join(VALID_CATEGORIES))

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": encoded,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        content = message.content[0].text.strip() if message.content else ""
        parsed = _parse_ai_response(content)
        return _normalize(parsed)

    except Exception as e:
        return {**_empty_result(True), "error": str(e)}


def _analyze_with_ollama(file_bytes: bytes, filename: str) -> dict:
    """Use local Ollama (LLaVA) for vision analysis."""
    try:
        encoded = base64.b64encode(file_bytes).decode("utf-8")
        prompt = _PROMPT.format(categories=", ".join(VALID_CATEGORIES))

        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt, "images": [encoded]}
                ],
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "").strip()
        parsed = _parse_ai_response(content)
        return _normalize(parsed)

    except Exception as e:
        return {**_empty_result(True), "error": str(e)}


def analyze_issue_image(file_bytes: bytes, filename: str) -> dict:
    """
    Analyze an image of a community issue.
    Priority: Claude API (cloud) → Ollama (local) → disabled.
    """
    if ANTHROPIC_API_KEY:
        return _analyze_with_claude(file_bytes, filename)

    if ENABLE_OLLAMA:
        return _analyze_with_ollama(file_bytes, filename)

    return _empty_result(enabled=False)