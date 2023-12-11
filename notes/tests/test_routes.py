from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(title='Название',
                                       text='Текст',
                                       slug='slug',
                                       author=cls.author)

    def test_main_anonymous(self):
        root = 'notes:home'
        url = reverse(root)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auntificated(self):
        roots = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for root in roots:
                with self.subTest(user=user, root=root):
                    url = reverse(root)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_owner_certain_note(self):
        roots = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for root in roots:
                with self.subTest(user=user, root=root):
                    self.client.force_login(user)
                    url = reverse(root, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        roots = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for root, slug in roots:
            with self.subTest(root=root):
                url = reverse(root, args=slug)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_access_login(self):
        roots = (
            'users:signup',
            'users:login',
            'users:logout'
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            for root in roots:
                with self.subTest(user=user, root=root):
                    url = reverse(root)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
