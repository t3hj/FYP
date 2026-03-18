from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import hashlib

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

            # Compute a stable hash of the image bytes to prevent exact duplicate uploads.
            image_hash = hashlib.sha256(file_bytes).hexdigest()

            # Check for an existing report with the same image hash.
            try:
                existing_hash = (
                    self.client.table(self.table_name)
                    .select("id, upload_date, created_at")
                    .eq("image_hash", image_hash)
                    .limit(1)
                    .execute()
                )
            except Exception:
                existing_hash = None

            if existing_hash and existing_hash.data:
                return {
                    "success": False,
                    "message": "This photo has already been reported. Thank you for flagging it.",
                }

            # Enforce a cooldown: prevent the same reporter from reporting the same issue
            # (same category and location) within the last 4 days.
            if reporter_id and (category and location):
                now = datetime.now(timezone.utc)
                four_days_ago = now - timedelta(days=4)

                try:
                    recent_reports = (
                        self.client.table(self.table_name)
                        .select("id, category, location, upload_date, created_at")
                        .eq("reporter_id", reporter_id)
                        .eq("category", category)
                        .eq("location", location)
                        .order("upload_date", desc=True)
                        .limit(10)
                        .execute()
                    )
                except Exception:
                    recent_reports = None

                if recent_reports and recent_reports.data:
                    for row in recent_reports.data:
                        ts_raw = row.get("upload_date") or row.get("created_at")
                        if not ts_raw:
                            continue
                        try:
                            # Handle both plain ISO strings and ones ending with 'Z'
                            ts_str = str(ts_raw).replace("Z", "+00:00")
                            ts = datetime.fromisoformat(ts_str)
                        except Exception:
                            continue
                        # Assume timestamps without tz are UTC
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts >= four_days_ago:
                            return {
                                "success": False,
                                "message": (
                                    "You have already reported this type of issue at this location "
                                    "within the last 4 days. Please give the council time to respond "
                                    "before submitting another report for the same problem."
                                ),
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
                "reporter_id": reporter_id,
                "image_hash": image_hash,
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
                    "reporter_id": reporter_id,
                    "image_hash": image_hash,
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

        # Fallback: if Claude didn't extract location but EXIF has GPS, reverse geocode it
        if (not location or not str(location).strip()) and latitude is not None and longitude is not None:
            location = reverse_geocode_location(latitude, longitude)

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

    def find_nearby_similar_reports(self, latitude, longitude, category, location_text=None, radius_km=0.5):
        """
        Find reports within a certain radius with the same category.
        Uses Haversine formula for GPS coordinates, or location text matching as fallback.
        
        Args:
            latitude: Report latitude (optional)
            longitude: Report longitude (optional)
            category: Report category
            location_text: Location as text (optional, used if no coordinates)
            radius_km: Search radius in kilometers (default 0.5km ≈ 500m)
        
        Returns:
            List of nearby similar reports (within radius, same category)
        """
        if latitude is None and longitude is None and not location_text:
            return []
        
        try:
            all_reports = self.list_uploaded_images()
        except Exception:
            return []
        
        nearby = []
        has_coordinates = latitude is not None and longitude is not None
        
        for report in all_reports:
            report_lat = report.get("latitude")
            report_lon = report.get("longitude")
            report_location = report.get("location", "")
            report_category = report.get("category", "Unknown")
            
            # Skip if different category
            if str(report_category).strip() != str(category).strip():
                continue
            
            distance_m = None
            match_type = None
            
            # Try GPS-based proximity search first
            if has_coordinates and report_lat is not None and report_lon is not None:
                try:
                    report_lat = float(report_lat)
                    report_lon = float(report_lon)
                    lat_f = float(latitude)
                    lon_f = float(longitude)
                    
                    distance_km = self._haversine_distance(lat_f, lon_f, report_lat, report_lon)
                    if distance_km <= radius_km:
                        distance_m = int(distance_km * 1000)
                        match_type = "proximity"
                except (TypeError, ValueError):
                    pass
            
            # Fallback to location text matching if no coordinates or GPS search didn't match
            if match_type is None and location_text and str(report_location).strip():
                location_normalized = str(location_text).strip().lower()
                report_location_normalized = str(report_location).strip().lower()
                
                # Exact match or substring match (e.g., "Main Street" in "Main Street near Town Hall")
                if location_normalized == report_location_normalized or \
                   (len(location_normalized) > 4 and location_normalized in report_location_normalized) or \
                   (len(report_location_normalized) > 4 and report_location_normalized in location_normalized):
                    distance_m = 0  # Location match, distance unknown
                    match_type = "location_text"
            
            if match_type:
                nearby.append({
                    "id": report.get("id"),
                    "title": report.get("title") or report.get("filename", "Untitled"),
                    "location": report.get("location", "Unknown"),
                    "severity": report.get("severity", "Medium"),
                    "category": report_category,
                    "upload_date": report.get("upload_date", "Unknown"),
                    "distance_m": distance_m,
                    "match_type": match_type,
                })
        
        # Sort by distance (nearest first, location matches at end)
        nearby.sort(key=lambda r: (r["match_type"] != "proximity", r["distance_m"] if r["distance_m"] else 999))
        return nearby

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates in kilometers.
        Uses Haversine formula.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
