import os 
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin

class CKEditor5CustomStorage(FileSystemStorage):
    """Custom storage for django_ckeditor_5 images, using a specific sub-folder."""
    # Files will be saved in MEDIA_ROOT/ckeditor_uploads/
    location = os.path.join(settings.MEDIA_ROOT, "ckeditor_uploads") 
    base_url = urljoin(settings.MEDIA_URL, "ckeditor_uploads/")