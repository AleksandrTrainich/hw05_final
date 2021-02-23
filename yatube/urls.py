from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #  регистрация и авторизация
    path('auth/', include('users.urls')),

    #  если нужного шаблона для /auth не нашлось в файле users.urls —
    #  ищем совпадения в файле django.contrib.auth.urls
    path('auth/', include('django.contrib.auth.urls')),

    #  раздел администратора
    path('admin/', admin.site.urls),

    #  обработчик для главной страницы ищем в urls.py приложения posts
    path('', include('posts.urls')),

    # раздел об авторе и технологиях
    path('about/', include('about.urls', namespace='about')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
