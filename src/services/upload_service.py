from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from config.settings import (
    ENABLE_GEOCODING,
    REQUIRE_AI,
    REQUIRE_GEOLOCATION,
    SUPABASE_BUCKET,
    SUPABASE_TABLE,
)
from src.database.supabase_client import get_supabase_client
from src.services.ai_service import analyze_issue_image
from src.utils.geocoding import geocode_location
from src.utils.geolocation import extract_gps_from_image_bytes
from src.utils.validators import validate_image_format


class UploadService:
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = SUPABASE_TABLE
        self.bucket_name = SUPABASE_BUCKET

    def analyze_image(self, uploaded_file):
        if uploaded_file is None:
            return {"success": False, "message": "No file selected."}

        if not validate_image_format(uploaded_file):
            return {
                "success": False,
                "message": "Invalid image format. Please upload a valid image file.",
            }

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

    def upload_image(self, uploaded_file, manual_location=None, manual_latitude=None, manual_longitude=None):
        if uploaded_file is None:
            return {"success": False, "message": "No file selected."}

        if not validate_image_format(uploaded_file):
            return {
                "success": False,
                "message": "Invalid image format. Please upload a valid image file.",
            }

        return self.upload_image_bytes(
            file_bytes=uploaded_file.getvalue(),
            original_name=Path(uploaded_file.name).name,
            content_type=uploaded_file.type or "application/octet-stream",
            manual_location=manual_location,
            manual_latitude=manual_latitude,
            manual_longitude=manual_longitude,
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
        analysis_override=None,
    ):
        try:
            analysis = dict(analysis_override) if isinstance(analysis_override, dict) else self._build_analysis(file_bytes, original_name)

            category = analysis.get("category") or "Other"
            title = analysis.get("title")
            severity = analysis.get("severity") or "Medium"
            details = analysis.get("details")
            recommended_action = analysis.get("recommended_action")
            location_hint = analysis.get("location")
            latitude = analysis.get("latitude")
            longitude = analysis.get("longitude")
            ollama_error = analysis.get("ollama_error")

            location = manual_location or location_hint
            latitude = manual_latitude if manual_latitude is not None else latitude
            longitude = manual_longitude if manual_longitude is not None else longitude

            if REQUIRE_AI:
                if ollama_error:
                    return {
                        "success": False,
                        "message": f"AI analysis is required but failed: {ollama_error}",
                        "analysis": analysis,
                    }
                if not category:
                    return {
                        "success": False,
                        "message": "AI analysis is required but no category was returned.",
                        "analysis": analysis,
                    }

            if (latitude is None or longitude is None) and ENABLE_GEOCODING and location:
                geocoded_lat, geocoded_lon = geocode_location(location)
                if latitude is None:
                    latitude = geocoded_lat
                if longitude is None:
                    longitude = geocoded_lon

            if REQUIRE_GEOLOCATION and (latitude is None or longitude is None):
                return {
                    "success": False,
                    "message": "Geolocation is required but could not be extracted. Enter a location before submitting.",
                    "analysis": {
                        **analysis,
                        "location": location,
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                }

            object_name = f"uploads/{datetime.now(timezone.utc).strftime('%Y%m%d')}/{uuid4().hex}{Path(original_name).suffix.lower() or '.jpg'}"
            self.client.storage.from_(self.bucket_name).upload(
                object_name,
                file_bytes,
                {"content-type": content_type or "application/octet-stream"},
            )
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(object_name)

            payload = {
                "filename": original_name,
                "cloud_storage_url": public_url,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "version": 1,
                "category": category,
                "title": title,
                "severity": severity,
                "additional_details": details,
                "recommended_action": recommended_action,
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
            }
            payload = {key: value for key, value in payload.items() if value is not None}

            try:
                insert_result = self.client.table(self.table_name).insert(payload).execute()
            except Exception:
                now_iso = datetime.now(timezone.utc).isoformat()
                legacy_payload = {
                    "image_path": public_url,
                    "category": category,
                    "title": title,
                    "severity": severity,
                    "location": location or "Unknown",
                    "additional_details": details,
                    "recommended_action": recommended_action,
                    "created_at": now_iso,
                    "latitude": latitude,
                    "longitude": longitude,
                }
                legacy_payload = {key: value for key, value in legacy_payload.items() if value is not None}

                try:
                    insert_result = self.client.table(self.table_name).insert(legacy_payload).execute()
                except Exception:
                    minimal_payload = {
                        "image_path": public_url,
                        "category": category,
                        "location": location or "Unknown",
                    }
                    insert_result = self.client.table(self.table_name).insert(minimal_payload).execute()

            return {
                "success": True,
                "message": "Image uploaded successfully.",
                "data": insert_result.data[0] if insert_result.data else payload,
                "analysis": {
                    "title": title,
                    "category": category,
                    "severity": severity,
                    "details": details,
                    "recommended_action": recommended_action,
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                    "ollama_error": ollama_error,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _build_analysis(self, file_bytes, filename):
        inferred_latitude, inferred_longitude = extract_gps_from_image_bytes(file_bytes)
        ai_result = analyze_issue_image(file_bytes, filename)

        category = ai_result.get("category") or "Other"
        # Support both old "details" key and new "description" key from AI service
        description = ai_result.get("description") or ai_result.get("details")
        title = ai_result.get("title")
        severity = ai_result.get("severity") or "Medium"
        recommended_action = ai_result.get("recommended_action")
        location = ai_result.get("location_hint")
        latitude = inferred_latitude
        longitude = inferred_longitude

        if (latitude is None or longitude is None) and ENABLE_GEOCODING and location:
            geocoded_lat, geocoded_lon = geocode_location(location)
            if latitude is None:
                latitude = geocoded_lat
            if longitude is None:
                longitude = geocoded_lon

        return {
            "title": title,
            "category": category,
            "severity": severity,
            "details": description,
            "recommended_action": recommended_action,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "ollama_error": ai_result.get("error"),
            "ai_enabled": ai_result.get("enabled", False),
            "ai_raw": ai_result.get("raw"),
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
            normalized_rows = []
            for row in rows:
                normalized = dict(row)
                normalized["filename"] = row.get("filename") or row.get("image_name") or "uploaded_image"
                normalized["cloud_storage_url"] = row.get("cloud_storage_url") or row.get("image_path")
                normalized["upload_date"] = row.get("upload_date") or row.get("created_at")
                normalized_rows.append(normalized)

            return normalized_rows
        except Exception:
            return []
