from datetime import datetime, timezone
import json
from pathlib import Path

from config.settings import BACKUP_DIRECTORY, SUPABASE_TABLE
from src.database.supabase_client import get_supabase_client


class BackupService:
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = SUPABASE_TABLE
        self.backup_dir = Path(BACKUP_DIRECTORY)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def run_backup(self):
        try:
            result = self.client.table(self.table_name).select("*").execute()
            rows = result.data or []

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"supabase_backup_{timestamp}.json"
            backup_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

            return {
                "success": True,
                "message": f"Exported {len(rows)} records.",
                "backup_file": str(backup_path),
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def list_backups(self):
        return sorted(
            [f.name for f in self.backup_dir.glob("supabase_backup_*.json")],
            reverse=True,
        )
