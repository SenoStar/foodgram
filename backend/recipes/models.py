from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (
    LEN_32,
    LEN_128,
    LEN_150,
    LEN_254
)
from .validators import user_username_validator


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=LEN_254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=LEN_150,
        unique=True,
        validators=[user_username_validator]
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


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=LEN_32,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LEN_32,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name
