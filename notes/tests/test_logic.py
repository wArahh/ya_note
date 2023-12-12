from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

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
        cls.add_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_create_new_note_and_cannot_duplicate_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.add_data)
        self.client.post(url, data=self.add_data)
        self.assertEqual(Note.objects.count(), 2)
        self.assertRedirects(response, reverse('notes:success'))

    def test_anonymous_create_new_note(self):
        url = reverse('notes:add')
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = self.client.post(url, data=self.add_data)
        self.assertEqual(Note.objects.count(), 1)
        self.assertRedirects(response, redirect_url)

    def test_not_slug_add_data(self):
        self.note.delete()
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.add_data.pop('slug')
        response = self.client.post(url, data=self.add_data)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.add_data['title'])
        assert new_note.slug == expected_slug

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        assert Note.objects.count() == 1
