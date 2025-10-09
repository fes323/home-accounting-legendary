from django.contrib import admin
from django.urls import include, path

from core.views import WelcomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/user/', include('users.urls')),
    path('api/', include('accounting.urls')),
    path('telegram/', include('telegram_bot.urls')),
    path('', WelcomeView.as_view(), name='welcome'),
]
