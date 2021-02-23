from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post
from django.urls import reverse

User = get_user_model()


class PostNewFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='Gena')
        # Создаем авторизированного пользователя автора поста
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(text='Тестовый текст статьи',
                                       author=cls.user)

    #  Проверка вызываемых шаблонов для каждого адреса
    def test_create_newpost(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст новой тестовой записи'}
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
