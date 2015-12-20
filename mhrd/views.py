from django.http import FileResponse, HttpResponse
from django.views.static import serve
from django.conf import settings
import posixpath
from urllib.parse import unquote
from core.models import File
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
import os


def media_file_view(request, path):
    serve_response = serve(request, path, settings.MEDIA_ROOT)
    if not isinstance(serve_response, FileResponse):
        return serve_response
    path = posixpath.normpath(unquote(path))
    path = path.lstrip('/')
    file = get_object_or_404(File, file=path)

    serve_response['Content-type'] = file.mime_type
    return serve_response


def media_file_accel(request, path):
    if settings.DEBUG:
        return media_file_view(request, path)
    path = posixpath.normpath(unquote(path))
    path = path.lstrip('/')
    file = get_object_or_404(File, file=path)
    response = HttpResponse()

    response['X-Accel-Redirect'] = os.path.join(settings.MEDIA_NGINX_REDIRECT, path)
    response['Content-type'] = file.mime_type
    return response


def index(request):
    return render_to_response('index.html', {})

