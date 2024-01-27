"""
Views for user api
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import status
from rest_framework.views import exception_handler


from user.serializers import (
    UserSerializer,
    AuthTokenSerializer
)

# from user.serializers import CustomRegisterSerializer



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and  response.status_code==400:
        # Convert ErrorDetail objects to simple strings
        for key, errors in response.data.items():
            response.data[key] = [str(error) for error in errors]
    print("****",response.data)
    return response


class CustomRegisterView(RegisterView):
    serializer_class = RegisterSerializer  # You may need to import the correct serializer for your setup

    def create(self, request, *args, **kwargs):

        # try:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # except Exception as e:
        #     print("Error!:", str(e))
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Customize the successful response if needed
        return Response({"detail": "Registration successful", "user_id": user.id}, status=status.HTTP_201_CREATED)




# class CreateUserView(generics.CreateAPIView):
#     """
#     Create a new user in the system
#     """
#     serializer_class = UserSerializer


# class CreateTokenView(ObtainAuthToken):
#     """
#     Create a new auth token for user
#     """
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# class ManageUserView(generics.RetrieveUpdateAPIView):
#     """
#     Manage the authenticated user
#     """
#     serializer_class = UserSerializer
#     authentication_classes = (authentication.TokenAuthentication,)
#     permission_classes = (permissions.IsAuthenticated,)

#     def get_object(self):
#         """
#         Retrieve and return authenticated user
#         """
#         return self.request.user
