class JWTAuthCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude Django admin and static/media files if needed
        if request.path.startswith("/super-admin/"):
            return self.get_response(request)

        # Optionally skip static/media to reduce overhead
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return self.get_response(request)

        # Add JWT Authorization header from HttpOnly cookie
        access_token = request.COOKIES.get("access_token")
        if access_token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        return self.get_response(request)
