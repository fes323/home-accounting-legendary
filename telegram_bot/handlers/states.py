"""
Состояния FSM для различных процессов.
"""

from aiogram.fsm.state import State, StatesGroup


class TransactionStates(StatesGroup):
    """Состояния для создания транзакций."""
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_wallet = State()


class WalletStates(StatesGroup):
    """Состояния для создания кошельков."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_currency = State()


class CategoryStates(StatesGroup):
    """Состояния для создания категорий."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_parent = State()


class TransactionCategoryStates(StatesGroup):
    """Состояния для создания категории во время транзакции."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_parent = State()


class SettingsStates(StatesGroup):
    """Состояния для настроек."""
    waiting_for_language = State()
    waiting_for_currency = State()
    waiting_for_notifications = State()
