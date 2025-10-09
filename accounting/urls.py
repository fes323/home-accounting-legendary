from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.category_views import TransactionCategoryViewSet
from .views.transaction_views import TransactionViewSet
from .views.wallet_views import WalletViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'categories', TransactionCategoryViewSet, basename='category')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('', include(router.urls)),
]
