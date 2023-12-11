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

    def test_list_notes(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        assert self.note in object_list

    def test_list_notes_not_author(self):
        url = reverse('notes:list')
        self.client.force_login(self.user)
        response = self.client.get(url)
        object_list = response.context['object_list']
        assert self.note not in object_list

    def test_form_notes(self):
        roots = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for root, slug in roots:
            with self.subTest(root=root):
                url = reverse(root, args=slug)
                response = self.client.get(url)
                assert 'form' in response.context


