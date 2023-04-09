from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

users = [
    {
        "email": "vpupkin@yandex.ru",
        "username": "vasya.pupkin",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "password": "Qwerty123"
    },
    {
        "email": "s@yandex.ru",
        "username": "user",
        "first_name": "user1",
        "last_name": "use",
        "password": "Qwerty123"
    }
]


class Command(BaseCommand):
    help = 'Import tags to database.'

    def handle(self, **kwargs):
        for data in users:
            print(data)
            User.objects.get_or_create(
                email=data['email'],
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data['password']
            )
