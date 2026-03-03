def validate_image_file(file):
    """
    Validates the uploaded image file.

    Args:
        file: The uploaded file object.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not file:
        return False

    file_extension = file.name.split('.')[-1].lower()
    return f".{file_extension}" in valid_extensions


def validate_image_size(file, max_size_mb=5):
    """
    Validates the size of the uploaded image file.

    Args:
        file: The uploaded file object.
        max_size_mb: The maximum allowed size in megabytes.

    Returns:
        bool: True if the file size is within the limit, False otherwise.
    """
    if not file:
        return False

    file.seek(0, 2)  # Move the cursor to the end of the file
    file_size_mb = file.tell() / (1024 * 1024)  # Convert bytes to megabytes
    file.seek(0)  # Reset cursor to the beginning of the file
    return file_size_mb <= max_size_mb


def validate_image_format(file):
    """
    Validates the format of the uploaded image file.

    Args:
        file: The uploaded file object.

    Returns:
        bool: True if the file format is valid, False otherwise.
    """
    from PIL import Image

    try:
        img = Image.open(file)
        img.verify()  # Verify that it is an image
        return True
    except (IOError, SyntaxError):
        return False