from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile

from posts.models import Post, Comment
from django.urls import reverse

User = get_user_model()


class PostNewFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='Gena')
        # Создаем авторизированного пользователя автора поста
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(text='Тестовый текст статьи',
                                       author=cls.user)
    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    #  Проверка вызываемых шаблонов для каждого адреса
    def test_create_newpost(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст новой тестовой записи',
                      'image':PostNewFormTest.uploaded}
    # Отправляем POST-запрос
        response = PostNewFormTest.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))

    def test_create_editpost(self):

        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {'text': 'Измененная тестовая запись'}
        # Отправляем POST-запрос
        response = PostNewFormTest.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'Gena', 'post_id': 1}),
            data=form_data,
            follow=True)

        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, сработал ли редирект на просмотр поста
        self.assertRedirects(response, reverse('post', kwargs={'username': 'Gena', 'post_id': 1}))
        # Проверяем, что создалась запись изменилась
        self.assertTrue(Post.objects.filter(text='Измененная тестовая запись').exists())

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {'text': 'Комментарий статьи'}
        # Отправляем POST-запрос
        response = PostNewFormTest.authorized_client.post(
            reverse('add_comment', kwargs={'username': 'Gena', 'post_id': 1}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('post', kwargs={'username': 'Gena', 'post_id': 1}))