"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {'password': {'write_only': True, 'min_length':5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        User = get_user_model()
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        # 1. Remove password from data 'bag' so super().update() doesn't save it as plain text.
        # If no password is provided in the request, 'None' is returned.
        password=validated_data.pop('password', None)

        # 2. Use the default update logic to handle 'safe' fields like 'name' and 'email'.
        # Because we 'popped' the password, this line only sees and updates non-sensitive fields.
        user = super().update(instance, validated_data)

        # 3. If a new password was provided, encrypt (hash) it before saving to the database
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSeriallizer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email=attrs.get('email')
        password=attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg= _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user']=user
        return attrs