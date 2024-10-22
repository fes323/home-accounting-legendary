from django.contrib.auth.backends import BaseBackend
from users.models import User
from django.db.models import Q


class AuthBackend(BaseBackend):
    def authenticate(self, request, username=None, email=None, password=None):
        if request:
            try:
                user = User.objects.get(Q(username=username) | Q(email=email))
            except User.DoesNotExist:
                return None
            finally:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        return None