"""
serializers for user api view
"""

from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext_lazy as _

# from dj_rest_auth.registration.serializers import RegisterSerializer
# from allauth.account.adapter import get_adapter
# from allauth.account.utils import setup_user_email
from rest_framework import serializers

# class CustomRegisterSerializer(RegisterSerializer):
#     email = serializers.EmailField(required=True)

#     def custom_signup(self, request, user):
#         # Customize the signup process if needed
#         # pass

#     def get_cleaned_data(self):

#         data = super().get_cleaned_data()
#         data['username'] = data['email']
#         return data

#     def save(self, *args, **kwargs):
#         # adapter = get_adapter()
#         # user = adapter.save_user(request, user, self)
#         # self.custom_signup(request, user)
#         # setup_user_email(request, user, [])
#         user = super().save(*args, **kwargs)
#         self.custom_signup(args[0], user)

#         return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user, setting the password correctly and return it
        """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication token
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user
        """
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
