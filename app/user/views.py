"""
Views for user api
"""

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import status
from rest_framework.views import exception_handler

from django.contrib.auth import update_session_auth_hash
from user.serializers import ChangePasswordSerializer


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code == 400:
        # Convert ErrorDetail objects to simple strings
        for key, errors in response.data.items():
            response.data[key] = [str(error) for error in errors]
    return response


class CustomRegisterView(RegisterView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):

        # try:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        return Response(
            {"detail": "Registration successful", "user_id": user.id},
            status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)
                return Response(
                    {'message': 'Password changed successfully.'},
                    status=status.HTTP_200_OK)
            return Response(
                {'error': 'Incorrect old password.'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
