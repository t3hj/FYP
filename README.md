# Image Upload & Data Storage Application

A Streamlit web application for uploading images and storing their metadata in a SQLite database.

## Features

- **Image Upload**: Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP)
- **Data Storage**: SQLite database for storing image metadata
- **Data Visualization**: View uploaded images data with summary statistics
- **File Management**: Automatic organization of uploaded files
- **User Interface**: Clean and intuitive web interface built with Streamlit

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this project
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided local URL (typically `http://localhost:8501`)

3. Use the application:
   - **Upload Images**: Go to the "Upload Images" tab to select and upload image files
   - **View Data**: Go to the "View Data" tab to see all uploaded images and statistics

## Project Structure

```
FYP/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .github/
│   └── copilot-instructions.md
├── uploads/              # Directory for uploaded images (created automatically)
└── image_data.db         # SQLite database (created automatically)
```

## Database Schema

The application uses a SQLite database with the following table structure:

```sql
CREATE TABLE uploaded_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    upload_date DATETIME NOT NULL,
    file_size INTEGER,
    image_format TEXT,
    description TEXT
);
```

## Future Enhancements

- Image resizing and optimization
- Advanced image filtering and search
- Export functionality for data
- User authentication
- Cloud storage integration
- AI-powered image analysis features

## Development

This project is set up for easy development and extension. The modular structure allows for easy addition of new features and components.

## License

This project is for educational purposes as part of a Final Year Project (FYP).
