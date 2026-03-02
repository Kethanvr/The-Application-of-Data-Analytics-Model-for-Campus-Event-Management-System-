from django.contrib.auth.hashers import check_password


class MongoEngineBackend:
    """Authenticate against the MongoEngine CustomUser document."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        from .models import CustomUser
        try:
            user = CustomUser.objects(username=username).first()
            if user and user.check_password(password) and user.is_active:
                return user
        except Exception:
            return None
        return None

    def get_user(self, user_id):
        from .models import CustomUser
        try:
            return CustomUser.objects(pk=user_id).first()
        except Exception:
            return None
