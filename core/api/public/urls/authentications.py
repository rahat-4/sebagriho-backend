from django.urls import path

from ..views.authentications import UserRegisterView, UserLoginView

urlpatterns = [
    path("/login", UserLoginView.as_view(), name="user-login"),
    # path("/set-password")
    path("/register", UserRegisterView.as_view(), name="user-register"),
]
