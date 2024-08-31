from django.core.exceptions import ValidationError
import os
import uuid
from django.conf import settings


def get_unique_file_path(filename, directory):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    filepath = os.path.join(settings.MEDIA_ROOT, directory, filename)
    while os.path.exists(filepath):
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(settings.MEDIA_ROOT, directory, filename)
    return os.path.join(directory, filename)


def get_image_path(instance, filename):
    return get_unique_file_path(filename, "images")


def get_file_path(instance, filename):
    return get_unique_file_path(filename, "attatchments")


def size_validate(file, megabyte_limit):
    filesize = file.size
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def attatchment_validate(file):
    size_validate(file, 50.0)


def image_validate(file):
    size_validate(file, 10.0)
    # ext = file.name.split('.')[-1].lower()
    # if ext not in ['jpg', 'png', 'jpeg', 'webp']:
    #     raise ValidationError('Invalid file format.')
