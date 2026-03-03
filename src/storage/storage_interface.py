from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def upload_image(self, image_file, metadata):
        """Upload an image to the storage system."""
        pass

    @abstractmethod
    def retrieve_image(self, image_id):
        """Retrieve an image from the storage system using its ID."""
        pass

    @abstractmethod
    def delete_image(self, image_id):
        """Delete an image from the storage system using its ID."""
        pass

    @abstractmethod
    def list_images(self):
        """List all images stored in the storage system."""
        pass

    @abstractmethod
    def backup_storage(self):
        """Create a backup of the storage system."""
        pass

    @abstractmethod
    def restore_storage(self, backup_id):
        """Restore the storage system from a backup."""
        pass