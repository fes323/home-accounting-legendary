
from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet
from users.views.auth_views import telegram_auth, user_profile

userRouter = routers.DefaultRouter()
userRouter.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(userRouter.urls)),
    path('auth/telegram/', telegram_auth, name='telegram_auth'),
    path('auth/profile/', user_profile, name='user_profile'),
]
