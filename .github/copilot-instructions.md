<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Streamlit Image Upload Application

This is a Streamlit web application for image upload and data storage. When working on this project:

## Key Technologies
- **Streamlit**: Web framework for the user interface
- **Pillow (PIL)**: Image processing and manipulation
- **pandas**: Data handling and analysis
- **sqlite3**: Database operations (built into Python)

## Project Structure
- `app.py`: Main Streamlit application
- `requirements.txt`: Python dependencies
- `uploads/`: Directory for storing uploaded images
- `image_data.db`: SQLite database for image metadata

## Development Guidelines
- Follow Streamlit best practices for UI components
- Use proper error handling for file operations
- Ensure database connections are properly closed
- Validate image formats before processing
- Keep the interface user-friendly and responsive

## Code Style
- Use descriptive function and variable names
- Add docstrings to functions
- Handle exceptions gracefully with user-friendly error messages
- Use Streamlit's built-in components when possible
