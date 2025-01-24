from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from .constants import LEN_128, LEN_150, LEN_254
from .validators import user_username_validator


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=LEN_254,
        unique=True,
        validators=[user_username_validator]
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=LEN_150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LEN_150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LEN_150
    )
    password = models.CharField(
        'Пароль',
        max_length=LEN_128
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class 
