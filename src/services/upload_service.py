from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import hashlib
import math

from config.settings import (
    ENABLE_GEOCODING,
    REQUIRE_AI,
    REQUIRE_GEOLOCATION,
    SUPABASE_BUCKET,
    SUPABASE_TABLE,
)
from src.database.supabase_client import get_supabase_client
from src.services.ai_service import analyze_issue_image
from src.utils.geocoding import geocode_location, reverse_geocode_location
from src.utils.geolocation import extract_gps_from_image_bytes
from src.utils.validators import validate_image_format


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two lat/lon points."""
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


class UploadService:
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = SUPABASE_TABLE
        self.bucket_name = SUPABASE_BUCKET

    # ── Image analysis ────────────────────────────────────────────────────────

    def analyze_image(self, uploaded_file):
        if uploaded_file is None:
            return {"success": False, "message": "No file selected."}

        # validate_image_format reads the file — must seek back after
        if not validate_image_format(uploaded_file):
            return {
                "success": False,
                "message": "Invalid image format. Please upload a valid image file.",
            }
        # Seek back so getvalue() / subsequent reads still work
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        original_name = Path(uploaded_file.name).name
        file_bytes = uploaded_file.getvalue()
        content_type = uploaded_file.type or "application/octet-stream"

        analysis = self._build_analysis(file_bytes=file_bytes, filename=original_name)
        if REQUIRE_AI and analysis.get("ollama_error"):
            return {
                "success": False,
                "message": f"AI analysis is required but failed: {analysis.get('ollama_error')}",
                "analysis": analysis,
            }

        return {
            "success": True,
            "message": "Image analyzed successfully.",
            "filename": original_name,
            "content_type": content_type,
            "analysis": analysis,
            "file_bytes": file_bytes,
        }

    # ── Upload ────────────────────────────────────────────────────────────────

    def upload_image(
        self,
        uploaded_file,
        manual_location=None,
        manual_latitude=None,
        manual_longitude=None,
        reporter_id=None,
    ):
        if uploaded_file is None:
            return {"success": False, "message": "No file selected."}

        if not validate_image_format(uploaded_file):
            return {
                "success": False,
                "message": "Invalid image format. Please upload a valid image file.",
            }
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        return self.upload_image_bytes(
            file_bytes=uploaded_file.getvalue(),
            original_name=Path(uploaded_file.name).name,
            content_type=uploaded_file.type or "application/octet-stream",
            manual_location=manual_location,
            manual_latitude=manual_latitude,
            manual_longitude=manual_longitude,
            reporter_id=reporter_id,
            analysis_override=None,
        )

    def upload_image_bytes(
        self,
        file_bytes,
        original_name,
        content_type,
        manual_location=None,
        manual_latitude=None,
        manual_longitude=None,
        reporter_id=None,
        analysis_override=None,
    ):
        try:
            analysis = (
                dict(analysis_override)
                if isinstance(analysis_override, dict)
                else self._build_analysis(file_bytes, original_name)
            )

            category         = analysis.get("category") or "Other"
            title            = analysis.get("title")
            severity         = analysis.get("severity") or "Medium"
            details          = analysis.get("details")
            recommended_action = analysis.get("recommended_action")
            location_hint    = analysis.get("location")
            latitude         = analysis.get("latitude")
            longitude        = analysis.get("longitude")
            ollama_error     = analysis.get("ollama_error")

            location  = manual_location or location_hint
            latitude  = manual_latitude  if manual_latitude  is not None else latitude
            longitude = manual_longitude if manual_longitude is not None else longitude

            if REQUIRE_AI and ollama_error:
                return {
                    "success": False,
                    "message": f"AI analysis is required but failed: {ollama_error}",
                    "analysis": analysis,
                }

            if (latitude is None or longitude is None) and ENABLE_GEOCODING and location:
                geocoded_lat, geocoded_lon = geocode_location(location)
                if latitude  is None: latitude  = geocoded_lat
                if longitude is None: longitude = geocoded_lon

            if REQUIRE_GEOLOCATION and (latitude is None or longitude is None):
                return {
                    "success": False,
                    "message": "Geolocation is required but could not be extracted.",
                    "analysis": {**analysis, "location": location, "latitude": latitude, "longitude": longitude},
                }

            # ── Exact-image duplicate guard ───────────────────────────────────
            image_hash = hashlib.sha256(file_bytes).hexdigest()
            try:
                existing = (
                    self.client.table(self.table_name)
                    .select("id")
                    .eq("image_hash", image_hash)
                    .limit(1)
                    .execute()
                )
                if existing and existing.data:
                    return {
                        "success": False,
                        "message": "This photo has already been reported. Thank you for flagging it.",
                    }
            except Exception:
                pass

            # ── Reporter cooldown (same category + location, 4 days) ──────────
            if reporter_id and category and location:
                now = datetime.now(timezone.utc)
                four_days_ago = now - timedelta(days=4)
                try:
                    recent = (
                        self.client.table(self.table_name)
                        .select("id, upload_date, created_at")
                        .eq("reporter_id", reporter_id)
                        .eq("category", category)
                        .eq("location", location)
                        .order("upload_date", desc=True)
                        .limit(10)
                        .execute()
                    )
                    for row in (recent.data or []):
                        ts_raw = row.get("upload_date") or row.get("created_at")
                        if not ts_raw:
                            continue
                        try:
                            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=timezone.utc)
                            if ts >= four_days_ago:
                                return {
                                    "success": False,
                                    "message": (
                                        "You have already reported this type of issue at this "
                                        "location within the last 4 days. Please give the council "
                                        "time to respond before submitting again."
                                    ),
                                }
                        except Exception:
                            continue
                except Exception:
                    pass

            # ── Upload to storage ─────────────────────────────────────────────
            object_name = (
                f"uploads/{datetime.now(timezone.utc).strftime('%Y%m%d')}/"
                f"{uuid4().hex}{Path(original_name).suffix.lower() or '.jpg'}"
            )
            self.client.storage.from_(self.bucket_name).upload(
                object_name,
                file_bytes,
                {"content-type": content_type or "application/octet-stream"},
            )
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(object_name)

            # ── Insert record ─────────────────────────────────────────────────
            payload = {
                "filename":           original_name,
                "cloud_storage_url":  public_url,
                "upload_date":        datetime.now(timezone.utc).isoformat(),
                "version":            1,
                "category":           category,
                "title":              title,
                "severity":           severity,
                "additional_details": details,
                "recommended_action": recommended_action,
                "location":           location,
                "latitude":           latitude,
                "longitude":          longitude,
                "reporter_id":        reporter_id,
                "image_hash":         image_hash,
            }
            payload = {k: v for k, v in payload.items() if v is not None}

            try:
                insert_result = self.client.table(self.table_name).insert(payload).execute()
            except Exception:
                now_iso = datetime.now(timezone.utc).isoformat()
                legacy = {k: v for k, v in {
                    "image_path":         public_url,
                    "category":           category,
                    "title":              title,
                    "severity":           severity,
                    "location":           location or "Unknown",
                    "additional_details": details,
                    "recommended_action": recommended_action,
                    "created_at":         now_iso,
                    "latitude":           latitude,
                    "longitude":          longitude,
                    "reporter_id":        reporter_id,
                    "image_hash":         image_hash,
                }.items() if v is not None}
                try:
                    insert_result = self.client.table(self.table_name).insert(legacy).execute()
                except Exception:
                    minimal = {"image_path": public_url, "category": category, "location": location or "Unknown"}
                    insert_result = self.client.table(self.table_name).insert(minimal).execute()

            return {
                "success": True,
                "message": "Image uploaded successfully.",
                "data": insert_result.data[0] if insert_result.data else payload,
                "analysis": {
                    "title":             title,
                    "category":          category,
                    "severity":          severity,
                    "details":           details,
                    "recommended_action": recommended_action,
                    "location":          location,
                    "latitude":          latitude,
                    "longitude":         longitude,
                    "ollama_error":      ollama_error,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ── Nearby duplicate detection ────────────────────────────────────────────

    def find_nearby_similar_reports(
        self,
        latitude,
        longitude,
        category: str,
        location_text: str = "",
        radius_km: float = 0.5,
    ) -> list[dict]:
        """
        Return open reports that are geographically close OR share the same
        location text and category, so the user can decide before submitting.

        Matching logic (OR):
          1. Coordinates within radius_km AND same category
          2. Normalised location text contains the same road/place name AND same category
        """
        try:
            # Fetch open reports with coordinates
            result = (
                self.client.table(self.table_name)
                .select("id, title, category, severity, location, latitude, longitude, upload_date, status")
                .neq("status", "Resolved")
                .neq("status", "Won't Fix")
                .execute()
            )
            all_reports = result.data or []
        except Exception:
            return []

        nearby: list[dict] = []

        # Normalise location text for fuzzy matching
        loc_norm = " ".join(location_text.lower().split()) if location_text else ""

        for report in all_reports:
            # Skip if category doesn't match
            if str(report.get("category") or "").strip() != category.strip():
                continue

            distance_m = None
            matched_by = None

            # --- Coordinate proximity ---
            if latitude is not None and longitude is not None:
                try:
                    r_lat = float(report.get("latitude") or 0)
                    r_lon = float(report.get("longitude") or 0)
                    if abs(r_lat) > 0.001 or abs(r_lon) > 0.001:
                        km = _haversine_km(latitude, longitude, r_lat, r_lon)
                        if km <= radius_km:
                            distance_m = int(km * 1000)
                            matched_by = "proximity"
                except (TypeError, ValueError):
                    pass

            # --- Location text match (fallback when no coords) ---
            if matched_by is None and loc_norm:
                r_loc = " ".join(str(report.get("location") or "").lower().split())
                if r_loc and (loc_norm in r_loc or r_loc in loc_norm):
                    matched_by = "location_text"

            if matched_by:
                nearby.append({
                    "id":         report.get("id"),
                    "title":      report.get("title") or "Untitled",
                    "category":   report.get("category"),
                    "severity":   report.get("severity") or "Medium",
                    "location":   report.get("location") or "Unknown",
                    "upload_date": str(report.get("upload_date") or "")[:10],
                    "distance_m": distance_m,
                    "match_type": matched_by,
                })

        # Sort: coord matches first, then by distance
        nearby.sort(key=lambda r: (
            0 if r["match_type"] == "proximity" else 1,
            r["distance_m"] if r["distance_m"] is not None else 9999,
        ))
        return nearby[:5]  # cap at 5 to avoid overwhelming the user

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_analysis(self, file_bytes, filename):
        inferred_lat, inferred_lon = extract_gps_from_image_bytes(file_bytes)
        ai_result = analyze_issue_image(file_bytes, filename)

        category   = ai_result.get("category") or "Other"
        description = ai_result.get("description") or ai_result.get("details")
        title      = ai_result.get("title")
        severity   = ai_result.get("severity") or "Medium"
        recommended_action = ai_result.get("recommended_action")
        location   = ai_result.get("location_hint")
        latitude   = inferred_lat
        longitude  = inferred_lon

        if (not location or not str(location).strip()) and latitude is not None and longitude is not None:
            location = reverse_geocode_location(latitude, longitude)

        if (latitude is None or longitude is None) and ENABLE_GEOCODING and location:
            geocoded_lat, geocoded_lon = geocode_location(location)
            if latitude  is None: latitude  = geocoded_lat
            if longitude is None: longitude = geocoded_lon

        return {
            "title":             title,
            "category":          category,
            "severity":          severity,
            "details":           description,
            "recommended_action": recommended_action,
            "location":          location,
            "latitude":          latitude,
            "longitude":         longitude,
            "ollama_error":      ai_result.get("error"),
            "ai_enabled":        ai_result.get("enabled", False),
            "ai_raw":            ai_result.get("raw"),
            "ai_confidence":     ai_result.get("confidence"),
        }

    def list_uploaded_images(self):
        try:
            try:
                result = (
                    self.client.table(self.table_name)
                    .select("*")
                    .order("upload_date", desc=True)
                    .execute()
                )
            except Exception:
                try:
                    result = (
                        self.client.table(self.table_name)
                        .select("*")
                        .order("created_at", desc=True)
                        .execute()
                    )
                except Exception:
                    result = self.client.table(self.table_name).select("*").execute()

            rows = result.data or []
            normalized = []
            for row in rows:
                r = dict(row)
                r["filename"]          = row.get("filename") or row.get("image_name") or "uploaded_image"
                r["cloud_storage_url"] = row.get("cloud_storage_url") or row.get("image_path")
                r["upload_date"]       = row.get("upload_date") or row.get("created_at")
                normalized.append(r)
            return normalized
        except Exception:
            return []

    def update_report(self, report_id, updates: dict) -> dict:
        """Update a report's status, assignment, or council notes."""
        try:
            updates = {k: v for k, v in updates.items() if v is not None or k in ("assigned_to", "council_notes")}
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            if updates.get("status") == "Resolved" and "resolved_at" not in updates:
                updates["resolved_at"] = datetime.now(timezone.utc).isoformat()
            result = (
                self.client.table(self.table_name)
                .update(updates)
                .eq("id", report_id)
                .execute()
            )
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_report(self, report_id) -> dict:
        """
        Permanently delete a report by ID.
        Also removes any associated votes rows to keep the DB clean.
        Storage object is NOT deleted (Supabase Storage has its own retention).
        """
        try:
            # Remove votes first (foreign key may not cascade automatically)
            try:
                self.client.table("votes").delete().eq(
                    "report_id", str(report_id)
                ).execute()
            except Exception:
                pass  # votes table may not exist yet — non-fatal

            self.client.table(self.table_name).delete().eq(
                "id", report_id
            ).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def add_vote(self, report_id: str, user_id: str) -> dict:
        """
        Record an upvote atomically via Supabase RPC.
        Requires this SQL function to exist:
          CREATE OR REPLACE FUNCTION increment_upvotes(report_id text)
          RETURNS void LANGUAGE sql AS $$
            UPDATE reports SET upvotes = COALESCE(upvotes, 0) + 1 WHERE id::text = report_id;
          $$;
        """
        try:
            self.client.table("votes").insert({
                "report_id": str(report_id),
                "user_id":   str(user_id),
            }).execute()
            self.client.rpc("increment_upvotes", {"report_id": str(report_id)}).execute()
            return {"success": True}
        except Exception as e:
            msg = str(e)
            if "duplicate" in msg.lower() or "unique" in msg.lower():
                return {"success": False, "message": "You have already upvoted this report."}
            return {"success": False, "message": msg}

    def get_user_votes(self, user_id: str) -> list[str]:
        """Return list of report_id strings the user has already upvoted."""
        try:
            result = (
                self.client.table("votes")
                .select("report_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            return [row["report_id"] for row in (result.data or [])]
        except Exception:
            return []