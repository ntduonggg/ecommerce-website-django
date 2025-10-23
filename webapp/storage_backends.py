from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    """Storage for static files (CSS, JS, images from your code)"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False
    
class MediaStorage(S3Boto3Storage):
    """Storage for media files (user uploads, product images, etc.)"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False