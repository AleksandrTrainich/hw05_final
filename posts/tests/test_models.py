from django.test import TestCase
from posts.models import Post, Group
from django.contrib.auth import get_user_model


User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        cls.group = Group.objects.create(title='Заголовок тестовой задачи',
                                         slug='test-group',
                                         description='Описание группы')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {"title": "Название группы",
                          "description": "Тематика группы",
                          'slug': "Адрес для страницы группы"}
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_texts = {"title": 'Введите название вашего сообщества',
                            "description": 'Напишите какие темы будут обсуждаться у Вас в сообществе',
                            "slug": 'Используйте латиницу'}
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        # /__str__  group - это строчка с содержимым post.title
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(text='текст поста длинною больше пяднадцати символов',
                                       author=User.objects.create(username='Gena'))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Статья",
            "group": "Группа",
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {"text": 'Напишите о том что Вас волнует',
                            "group": 'Выберите группу'}
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = PostModelTest.post
        post_str_15 = str(post)[:15]
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, post_str_15)
