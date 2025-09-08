from datetime import datetime, timedelta
from django.conf import settings


def set_auth_cookies(response, access_token, refresh_token, remember_me=False):
    """
    Sets JWT cookies (access + refresh) and optional remember_me flag.
    """
    # Calculate expiry times as datetime objects
    access_expires = datetime.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

    if remember_me:
        refresh_expires = datetime.now() + timedelta(days=7)
        response.set_cookie(
            key="remember_me",
            value="true",
            expires=refresh_expires,
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=False,
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
    else:
        refresh_expires = datetime.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

    # Set access token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        expires=access_expires,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=refresh_expires,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    return response
