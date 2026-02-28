#!/usr/bin/env python
import os
import sys

from django.core.files.storage import default_storage
from minio_storage.storage import MinioMediaStorage

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_clip.settings")
    try:
        default_storage._wrapped = MinioMediaStorage()
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)
