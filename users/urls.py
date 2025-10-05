
from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet

userRouter = routers.DefaultRouter()
userRouter.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(userRouter.urls))
]
