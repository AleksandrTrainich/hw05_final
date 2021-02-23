from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название группы",
                             max_length=200,
                             help_text='Введите название вашего сообщества')
    slug = models.SlugField(verbose_name="Адрес для страницы группы",
                            max_length=100,
                            unique=True,
                            help_text='Используйте латиницу')
    description = models.TextField("Тематика группы",
                                   help_text='Напишите какие темы будут обсуждаться у Вас в сообществе')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Статья",
        help_text='Напишите о том что Вас волнует')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              verbose_name="Группа",
                              help_text='Выберите группу',
                              on_delete=models.SET_NULL,
                              related_name="posts",
                              blank=True,
                              null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-pub_date"]

class Comment(models.Model):
    text = models.TextField(
        "Комментарий",
        help_text='Напишите о свой комментарий')
    created = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="сomments")
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="сomments")

    class Meta:
        ordering = ['-created']

class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')

    def __str__(self):
        return self.author.username
