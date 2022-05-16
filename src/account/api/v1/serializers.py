from typing import Any, Dict
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.formfields import PhoneNumberField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import JSONField, ModelSerializer, Serializer

from account.models import CustomUser

def clean_string_capitalize(value: str) -> str:
    """Clean string and capitalize it."""
    return value.strip().lower().capitalize()

class UserRegisterSerializer(ModelSerializer[CustomUser]):
    phone_number = PhoneNumberField(region='NG')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'gender',
                'date_of_birth']


    def validate_password(self, value: str) -> str:
        """Validate if password passes validations."""
        validate_password(value)
        return value

    def validate_first_name(self, value: str) -> str:
        """Clean first name."""
        return clean_string_capitalize(value)

    def validate_last_name(self, value: str) -> str:
        """Clean last name."""
        return clean_string_capitalize(value)

    def validate_email(self, value: str) -> str:
        """Check if user exists with this email."""
        email = value.strip().lower()
        if CustomUser.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError('This email is already registered, please login instead.')
        return email

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate if password is similar to the attributes of the user."""
        user = CustomUser(**attrs)
        validate_password(attrs.get('password', ''), user)
        return attrs


class UserLoginSerializer(Serializer[Dict[str, Any]]):  # pylint: disable=abstract-method
    email = CharField()
    password = CharField()

    def validate_email(self, value: str) -> CustomUser:
        """Validate if email exists."""
        email = value.strip().lower()
        try:
            user = CustomUser.objects.get(email__iexact=email, is_active=True)
        except CustomUser.DoesNotExist:
            raise ValidationError('Please enter a correct email and password.')
        return user

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate if user authenticates successfully."""
        user = attrs.get('email')
        password = attrs.get('password')
        if not user.check_password(password):  # type: ignore
            raise ValidationError({'email': ['Please enter a correct email and password.']})
        return attrs



class UserChangePasswordSerializer(ModelSerializer[CustomUser]):
    new_password_1 = CharField(min_length=8, max_length=30)
    new_password_2 = CharField(min_length=8, max_length=30)

    class Meta:
        model = CustomUser
        fields = ['password', 'new_password_1', 'new_password_2']
        extra_kwargs = {'password': {'required': True}}

    def validate_new_password_1(self, value: str) -> str:
        """Validate if password passes validations."""
        validate_password(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate if user authenticates successfully and if new password matches."""
        password = attrs.get('password')

        if not self.instance.check_password(password):  # type: ignore
            raise ValidationError({'password': ['Please enter your current password.']})

        new_password_1 = attrs.get('new_password_1')
        new_password_2 = attrs.get('new_password_2')

        if new_password_1 != new_password_2:
            raise ValidationError(
                {'new_password_1': ['Passwords do not match.'], 'new_password_2': ['Passwords do not match.']}
            )
        if new_password_1 == password:
            raise ValidationError(
                {
                    'new_password_1': ['Password is the same as current password.'],
                    'new_password_2': ['Password is the same as current password.'],
                }
            )
        validate_password(new_password_1, user=self.instance)  # type: ignore
        return attrs
