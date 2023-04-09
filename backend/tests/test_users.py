from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTestCase(APITestCase):

    def setUp(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')
        self.data = {
            'email': 'user@ya.ru',
            'username': 'user',
            'first_name': 'user',
            'last_name': 'user',
            'password': '123user23sdf13'
        }

    def test_regisration_new_user(self):
        '''Test registration.'''

        response = self.client.post('/api/users/', self.data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_token_create(self):
        '''Test token create.'''

        self.client.post('/api/users/', self.data)
        response = self.client.post('/api/auth/token/login/', self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UsersTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_first = User.objects.create_user(
            email='user@ya.ru',
            username='user',
            first_name='user',
            last_name='user',
            password='123user23sdf13'
        )
        cls.user_second = User.objects.create_user(
            email='usersec@ya.ru',
            username='usersec',
            first_name='usersec',
            last_name='usersec',
            password='123user23sdf13'
        )
        cls.user_first.save()
        cls.user_second.save()
        cls.token = Token.objects.create(user=cls.user_first)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='token ' + self.token.key)
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')

    def test_page_me(self):
        '''Test page me.'''

        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_subscribe(self):
        '''Test subscribe user to author.'''

        self.client.post('/api/users/4/subscribe/')
        count = self.client.get('/api/users/subscriptions/').data
        self.assertEqual(len(count), 1)

    def test_cant_subscribe(self):
        '''Test can't subscribe author to author.'''

        response = self.client.post('/api/users/3/subscribe/')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
