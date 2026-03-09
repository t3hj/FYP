import base64
import json

import requests

from config.settings import ENABLE_OLLAMA, OLLAMA_MODEL, OLLAMA_URL

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


def analyze_issue_image(file_bytes, filename):
    """
    Analyze an image of a community issue using Ollama LLaVA.
    Returns a rich structured result mimicking a FixMyStreet-style report
    so users are not required to fill in any form fields manually.
    """
    if not ENABLE_OLLAMA:
        return {
            "enabled": False,
            "title": None,
            "category": None,
            "severity": None,
            "description": None,
            "location_hint": None,
            "recommended_action": None,
            "raw": None,
            "error": None,
        }

    try:
        encoded = base64.b64encode(file_bytes).decode("utf-8")

        categories_str = ", ".join(VALID_CATEGORIES)
        prompt = (
            "Analyze this image of a community issue. "
            "Reply with ONLY a JSON object, no other text. "
            "Use these exact keys:\n"
            f"category (one of: {categories_str}), "
            "severity (one of: Low, Medium, High, Critical), "
            "title (short headline under 10 words), "
            "description (1-2 sentences about what is wrong), "
            "location_hint (any visible street name or landmark, or null), "
            "recommended_action (what the council should do).\n"
            "Example: {\"category\":\"Pothole\",\"severity\":\"High\","
            "\"title\":\"Large pothole on main road\","
            "\"description\":\"Deep pothole causing vehicle damage.\","
            "\"location_hint\":null,\"recommended_action\":\"Fill and repave pothole.\"}"
        )

        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [encoded],
                    }
                ],
                "stream": False,
            },
            timeout=90,
        )
        response.raise_for_status()

        content = (
            response.json()
            .get("message", {})
            .get("content", "")
            .strip()
        )

        parsed = {}
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}

        # Validate / normalise category
        raw_category = str(parsed.get("category") or "Other").strip()
        category = raw_category if raw_category in VALID_CATEGORIES else "Other"

        # Validate / normalise severity
        raw_severity = str(parsed.get("severity") or "Medium").strip()
        severity = raw_severity if raw_severity in VALID_SEVERITIES else "Medium"

        return {
            "enabled": True,
            "title": parsed.get("title"),
            "category": category,
            "severity": severity,
            "description": parsed.get("description"),
            "location_hint": parsed.get("location_hint"),
            "recommended_action": parsed.get("recommended_action"),
            "raw": content,
            "error": None,
        }

    except Exception as e:
        return {
            "enabled": True,
            "title": None,
            "category": None,
            "severity": None,
            "description": None,
            "location_hint": None,
            "recommended_action": None,
            "raw": None,
            "error": str(e),
        }

