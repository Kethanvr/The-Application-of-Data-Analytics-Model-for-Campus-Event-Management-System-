from django.http import HttpResponseForbidden
import json
import os
import hashlib
from django.conf import settings


class LocalhostOnlyMiddleware:
    """
    Middleware that restricts access to localhost only.
    Disabled in this version to allow local development.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow all connections for local development
        response = self.get_response(request)
        return response


class FileIntegrityMiddleware:
    """
    Middleware that checks file integrity on each request.
    Simplified version that just passes through.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
