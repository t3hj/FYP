from datetime import datetime
import os
import json

class VersioningManager:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.versions_file = os.path.join(storage_path, 'versions.json')
        self._initialize_versioning()

    def _initialize_versioning(self):
        if not os.path.exists(self.versions_file):
            with open(self.versions_file, 'w') as f:
                json.dump({}, f)

    def add_version(self, image_id, version_data):
        versions = self._load_versions()
        if image_id not in versions:
            versions[image_id] = []
        versions[image_id].append(version_data)
        self._save_versions(versions)

    def get_versions(self, image_id):
        versions = self._load_versions()
        return versions.get(image_id, [])

    def _load_versions(self):
        with open(self.versions_file, 'r') as f:
            return json.load(f)

    def _save_versions(self, versions):
        with open(self.versions_file, 'w') as f:
            json.dump(versions, f)

    def create_version_data(self, image_id, description):
        return {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'image_id': image_id
        }