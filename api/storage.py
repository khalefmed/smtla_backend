# api/storage.py
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class PublicCloudinaryStorage(RawMediaCloudinaryStorage):
    def _save(self, name, content):
        # Override to add public access
        self.TAG = 'public'
        return super()._save(name, content)