from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    password = models.CharField(
        verbose_name='Password',
        max_length=150,
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
