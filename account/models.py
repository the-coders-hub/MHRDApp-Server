import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from core.models import File

from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save


class EmailDomain(models.Model):
    domain = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)
    _history_ = HistoricalRecords()

    @classmethod
    def verify_domain(cls, email):
        id_, _, domain = email.partition('@')
        if _ is not '@':
            return False
        return cls.objects.filter(domain=domain).exists()

    def __str__(self):
        return self.domain


class Designation(models.Model):
    name = models.CharField(max_length=64)
    verified = models.BooleanField(default=False)
    _history_ = HistoricalRecords()

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    college = models.ForeignKey('college.College', null=True, blank=True)
    picture = models.ForeignKey(File, related_name='+', null=True, blank=True)
    designations = models.ManyToManyField(Designation, blank=True)
    _history_ = HistoricalRecords()

    def __str__(self):
        return self.user.username


def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)


def signup_code_generation():
    return get_random_string(length=8)


class SignUpCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=8, default=signup_code_generation)
    active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    _history_ = HistoricalRecords()

    def __str__(self):
        return '%s: %s' % (self.email, self.code)


class UserToken(models.Model):
    user = models.ForeignKey(User)
    token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(default=timezone.now)
    has_expired = models.BooleanField(default=False)

    def is_active(self):
        if self.has_expired:
            return False
        curr_date = timezone.now()
        diff = abs((curr_date - self.last_accessed).days)
        # 1 month expiration date
        if diff > 30:
            self.has_expired = True
            self.save()
            return False
        else:
            self.last_accessed = curr_date
            self.save()
            return True
