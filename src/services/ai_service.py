import base64
import json

import requests

from config.settings import ENABLE_OLLAMA, OLLAMA_MODEL, OLLAMA_URL


def analyze_issue_image(file_bytes, filename):
    if not ENABLE_OLLAMA:
        return {
            "enabled": False,
            "category": None,
            "details": None,
            "location_hint": None,
            "raw": None,
            "error": None,
        }

    try:
        encoded = base64.b64encode(file_bytes).decode("utf-8")
        prompt = (
            "Analyze this community issue image and respond as strict JSON with keys: "
            "category, details, location_hint. "
            "category should be one of: Pothole, Broken Streetlight, Graffiti, Litter, "
            "Damaged Road Sign, Other. "
            "details should be a short factual description. "
            "location_hint should be any visible location clue text, otherwise null."
        )

        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Filename: {filename}. {prompt}",
                        "images": [encoded],
                    }
                ],
                "stream": False,
            },
            timeout=60,
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
                parsed = json.loads(content[start:end + 1])

        return {
            "enabled": True,
            "category": parsed.get("category") if isinstance(parsed, dict) else None,
            "details": parsed.get("details") if isinstance(parsed, dict) else None,
            "location_hint": parsed.get("location_hint") if isinstance(parsed, dict) else None,
            "raw": content,
            "error": None,
        }
    except Exception as e:
        return {
            "enabled": True,
            "category": None,
            "details": None,
            "location_hint": None,
            "raw": None,
            "error": str(e),
        }
