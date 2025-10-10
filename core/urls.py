from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_http_methods

from core.views import WelcomeView


# Обработчик для несуществующих маршрутов
@require_http_methods(["GET", "POST"])
def handle_404(request, exception=None):
    """Обработчик для несуществующих маршрутов"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found on this server.',
        'path': request.path
    }, status=404)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/user/', include('users.urls')),
    path('api/', include('accounting.urls')),
    path('telegram/', include('telegram_bot.urls')),
    path('', WelcomeView.as_view(), name='welcome'),
]

# Добавляем обработчик для всех несуществующих маршрутов
handler404 = handle_404
