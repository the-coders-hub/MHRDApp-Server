import os
import uuid

import magic
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords


def file_upload(instance, filename):
    filename = uuid.uuid1().hex + uuid.uuid4().hex
    return 'files/' + filename


class FileManger(models.Manager):

    class FileQueryset(models.query.QuerySet):

        def delete(self):
            for file in self:
                file.delete()

    def get_queryset(self):
        return self.FileQueryset(self.model, using=self._db)


class File(models.Model):
    file = models.FileField(upload_to=file_upload)
    mime_type = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    _history_ = HistoricalRecords()

    @classmethod
    def get_mime_type(cls, value):
        return magic.from_buffer(value.read(1024), mime=True)

    def delete(self, using=None, keep_parents=False):
        name = self.file.name
        uuid_hex = name.split('/')[1]
        new_name = 'deleted/%s' % uuid_hex
        initial_path = self.file.path
        new_path = settings.MEDIA_ROOT + new_name
        if not os.path.exists(settings.MEDIA_ROOT + 'deleted/'):
            os.mkdir(settings.MEDIA_ROOT + 'deleted/', mode=0o755)
        os.rename(initial_path, new_path)
        self.file.name = new_name
        self.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.mime_type:
            self.mime_type = self.get_mime_type(self.file)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __str__(self):
        return self.file.name

    objects = FileManger()


class Tag(models.Model):
    tag = models.CharField(max_length=16)
    subscribers = models.ManyToManyField(User, blank=True)
