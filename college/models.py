from django.db import models
from core.models import File, Tag
from account.models import EmailDomain
from simple_history.models import HistoricalRecords


class College(models.Model):
    name = models.CharField(max_length=108)
    logo = models.ForeignKey(File, related_name='+', null=True, blank=True)
    cover = models.ForeignKey(File, related_name='+', null=True, blank=True)
    location = models.TextField()
    phone = models.CharField(max_length=32, null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    email_domains = models.ManyToManyField(EmailDomain, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    _history_ = HistoricalRecords()

    def __str__(self):
        return self.name

