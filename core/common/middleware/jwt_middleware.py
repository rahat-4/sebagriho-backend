import logging

logger = logging.getLogger(__name__)


class JWTAuthCookieMiddleware:
    """
    Middleware to extract JWT token from HttpOnly cookies and add it to the Authorization header
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip certain paths to avoid unnecessary processing
        skip_paths = ["/super-admin/", "/static/", "/media/"]

        if not any(request.path.startswith(path) for path in skip_paths):
            # Check if Authorization header is already present
            auth_header = request.META.get("HTTP_AUTHORIZATION")

            if not auth_header or not auth_header.startswith("Bearer "):
                # Get access token from HttpOnly cookie
                access_token = request.COOKIES.get("access_token")

                if access_token:
                    # Add Bearer token to request headers
                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                    logger.debug(
                        f"JWT token added from cookie for path: {request.path}"
                    )
                else:
                    logger.debug(
                        f"No access token found in cookies for path: {request.path}"
                    )
            else:
                logger.debug(
                    f"Authorization header already present for path: {request.path}"
                )

        response = self.get_response(request)
        return response
