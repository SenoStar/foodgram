import re
from django.core.exceptions import ValidationError
from .constants import pattern_username


def user_username_validator(username):
    if re.match(pattern_username, username) is None:
        return ValidationError(
            {
                'В username имеется запрещенный символ! '
                'Можно использовать буквы и цифры '
            }
        )