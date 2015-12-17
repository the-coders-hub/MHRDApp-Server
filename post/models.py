from django.db import models
from django.contrib.auth.models import User
from core.models import Tag, File


CONTENT_VISIBLE = '0'
CONTENT_HIDDEN = '1'
CONTENT_DELETED = '2'
CONTENT_VISIBILITY = [
    [CONTENT_DELETED, 'Deleted'],
    [CONTENT_HIDDEN, 'Hidden'],
    [CONTENT_VISIBLE, 'Visible']
]


class Post(models.Model):

    user = models.ForeignKey(User, related_name='posts')
    title = models.CharField(max_length=256)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    anonymous = models.BooleanField(default=False)
    visibility = models.CharField(max_length=1, choices=CONTENT_VISIBILITY, default=CONTENT_VISIBLE)
    attachments = models.ManyToManyField(File, blank=True)
    upvotes = models.ManyToManyField(User, related_name='post_upvotes')
    downvotes = models.ManyToManyField(User, related_name='post_downvotes')


class Reply(models.Model):
    user = models.ForeignKey(User, related_name='comments')
    content = models.TextField()
    post = models.ForeignKey(Post, related_name='replies')
    created = models.DateTimeField(auto_now_add=True)
    upvotes = models.ManyToManyField(User, related_name='comment_upvotes')
    downvotes = models.ManyToManyField(User, related_name='comment_downvotes')
    visibility = models.CharField(max_length=1, choices=CONTENT_VISIBILITY, default=CONTENT_VISIBLE)

