# Local Lens

Local Lens is a Streamlit app for reporting community issues from photos. Residents upload an image, AI extracts issue details, location data is captured or inferred, and reports are stored in Supabase for council review.

## What Local Lens Does
- AI-assisted issue reporting from uploaded photos
- Structured report form pre-filled with title, category, severity, details, and recommended action
- Geolocation support from EXIF GPS data and optional geocoding fallback
- Report listing with search and filters
- Map view for geo-tagged reports
- Council-only insights dashboard (password protected)
- One-click metadata backups to local JSON files
- Duplicate protection for identical photos and short-term repeat submissions

## App Tabs
- Report an Issue: Upload photo, review AI output, and submit a structured report
- View Reports: Search, filter, and browse all submitted reports
- Map: Visualize report locations with valid coordinates
- Council Insights: Category, severity, and time-based charts for council staff
- Backup: Trigger and view local backup exports

## Tech Stack
- Streamlit
- Supabase (database + storage)
- Ollama (optional vision analysis)
- Pandas, Pillow, Requests, Geopy

## Project Layout
- app.py: Main Streamlit entry point
- config/: Secrets and runtime settings
- src/services/: Upload, AI, and backup services
- src/database/: Supabase client and schema migration files
- src/ui/: Theme, reusable components, and tab renderers
- src/utils/: Validation, image metadata, geolocation, and geocoding helpers
- tests/: Test suites for storage and service modules
- docker/: Dockerfile and compose setup

## Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/t3hj/FYP.git
   cd FYP
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add Streamlit secrets in .streamlit/secrets.toml:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-service-or-anon-key"
   SUPABASE_BUCKET = "report-images"
   SUPABASE_TABLE = "reports"

   ENABLE_OLLAMA = "false"
   OLLAMA_URL = "http://localhost:11434"
   OLLAMA_MODEL = "llava"

   REQUIRE_AI = "false"
   REQUIRE_GEOLOCATION = "false"
   ENABLE_GEOCODING = "true"

   COUNCIL_ADMIN_PASSWORD = "change-me"
   ```

5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Required Supabase Schema
Use a reports table with fields expected by the upload flow.

Core fields:
- id (primary key)
- filename (text)
- cloud_storage_url (text)
- upload_date (timestamp/text)
- version (integer)

AI and report metadata:
- title (text)
- category (text)
- severity (text)
- additional_details (text)
- recommended_action (text)
- location (text)
- latitude (double precision)
- longitude (double precision)

Anti-duplicate support:
- reporter_id (text)
- image_hash (text)

Note: the service includes compatibility fallbacks for legacy columns such as image_path and created_at.

## Configuration Modes
- Optional AI mode:
  - ENABLE_OLLAMA = "true" enables Ollama-based analysis
  - If disabled, users can still submit reports manually

- Strict AI mode:
  - REQUIRE_AI = "true" blocks submission if AI analysis fails

- Strict geolocation mode:
  - REQUIRE_GEOLOCATION = "true" blocks submission without coordinates
  - ENABLE_GEOCODING = "true" allows geocoding from location text when GPS is missing

## Docker
Docker assets are available in docker/:
- docker/Dockerfile
- docker/docker-compose.yml

Build and run with your preferred Docker workflow.

## Testing
Run tests with:
```bash
pytest
```

## Contributing
Contributions are welcome. Open an issue or submit a pull request with a clear description of the change.

## License
This project is licensed under the MIT License.