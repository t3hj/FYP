"""
Priority Scoring Service
========================
Computes a 0–100 priority score for each report based on four signals:

  1. Severity       (AI-assessed at upload)  — up to 40 pts
  2. Time open      (days since reported)     — up to 25 pts
  3. Community votes (upvotes)               — up to 20 pts
  4. Local density  (nearby open reports)    — up to 15 pts

Total = sum of all four components, capped at 100.

Threshold bands:
  80–100  Critical Priority   — immediate attention required
  60–79   High Priority       — action this week
  40–59   Medium Priority     — schedule for next sprint
  0–39    Low Priority        — monitor

Usage:
    from src.services.priority_service import score_reports

    scored = score_reports(reports)   # list of dicts, sorted highest → lowest
    top_report = scored[0]
    print(top_report["_priority_score"])        # e.g. 87
    print(top_report["_priority_breakdown"])    # dict of component scores
    print(top_report["_priority_band"])         # "Critical Priority"
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional


# ── Component weights ─────────────────────────────────────────────────────────

_SEVERITY_SCORES = {
    "Critical": 40,
    "High":     30,
    "Medium":   20,
    "Low":      10,
}

_MAX_TIME_PTS    = 25   # saturates at 50 days open
_MAX_VOTE_PTS    = 20   # saturates at 10 upvotes
_MAX_DENSITY_PTS = 15   # saturates at 5 nearby reports

_BAND_THRESHOLDS = [
    (80, "Critical Priority", "#7c3aed"),
    (60, "High Priority",     "#ef4444"),
    (40, "Medium Priority",   "#f59e0b"),
    (0,  "Low Priority",      "#22c55e"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(raw) -> Optional[datetime]:
    if not raw:
        return None
    try:
        s = str(raw).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in kilometres."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _severity_component(report: dict) -> int:
    sev = str(report.get("severity") or "Medium").strip()
    return _SEVERITY_SCORES.get(sev, 20)


def _time_component(report: dict, now: datetime) -> float:
    """
    Logarithmic growth so very old reports don't completely dominate.
    Full 25 pts reached at ~50 days open.
    """
    status = str(report.get("status") or "Open").strip()
    if status in ("Resolved", "Won't Fix"):
        return 0.0

    dt = _parse_date(report.get("upload_date") or report.get("created_at"))
    if not dt:
        return 0.0

    days_open = max((now - dt).total_seconds() / 86400, 0)
    # log curve: 1 day → ~4 pts, 7 days → ~13 pts, 30 days → ~21 pts, 50 days → 25 pts
    score = _MAX_TIME_PTS * math.log1p(days_open) / math.log1p(50)
    return min(score, _MAX_TIME_PTS)


def _vote_component(report: dict) -> float:
    votes = int(report.get("upvotes") or 0)
    score = _MAX_VOTE_PTS * math.log1p(votes) / math.log1p(10)
    return min(score, _MAX_VOTE_PTS)


def _density_component(report: dict, all_reports: list[dict], radius_km: float = 1.0) -> float:
    """Count OTHER open reports within radius_km of this report."""
    try:
        lat = float(report.get("latitude") or 0)
        lon = float(report.get("longitude") or 0)
    except (TypeError, ValueError):
        return 0.0

    if abs(lat) < 0.001 and abs(lon) < 0.001:
        return 0.0

    report_id = report.get("id")
    nearby = 0
    for other in all_reports:
        if other.get("id") == report_id:
            continue
        status = str(other.get("status") or "Open")
        if status in ("Resolved", "Won't Fix"):
            continue
        try:
            olat = float(other.get("latitude") or 0)
            olon = float(other.get("longitude") or 0)
        except (TypeError, ValueError):
            continue
        if abs(olat) < 0.001 and abs(olon) < 0.001:
            continue
        if _haversine_km(lat, lon, olat, olon) <= radius_km:
            nearby += 1

    score = _MAX_DENSITY_PTS * math.log1p(nearby) / math.log1p(5)
    return min(score, _MAX_DENSITY_PTS)


def _priority_band(score: float) -> tuple[str, str]:
    """Return (band_label, hex_colour) for a given score."""
    for threshold, label, colour in _BAND_THRESHOLDS:
        if score >= threshold:
            return label, colour
    return "Low Priority", "#22c55e"


# ── Public API ────────────────────────────────────────────────────────────────

def compute_priority(report: dict, all_reports: list[dict]) -> dict:
    """
    Return a priority dict for a single report:
      {
        "score":     float  0–100,
        "band":      str,
        "colour":    str    hex,
        "breakdown": {
            "severity":  int,
            "time_open": float,
            "votes":     float,
            "density":   float,
        }
      }
    """
    now = datetime.now(timezone.utc)

    sev_pts     = _severity_component(report)
    time_pts    = _time_component(report, now)
    vote_pts    = _vote_component(report)
    density_pts = _density_component(report, all_reports)

    total = min(sev_pts + time_pts + vote_pts + density_pts, 100.0)
    band, colour = _priority_band(total)

    return {
        "score":   round(total, 1),
        "band":    band,
        "colour":  colour,
        "breakdown": {
            "severity":  sev_pts,
            "time_open": round(time_pts, 1),
            "votes":     round(vote_pts, 1),
            "density":   round(density_pts, 1),
        },
    }


def score_reports(reports: list[dict]) -> list[dict]:
    """
    Attach priority metadata to each report and return the list
    sorted highest → lowest score.

    Each report dict gains three extra keys:
      _priority_score     float
      _priority_band      str
      _priority_breakdown dict
      _priority_colour    str
    """
    scored = []
    for report in reports:
        p = compute_priority(report, reports)
        enriched = dict(report)
        enriched["_priority_score"]     = p["score"]
        enriched["_priority_band"]      = p["band"]
        enriched["_priority_breakdown"] = p["breakdown"]
        enriched["_priority_colour"]    = p["colour"]
        scored.append(enriched)

    scored.sort(key=lambda r: r["_priority_score"], reverse=True)
    return scored