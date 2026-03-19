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

# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are an AI assistant for Local Lens, a UK council community issue reporting platform. "
    "Your job is to analyse photos uploaded by residents and extract structured report data. "
    "Always respond with ONLY a valid JSON object — no markdown, no preamble, no explanation. "
    "Be concise, accurate, and use British English spelling."
)

_USER_PROMPT = """\
Analyse this photo of a community issue and return a JSON object with these exact keys:

  category        — one of: {categories}
  severity        — one of: Low, Medium, High, Critical
                    Use this calibration:
                    • Low      = cosmetic/minor (small litter, minor scuff)
                    • Medium   = inconvenience, no immediate safety risk (overflowing bin, faded markings)
                    • High     = safety risk if not addressed within days (large pothole, broken streetlight, exposed wiring)
                    • Critical = immediate danger or significant impact (collapsed road, raw sewage, structure at risk)
  title           — a short headline under 10 words describing the specific problem
  description     — 2–3 sentences: what is wrong, how bad it looks, any visible hazard
  location_hint   — any visible street name, road sign, landmark or postcode in the image; null if none visible
  recommended_action — specific action the council should take (e.g. "Resurface 2m² section of pavement")
  confidence      — your confidence in the category assignment: "high", "medium", or "low"

Example output:
{{"category":"Pavement / Footpath Damage","severity":"High","title":"Large crack splitting pavement slab","description":"A significant longitudinal crack has split a paving slab near a pedestrian crossing, creating a trip hazard approximately 3cm deep. The raised edge poses a fall risk especially for elderly pedestrians and wheelchair users.","location_hint":"Junction of High Street and Mill Road","recommended_action":"Replace damaged slab and inspect adjacent slabs for similar movement.","confidence":"high"}}
"""


def _empty_result(enabled: bool, error=None):
    return {
        "enabled": enabled,
        "title": None,
        "category": None,
        "severity": None,
        "description": None,
        "location_hint": None,
        "recommended_action": None,
        "confidence": None,
        "raw": None,
        "error": error,
    }


def _parse_ai_response(content: str) -> dict:
    """Parse JSON from AI response text, with fallback bracket search."""
    # Strip common LLM markdown wrapping
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

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
    raw_conf = str(parsed.get("confidence") or "medium").strip().lower()

    # Partial match fallback for category (handles minor wording differences)
    if raw_cat not in VALID_CATEGORIES:
        raw_cat_lower = raw_cat.lower()
        matched = next(
            (c for c in VALID_CATEGORIES if c.lower() in raw_cat_lower or raw_cat_lower in c.lower()),
            "Other",
        )
        raw_cat = matched

    return {
        "enabled": True,
        "title": parsed.get("title"),
        "category": raw_cat if raw_cat in VALID_CATEGORIES else "Other",
        "severity": raw_sev if raw_sev in VALID_SEVERITIES else "Medium",
        "description": parsed.get("description"),
        "location_hint": parsed.get("location_hint"),
        "recommended_action": parsed.get("recommended_action"),
        "confidence": raw_conf if raw_conf in ("high", "medium", "low") else "medium",
        "raw": json.dumps(parsed),
        "error": None,
    }


def _compress_image_if_needed(file_bytes: bytes, max_size_mb: float = 5.0) -> bytes:
    """Compress image if it exceeds max_size_mb (Claude API limit)."""
    if len(file_bytes) <= (max_size_mb * 1024 * 1024):
        return file_bytes

    try:
        img = Image.open(io.BytesIO(file_bytes))

        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img

        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        quality = 85
        while quality >= 50:
            output.seek(0)
            output.truncate(0)
            img.save(output, format="JPEG", quality=quality, optimize=True)
            if len(output.getvalue()) <= (max_size_mb * 1024 * 1024):
                return output.getvalue()
            quality -= 5

        return output.getvalue()

    except Exception:
        return file_bytes


def _analyze_with_claude(file_bytes: bytes, filename: str) -> dict:
    """Use Anthropic Claude for vision analysis with system prompt."""
    try:
        import anthropic

        compressed_bytes = _compress_image_if_needed(file_bytes, max_size_mb=5.0)

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpeg"
        media_type_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        encoded = base64.standard_b64encode(compressed_bytes).decode("utf-8")
        prompt = _USER_PROMPT.format(categories=", ".join(VALID_CATEGORIES))

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=_SYSTEM_PROMPT,
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
        # Ollama doesn't support a separate system prompt in the same way,
        # so prepend it to the user prompt
        prompt = _SYSTEM_PROMPT + "\n\n" + _USER_PROMPT.format(categories=", ".join(VALID_CATEGORIES))

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
    Analyse an image of a community issue.
    Priority: Claude API (cloud) → Ollama (local) → disabled.

    Returns dict with keys:
      enabled, title, category, severity, description, location_hint,
      recommended_action, confidence, raw, error
    """
    if ANTHROPIC_API_KEY:
        return _analyze_with_claude(file_bytes, filename)

    if ENABLE_OLLAMA:
        return _analyze_with_ollama(file_bytes, filename)

    return _empty_result(enabled=False)