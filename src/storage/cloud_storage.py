from google.cloud import storage
import os

class CloudStorage:
    def __init__(self, bucket_name):
        """Initialize the CloudStorage with the specified bucket name."""
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_image(self, file_path, destination_blob_name):
        """Upload an image to the cloud storage."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            print(f"Uploaded {file_path} to {destination_blob_name}.")
        except Exception as e:
            print(f"An error occurred while uploading: {e}")

    def download_image(self, source_blob_name, destination_file_path):
        """Download an image from the cloud storage."""
        try:
            blob = self.bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_path)
            print(f"Downloaded {source_blob_name} to {destination_file_path}.")
        except Exception as e:
            print(f"An error occurred while downloading: {e}")

    def list_images(self):
        """List all images in the cloud storage bucket."""
        try:
            blobs = self.bucket.list_blobs()
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"An error occurred while listing images: {e}")
            return []

    def delete_image(self, blob_name):
        """Delete an image from the cloud storage."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            print(f"Deleted {blob_name} from cloud storage.")
        except Exception as e:
            print(f"An error occurred while deleting: {e}")