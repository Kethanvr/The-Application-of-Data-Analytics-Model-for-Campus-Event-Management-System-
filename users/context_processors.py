def mongo_user(request):
    """Inject the MongoEngine user as 'user' into every template context."""
    return {'user': request.user}
