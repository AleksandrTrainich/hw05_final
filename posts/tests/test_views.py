from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile

from posts.models import Post, Group, Follow

User = get_user_model()

settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        # Создаем авторизированного пользователя НЕ автора поста
        cls.user_1 = User.objects.create_user(username='NotGena')
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.user_1)
        cls.group = Group.objects.create(title='Название группы',
                                         slug='test-group',
                                         description='Описание группы')

        cls.post = Post.objects.create(text='Тестовый текст статьи',
                                       author=cls.user,
                                       image=cls.uploaded)

        cls.temp_url_names = {'index.html': reverse('index'),
                              'group.html': reverse('group_posts', kwargs={'slug': 'test-group'}),
                              'profile.html': reverse('profile', kwargs={'username': 'Gena'}),
                              'post.html': reverse('post', kwargs={'username': 'Gena', 'post_id': 1}),
                              'posts/new_post.html': reverse('post_edit', kwargs={'username': 'Gena', 'post_id': 1}),
                              'follow.html': reverse('follow_index')}

    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        for template, url in PostViewsTests.temp_url_names.items():
            with self.subTest(url=url):
                response = PostViewsTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    #  два одинаковыx ключа не сработают =0
    # поэтому для 'posts/new_post.html': reverse('new_post') еще разок
    def test_urls_uses_correct_template_new(self):
        response = PostViewsTests.authorized_client.get(reverse('new_post'))
        self.assertTemplateUsed(response, 'posts/new_post.html')

    # Проверяем словарь context главной страницы
    def test_home_page_show_correct_context(self):
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        Post.objects.create(text='Тестовый текст статьи c группой',
                            author=PostViewsTests.user,
                            group=PostViewsTests.group)
        response = PostViewsTests.authorized_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_image_1 = response.context.get('page')[1].image
        post_text_1 = response.context.get('page')[1].text
        self.assertEqual(post_text_0, 'Тестовый текст статьи c группой')
        self.assertEqual(post_image_1.name, 'posts/small.gif')
        self.assertEqual(post_text_1, 'Тестовый текст статьи')

    # Проверка работы кэша главной страницы
    def test_home_page_cache(self):

        response = PostViewsTests.authorized_client.get(reverse('index'))
        response_content = response.content
        Post.objects.create(text='Эта статья появится через 20 с',
                            author=PostViewsTests.user_1)
        response_new = PostViewsTests.authorized_client.get(reverse('index'))
        self.assertEqual(response_content, response_new.content, 'Кэш не работает')

    # Проверяем, что словарь context страницы группы
    # содержит ожидаемые значения
    def test_group_detail_pages_show_correct_context(self):
        image_group = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        group_uploaded = SimpleUploadedFile(
            name='image_group.gif',
            content=image_group,
            content_type='image/gif'
        )

        Post.objects.create(text='Тестовый текст статьи c группой',
                            author=PostViewsTests.user, group=PostViewsTests.group, image=group_uploaded)

        response = PostViewsTests.authorized_client.get(reverse('group_posts',
                                                                kwargs={'slug': f'{PostViewsTests.group.slug}'}))
        group_context = response.context.get('group')
        self.assertEqual(group_context.title, 'Название группы')
        self.assertEqual(group_context.description, 'Описание группы')
        self.assertEqual(group_context.slug, 'test-group')

        post_group_text_0 = response.context.get('page')[0].text
        post_group_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_group_text_0, 'Тестовый текст статьи c группой', 'Пост не появился в группе')
        self.assertEqual(post_group_image_0.name, 'posts/image_group.gif')

    # Проверяем словарь context профиля пользователя
    def test_profile_page_show_correct_context(self):
        response = PostViewsTests.authorized_client.get(
            (reverse('profile', kwargs={'username': 'Gena'})))
        prolile_text_0 = response.context.get('page')[0].text
        prolile_image_0 = response.context.get('page')[0].image
        self.assertEqual(prolile_text_0, 'Тестовый текст статьи')
        self.assertEqual(prolile_image_0.name, 'posts/small.gif')

    # Проверяем словарь context поста пользователя
    def test_post_profile_page_show_correct_context(self):
        response = PostViewsTests.authorized_client.get(reverse(
            'post', kwargs={'username': 'Gena', 'post_id': 1}))
        prolile_post_text = response.context.get('posts').text
        prolile_post_image = response.context.get('posts').image
        self.assertEqual(prolile_post_text, 'Тестовый текст статьи')
        self.assertEqual(prolile_post_image.name, 'posts/small.gif')

    # Проверяем словарь context редактирования поста пользователя
    # тест создания нового поста
    def test_new_page_show_correct_form(self):
        response = PostViewsTests.authorized_client.get(reverse('new_post'))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {'group': forms.models.ModelChoiceField, 'text': forms.fields.CharField}
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # тест создания редактирования поста
    def test_initial_value(self):
        # проверим, что поле text отличантся от начального значения(не пустное)
        response = PostViewsTests.authorized_client.get(reverse('post_edit',
                                                                kwargs={'username': 'Gena', 'post_id': 1}))
        form = response.context.get('form')
        form_edit = form.has_changed()
        self.assertEqual(form_edit, True)

    # тест подписок пользователя
    def test_follow_auth_client(self):
        # оформим подписку на пользователя 'Gena'
        # отправляем POST-запрос
        PostViewsTests.authorized_client_1.post(reverse('profile_follow',
                                                        kwargs={'username': 'Gena'}))
        following_count = Follow.objects.filter(user=PostViewsTests.user_1).count()
        self.assertEqual(following_count, 1, 'Подписка не оформяется')

        # повторная подписка не пройдет!
        PostViewsTests.authorized_client_1.post(reverse('profile_follow',
                                                        kwargs={'username': 'Gena'}))
        following_count = Follow.objects.filter(user=PostViewsTests.user_1).count()
        self.assertEqual(following_count, 1, 'Два раза нельзя подписыватся на одного автора')

        # удалим подписку
        PostViewsTests.authorized_client_1.post(reverse('profile_unfollow',
                                                        kwargs={'username': 'Gena'}))
        following_count = Follow.objects.filter(user=PostViewsTests.user_1).count()
        self.assertEqual(following_count, 0, 'Подписка не удаляется!')

        # оформим подписку на самого себя
        PostViewsTests.authorized_client.post(reverse('profile_follow',
                                                      kwargs={'username': 'Gena'}))
        following_count = Follow.objects.filter(user=PostViewsTests.user).count()
        self.assertEqual(following_count, 0, 'Проверить что нельзя на самого себя подписаться')

    # тест ленты пользователя
    def test_follow_tape_auth_client(self):
        # оформим подписку на пользователя 'Gena'

        PostViewsTests.authorized_client_1.post(reverse('profile_follow',
                                                        kwargs={'username': 'Gena'}))
        # сделаем запрос на страницу с подписками
        response = PostViewsTests.authorized_client_1.get(reverse('follow_index'))
        post_text_0 = response.context.get('page')[0].text
        post_image_0 = response.context.get('page')[0].image
        # проверим текст статьи
        self.assertEqual(post_text_0, 'Тестовый текст статьи')
        # проверим что картинка тоже есть
        self.assertEqual(post_image_0.name, 'posts/small.gif', 'Проверить что в ленту передаются картинки')
        # отпишемся
        PostViewsTests.authorized_client_1.post(reverse('profile_unfollow',
                                                        kwargs={'username': 'Gena'}))
        response = PostViewsTests.authorized_client_1.get(reverse('follow_index'))
        post_text_0 = response.context.get('page').object_list
        # количество постов в ленте равно 0.
        self.assertEqual(len(post_text_0), 0, 'Проверить что в лента с подписками работает')


class PaginatorViewsTest(TestCase):
    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        posts = [Post(text='Тестовый текст статьи' + str(i), author=self.user) for i in range(13)]
        Post.objects.bulk_create(posts)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
