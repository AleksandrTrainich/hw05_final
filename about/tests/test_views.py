from django.test import TestCase, Client
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем пользователя

        cls.temp_url_names = {'about/author.html': reverse('about:author'),
                              'about/tech.html': reverse('about:tech')}

    #  Проверка вызываемых шаблонов
    def test_urls_uses_correct_template(self):
        for template, url in AboutViewsTests.temp_url_names.items():
            with self.subTest(url=url):
                response = AboutViewsTests.guest_client.get(url)
                self.assertTemplateUsed(response, template)
