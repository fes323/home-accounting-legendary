"""
Главный роутер для объединения всех обработчиков.
"""

from aiogram import Dispatcher

from .balance_handlers import BalanceHandler
from .category_handlers import CategoryHandler
from .settings_handlers import SettingsHandler
from .transaction_handlers import TransactionHandler
from .wallet_handlers import WalletHandler
from .webapp_handlers import WebAppHandler


def register_handlers(dp: Dispatcher):
    """
    Регистрация всех обработчиков в диспетчере.

    Args:
        dp: Диспетчер aiogram для регистрации роутеров
    """
    # Создаем экземпляры обработчиков
    balance_handler = BalanceHandler()
    category_handler = CategoryHandler()
    settings_handler = SettingsHandler()
    transaction_handler = TransactionHandler()
    wallet_handler = WalletHandler()
    webapp_handler = WebAppHandler()

    # Регистрируем роутеры в диспетчере
    dp.include_router(balance_handler.get_router())
    dp.include_router(category_handler.get_router())
    dp.include_router(settings_handler.get_router())
    dp.include_router(transaction_handler.get_router())
    dp.include_router(wallet_handler.get_router())
    dp.include_router(webapp_handler.get_router())
