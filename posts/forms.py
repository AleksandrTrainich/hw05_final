from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        widgets = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
        }
        labels = {
            'group': _('Сообщество'),
            'image': _('Прикрепите изображение')
        }
        help_texts = {
            'group': _('Выберите группу или оставьте все как есть'),
            'text': _('Напишите что-то хорошее')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
        }
