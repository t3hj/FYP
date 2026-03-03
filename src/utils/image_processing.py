def resize_image(image, target_size):
    """
    Resize the given image to the target size.

    Parameters:
    image (PIL.Image): The image to resize.
    target_size (tuple): The desired size as (width, height).

    Returns:
    PIL.Image: The resized image.
    """
    return image.resize(target_size, Image.ANTIALIAS)

def convert_image_format(image, format):
    """
    Convert the given image to the specified format.

    Parameters:
    image (PIL.Image): The image to convert.
    format (str): The target format (e.g., 'JPEG', 'PNG').

    Returns:
    PIL.Image: The converted image.
    """
    output = io.BytesIO()
    image.save(output, format=format)
    output.seek(0)
    return output

def process_image(file):
    """
    Process the uploaded image file.

    Parameters:
    file (UploadedFile): The uploaded image file.

    Returns:
    PIL.Image: The processed image.
    """
    image = Image.open(file)
    # Example processing: Resize to 800x800
    image = resize_image(image, (800, 800))
    return image