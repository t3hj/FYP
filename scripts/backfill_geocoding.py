"""
Backfill geocoding for existing reports.
Converts location text (road names, landmarks) to latitude/longitude 
for reports that have location but missing coordinates.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.supabase_client import get_supabase_client
from src.utils.geocoding import geocode_location
from config.settings import SUPABASE_TABLE


def backfill_geocoding():
    """Fetch all reports, geocode those with location but missing coordinates."""
    client = get_supabase_client()
    table_name = SUPABASE_TABLE

    print(f"Loading all reports from {table_name}...")
    
    try:
        result = client.table(table_name).select("*").execute()
        reports = result.data or []
    except Exception as e:
        print(f"❌ Failed to fetch reports: {e}")
        return

    print(f"Found {len(reports)} reports.\n")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i, report in enumerate(reports, 1):
        report_id = report.get("id")
        location = report.get("location")
        latitude = report.get("latitude")
        longitude = report.get("longitude")

        # Skip if already has valid coordinates
        if latitude is not None and longitude is not None:
            print(f"[{i}/{len(reports)}] ID {report_id}: Already has coordinates ✓")
            skipped_count += 1
            continue

        # Skip if no location text
        if not location or not str(location).strip():
            print(f"[{i}/{len(reports)}] ID {report_id}: No location text, skipping")
            skipped_count += 1
            continue

        # Try to geocode
        print(f"[{i}/{len(reports)}] ID {report_id}: Geocoding '{location}'...", end=" ")
        try:
            lat, lon = geocode_location(location)

            if lat is not None and lon is not None:
                # Update the report with new coordinates
                update_result = (
                    client.table(table_name)
                    .update({"latitude": lat, "longitude": lon})
                    .eq("id", report_id)
                    .execute()
                )
                print(f"✓ ({lat:.4f}, {lon:.4f})")
                updated_count += 1
            else:
                print("✗ Could not geocode")
                skipped_count += 1

        except Exception as e:
            print(f"✗ Error: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Backfill complete!")
    print(f"  Updated: {updated_count} reports")
    print(f"  Skipped: {skipped_count} reports (already have coords or no location)")
    print(f"  Errors:  {error_count} reports")
    print(f"{'='*60}\n")

    if updated_count > 0:
        print("✅ Existing reports with road names can now appear on the map!")


if __name__ == "__main__":
    backfill_geocoding()
