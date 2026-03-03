import pytest
from src.storage.cloud_storage import CloudStorage

@pytest.fixture
def cloud_storage():
    return CloudStorage()

def test_upload_image(cloud_storage):
    # Assuming the CloudStorage class has an upload_image method
    result = cloud_storage.upload_image("path/to/test/image.jpg")
    assert result is True  # Adjust based on actual expected result

def test_download_image(cloud_storage):
    # Assuming the CloudStorage class has a download_image method
    cloud_storage.upload_image("path/to/test/image.jpg")
    result = cloud_storage.download_image("image.jpg")
    assert result is not None  # Adjust based on actual expected result

def test_delete_image(cloud_storage):
    cloud_storage.upload_image("path/to/test/image.jpg")
    result = cloud_storage.delete_image("image.jpg")
    assert result is True  # Adjust based on actual expected result

def test_list_images(cloud_storage):
    cloud_storage.upload_image("path/to/test/image1.jpg")
    cloud_storage.upload_image("path/to/test/image2.jpg")
    images = cloud_storage.list_images()
    assert "image1.jpg" in images
    assert "image2.jpg" in images

def test_image_versioning(cloud_storage):
    cloud_storage.upload_image("path/to/test/image.jpg")
    cloud_storage.upload_image("path/to/test/image_v2.jpg")
    versions = cloud_storage.get_image_versions("image.jpg")
    assert len(versions) == 2  # Adjust based on actual expected result