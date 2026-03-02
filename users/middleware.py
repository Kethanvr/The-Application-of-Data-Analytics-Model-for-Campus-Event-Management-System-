class _AnonymousUser:
    is_authenticated = False
    is_anonymous = True
    is_active = False
    role = None
    pk = None

    def __str__(self):
        return 'AnonymousUser'


AnonymousUser = _AnonymousUser


class MongoAuthMiddleware:
    """Replace Django's default auth middleware for MongoEngine users."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('_auth_user_id')
        backend_path = request.session.get('_auth_user_backend')
        if user_id and backend_path:
            from users.backends import MongoEngineBackend
            backend = MongoEngineBackend()
            user = backend.get_user(user_id)
            request.user = user if user else AnonymousUser()
        else:
            request.user = AnonymousUser()
        return self.get_response(request)


class LocalhostOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


class FileIntegrityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
