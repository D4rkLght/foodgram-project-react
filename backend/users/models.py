from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Administrator'),
        (USER, 'User'),
    )
    password = models.CharField(
        verbose_name='Password',
        max_length=150,
    )

    role = models.CharField(
        verbose_name='Role',
        max_length=254,
        choices=ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
