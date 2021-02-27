from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        # Создаем авторизированного пользователя НЕ автора поста
        cls.user_1 = User.objects.create_user(username='NotGena')
        cls.authorized_client_1 = Client()
        cls.authorized_client_1.force_login(cls.user_1)

        cls.client_list_not_author = [cls.guest_client, cls.authorized_client_1]

        cls.group = Group.objects.create(title='Название группы',
                                         slug='test-group',
                                         description='Описание группы')

        cls.post = Post.objects.create(text='Тестовый текст статьи',
                                       author=cls.user)

        cls.templates_url_names_guest_client = {'index.html': reverse('index'),
                                                'group.html': reverse('group_posts', kwargs={'slug': 'test-group'}),
                                                'profile.html': reverse('profile', kwargs={'username': 'Gena'}),
                                                'post.html': reverse('post',
                                                                     kwargs={'username': 'Gena',
                                                                             'post_id': 1})}
        cls.templates_url_names_authorized_client = {'follow.html': reverse('follow_index'),
                                                     'posts/new_post.html': reverse('post_edit',
                                                                                    kwargs={'username': 'Gena',
                                                                                            'post_id': 1})}
        cls.templates_url_names = {**cls.templates_url_names_guest_client,
                                   **cls.templates_url_names_authorized_client}

    # Проверяем доступ страниц для зарегестирированных пользователей
    #  и автора поста
    def test_url_authorized_client(self):
        for url in PostURLTests.templates_url_names_authorized_client.values():
            with self.subTest(url=url):
                response = PostURLTests.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    # Проверяем доступ страниц для зарегестирированных пользователей
    #  для new
    def test_url_authorized_client_new(self):
        response = PostURLTests.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    # Проверяем общедоступные страницы
    def test_url_guest_client(self):
        for url in PostURLTests.templates_url_names_guest_client.values():
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
    # Проверяем возвращает ли сервер код 404, если страница не найдена

    def test_url_authorized_client_not_page(self):
        response = PostURLTests.authorized_client.get('/new_post/not_page/')
        self.assertEqual(response.status_code, 404)
    # Проверяем что только автор поста может редактировать его
    # статус для гостя и НЕ атора поста

    def test_url_post_edit_only_author_status_code(self):
        url = reverse('post_edit', kwargs={'username': 'Gena', 'post_id': 1})
        for client in PostURLTests.client_list_not_author:
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, 302)

    # редирект для гостя отправляет на регистрацию
    def test_url_post_edit_only_author_redirects_guest(self):
        url_post_edit = reverse('post_edit', kwargs={'username': 'Gena', 'post_id': 1})
        url_auth = '/auth/login/?next=' + url_post_edit
        response = PostURLTests.guest_client.get(url_post_edit)
        self.assertRedirects(response, url_auth)

    # редирект для авторизованного пользователя на страницу поста
    def test_url_post_edit_only_author_redirects_authorized_client(self):
        url_post_edit = reverse('post_edit', kwargs={'username': 'Gena', 'post_id': 1})
        url_post = reverse('post', kwargs={'username': 'Gena', 'post_id': 1})
        response = PostURLTests.authorized_client_1.get(url_post_edit)
        self.assertRedirects(response, url_post)
