from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config.settings import (
    ENABLE_GEOCODING,
    REQUIRE_AI,
    REQUIRE_GEOLOCATION,
    SUPABASE_BUCKET,
    SUPABASE_TABLE,
)
from src.services.ai_service import analyze_issue_image
from src.database.supabase_client import get_supabase_client
from src.utils.geocoding import geocode_location
from src.utils.geolocation import extract_gps_from_image_bytes
from src.utils.validators import validate_image_format


class UploadService:
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = SUPABASE_TABLE
        self.bucket_name = SUPABASE_BUCKET

    def upload_image(self, uploaded_file, manual_location=None, manual_latitude=None, manual_longitude=None):
        if uploaded_file is None:
            return {"success": False, "message": "No file selected."}

        if not validate_image_format(uploaded_file):
            return {
                "success": False,
                "message": "Invalid image format. Please upload a valid image file.",
            }

        try:
            original_name = Path(uploaded_file.name).name
            extension = Path(original_name).suffix.lower() or ".jpg"
            object_name = f"uploads/{datetime.now(timezone.utc).strftime('%Y%m%d')}/{uuid4().hex}{extension}"
            file_bytes = uploaded_file.getvalue()
            inferred_latitude, inferred_longitude = extract_gps_from_image_bytes(file_bytes)
            ai_result = analyze_issue_image(file_bytes, original_name)

            if REQUIRE_AI:
                if not ai_result.get("enabled"):
                    return {
                        "success": False,
                        "message": "AI analysis is required, but Ollama is disabled. Enable ENABLE_OLLAMA in secrets.",
                    }
                if ai_result.get("error"):
                    return {
                        "success": False,
                        "message": f"AI analysis is required but failed: {ai_result.get('error')}",
                    }
                if not ai_result.get("category"):
                    return {
                        "success": False,
                        "message": "AI analysis is required but no category was returned.",
                    }

            latitude = inferred_latitude if inferred_latitude is not None else manual_latitude
            longitude = inferred_longitude if inferred_longitude is not None else manual_longitude

            category = ai_result.get("category") or "Other"
            details = ai_result.get("details")
            location = manual_location or ai_result.get("location_hint")

            if (latitude is None or longitude is None) and ENABLE_GEOCODING and location:
                geocoded_lat, geocoded_lon = geocode_location(location)
                if latitude is None:
                    latitude = geocoded_lat
                if longitude is None:
                    longitude = geocoded_lon

            if REQUIRE_GEOLOCATION and (latitude is None or longitude is None):
                return {
                    "success": False,
                    "message": "Geolocation is required but could not be extracted. Please provide a clearer location.",
                }

            self.client.storage.from_(self.bucket_name).upload(
                object_name,
                file_bytes,
                {"content-type": uploaded_file.type or "application/octet-stream"},
            )

            public_url = self.client.storage.from_(self.bucket_name).get_public_url(object_name)

            payload = {
                "filename": original_name,
                "cloud_storage_url": public_url,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "version": 1,
                "category": category,
                "additional_details": details,
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
                    "location": location or "Unknown",
                    "additional_details": details,
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
                    "category": category,
                    "details": details,
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                    "ollama_error": ai_result.get("error"),
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

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
