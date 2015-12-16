from simple_history.admin import SimpleHistoryAdmin
from django.contrib.admin import register
from .models import EmailDomain, UserToken, SignUpCode


@register(EmailDomain)
class EmailDomainAdmin(SimpleHistoryAdmin):
    list_display = ['domain', 'timestamp']


@register(SignUpCode)
class SignUpCodeAdmin(SimpleHistoryAdmin):
    list_display = ['email', 'code', 'active', 'verified', 'timestamp']


@register(UserToken)
class UserTokenAdmin(SimpleHistoryAdmin):
    list_display = ['user', 'token', 'created', 'last_accessed', 'has_expired']

