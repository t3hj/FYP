# Streamlit Image Upload Application

This project is a Streamlit web application designed for image upload and data management, featuring a central hosted database and cloud storage for images. The application ensures data integrity through backups and versioning.

## Key Features
- **Image Upload**: Users can upload images through a user-friendly interface.
- **Image Gallery**: View uploaded images in a gallery format.
- **Version History**: Track changes and versions of uploaded images.
- **Backup and Restore**: Manage backups of the database and image storage to prevent data loss.

## Project Structure
- `app.py`: Main entry point for the Streamlit application.
- `requirements.txt`: Lists Python dependencies required for the project.
- `README.md`: Documentation for the project.
- `.env.example`: Template for environment variables.
- `.gitignore`: Specifies files to be ignored by Git.
- `config/`: Contains configuration settings and logging setup.
- `src/`: Contains the core application logic, including database, storage, backup, services, and utilities.
- `pages/`: Contains Streamlit pages for different functionalities.
- `tests/`: Contains unit tests for various components of the application.
- `scripts/`: Contains scripts for backup, migration, and cloud resource setup.
- `docker/`: Contains Docker configuration files for containerization.

## Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/t3hj/FYP.git
   cd FYP
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables by copying `.env.example` to `.env` and filling in the necessary values.

5. Run the application:
   ```
   streamlit run app.py
   ```

## Supabase Requirements
Create a `reports` table that supports uploaded image metadata. At minimum, ensure these columns exist:
- `id` (primary key)
- `filename` (text)
- `cloud_storage_url` (text)
- `upload_date` (timestamp/text)
- `version` (integer)

To support map view and AI-enriched fields, also add:
- `category` (text)
- `additional_details` (text)
- `location` (text)
- `latitude` (double precision)
- `longitude` (double precision)

## Ollama (Optional)
The app can run optional local Ollama vision analysis during upload.
- Set `ENABLE_OLLAMA = "true"` in Streamlit secrets to enable.
- Configure `OLLAMA_URL` and `OLLAMA_MODEL`.
- If Ollama is unavailable, uploads still succeed and the app falls back to EXIF/manual data.

## Usage
- Navigate to the upload page to upload images.
- View the gallery to see all uploaded images.
- Check the version history to track changes.
- Use the backup and restore page to manage data backups.

## Backup and Versioning
The application includes a robust backup system that regularly saves the database and image storage to prevent data loss. Versioning allows users to revert to previous versions of images if needed.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.