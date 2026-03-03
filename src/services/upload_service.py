from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config.settings import SUPABASE_BUCKET, SUPABASE_TABLE
from src.database.supabase_client import get_supabase_client
from src.utils.validators import validate_image_format


class UploadService:
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = SUPABASE_TABLE
        self.bucket_name = SUPABASE_BUCKET

    def upload_image(self, uploaded_file):
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
            }

            insert_result = self.client.table(self.table_name).insert(payload).execute()

            return {
                "success": True,
                "message": "Image uploaded successfully.",
                "data": insert_result.data[0] if insert_result.data else payload,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def list_uploaded_images(self):
        try:
            result = (
                self.client.table(self.table_name)
                .select("*")
                .order("upload_date", desc=True)
                .execute()
            )
            return result.data or []
        except Exception:
            return []
