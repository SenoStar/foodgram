from rest_framework import serializers


def validate_password_length(value):
    """Валидатор для проверки длины пароля."""
    if len(value) > 128:
        raise serializers.ValidationError(
            'Пароль не может превышать 128 символов.'
        )
    return value
