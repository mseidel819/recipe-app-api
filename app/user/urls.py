"""
url mappings for user api
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from dj_rest_auth.jwt_auth import get_refresh_view
# from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from user.views import CustomRegisterView, change_password


app_name = "user"

urlpatterns = [
    # path('create/', views.CreateUserView.as_view(), name="create"),
    # path('token/', views.CreateTokenView.as_view(), name="token"),
    # path('me/', views.ManageUserView.as_view(), name="me"),
    path("register/", CustomRegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    path('change_password/', change_password, name='change_password'),
]
