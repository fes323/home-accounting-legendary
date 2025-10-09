"""
Обработчики транзакций (доходы и расходы).
"""

import asyncio
import logging
from decimal import Decimal

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards import (category_selection_keyboard,
                                    paginated_category_selection_keyboard,
                                    skip_keyboard, transaction_type_keyboard,
                                    wallet_selection_keyboard)
from telegram_bot.utils import validate_amount

from .base import BaseHandler, ErrorHandler, ResponseFormatter, StateManager
from .states import TransactionCategoryStates, TransactionStates


class TransactionHandler(BaseHandler):
    """Обработчик транзакций."""

    def _register_handlers(self):
        """Регистрация обработчиков транзакций."""
        # Команды
        self.router.message.register(self.cmd_income, Command("income"))
        self.router.message.register(self.cmd_expense, Command("expense"))

        # Кнопки главного меню
        self.router.message.register(self.btn_income, F.text == "➕ Доход")
        self.router.message.register(self.btn_expense, F.text == "➖ Расход")

        # FSM состояния
        self.router.message.register(
            self.process_amount, TransactionStates.waiting_for_amount)
        self.router.message.register(
            self.process_description, TransactionStates.waiting_for_description)

        # FSM состояния для создания категории во время транзакции
        self.router.message.register(
            self.process_transaction_category_title, TransactionCategoryStates.waiting_for_title)
        self.router.message.register(
            self.process_transaction_category_description, TransactionCategoryStates.waiting_for_description)

        # Callback обработчики
        self.router.callback_query.register(
            self.callback_select_wallet, F.data.startswith("select_wallet_"))
        self.router.callback_query.register(
            self.callback_select_category, F.data.startswith("select_category_"))
        self.router.callback_query.register(
            self.callback_no_category, F.data == "no_category")
        self.router.callback_query.register(
            self.callback_create_new_category, F.data == "create_new_category")
        self.router.callback_query.register(
            self.callback_cancel_transaction, F.data == "cancel_transaction")

        # Обработчики для создания категории во время транзакции
        self.router.callback_query.register(
            self.callback_create_transaction_category_root, F.data == "ctcr")
        self.router.callback_query.register(
            self.callback_select_transaction_category_parent, F.data.startswith("tcp_"))
        # Обработчик пагинации выбора категории
        self.router.callback_query.register(
            self.callback_category_select_page, F.data.startswith("category_select_page_"))

    async def cmd_income(self, message: Message, state: FSMContext):
        """Добавить доход."""
        await state.set_state(TransactionStates.waiting_for_amount)
        await state.update_data(transaction_type="IN")

        sent_message = await message.answer(
            "💰 <b>Добавление дохода</b>\n\n"
            "Введите сумму дохода:",
            reply_markup=transaction_type_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def cmd_expense(self, message: Message, state: FSMContext):
        """Добавить расход."""
        await state.set_state(TransactionStates.waiting_for_amount)
        await state.update_data(transaction_type="EX")

        sent_message = await message.answer(
            "💸 <b>Добавление расхода</b>\n\n"
            "Введите сумму расхода:",
            reply_markup=transaction_type_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def btn_income(self, message: Message, state: FSMContext):
        """Обработчик кнопки доход."""
        await self.cmd_income(message, state)

    async def btn_expense(self, message: Message, state: FSMContext):
        """Обработчик кнопки расход."""
        await self.cmd_expense(message, state)

    async def process_amount(self, message: Message, state: FSMContext, django_user):
        """Обработка введенной суммы."""
        amount = validate_amount(message.text)

        if amount is None:
            await message.answer("❌ Неверный формат суммы! Введите положительное число.")
            return

        await state.update_data(amount=amount)
        await state.set_state(TransactionStates.waiting_for_description)

        sent_message = await message.answer(
            "📝 Введите описание транзакции:",
            reply_markup=transaction_type_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def process_description(self, message: Message, state: FSMContext, django_user):
        """Обработка описания транзакции."""
        await state.update_data(description=message.text)
        await state.set_state(TransactionStates.waiting_for_wallet)

        from accounting.models.wallet import Wallet

        wallets = await asyncio.to_thread(
            lambda: list(Wallet.objects.filter(
                user=django_user).select_related('currency'))
        )

        if not wallets:
            await message.answer(
                "❌ У вас нет кошельков! Сначала создайте кошелек командой /wallets"
            )
            await state.clear()
            return

        text = "💳 Выберите кошелек для транзакции:"
        sent_message = await message.answer(text, reply_markup=wallet_selection_keyboard(wallets))
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def callback_select_wallet(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Выбор кошелька для транзакции."""
        wallet_uuid = callback.data.split("_")[-1]

        from accounting.models.wallet import Wallet

        try:
            wallet = await asyncio.to_thread(
                Wallet.objects.select_related(
                    'currency').get, uuid=wallet_uuid, user=django_user
            )

            data = await state.get_data()
            data['wallet_uuid'] = wallet_uuid
            await state.update_data(wallet_uuid=wallet_uuid)

            # Получаем категории пользователя
            from accounting.models.transactionCategory import \
                TransactionCategoryTree
            categories = await asyncio.to_thread(
                lambda: list(
                    TransactionCategoryTree.objects.filter(user=django_user))
            )

            if categories:
                await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
                await state.set_state(TransactionStates.waiting_for_category)
                # Сохраняем категории для пагинации
                await state.update_data(all_categories=categories, current_page=0)
                await callback.message.edit_text(
                    f"📂 Выберите категорию для транзакции:",
                    reply_markup=paginated_category_selection_keyboard(
                        categories, page=0)
                )
            else:
                # Создаем транзакцию без категории
                transaction, updated_wallet = await self._create_transaction(state, django_user, wallet, None)

                # Получаем обновленные данные состояния
                updated_data = await state.get_data()
                await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
                await callback.message.edit_text(
                    ResponseFormatter.format_success_message(
                        "Транзакция добавлена!",
                        [
                            f"💰 Сумма: {updated_data['amount']} {updated_wallet.currency.char_code}",
                            f"📝 Описание: {updated_data['description']}",
                            f"💳 Кошелек: {updated_wallet.title}"
                        ]
                    ),
                    reply_markup=None
                )
                await state.clear()

            await callback.answer()

        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "выбор кошелька"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def callback_select_category(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Выбор категории для транзакции."""
        category_uuid = callback.data.split("_")[-1]

        from accounting.models.transactionCategory import \
            TransactionCategoryTree
        from accounting.models.wallet import Wallet

        try:
            category = await asyncio.to_thread(
                TransactionCategoryTree.objects.get, uuid=category_uuid, user=django_user
            )

            data = await state.get_data()

            if 'wallet_uuid' not in data:
                await callback.message.edit_text(
                    "❌ Ошибка: информация о кошельке потеряна. Начните транзакцию заново.",
                    reply_markup=None
                )
                await state.clear()
                await callback.answer("Произошла ошибка")
                return

            wallet = await asyncio.to_thread(
                Wallet.objects.select_related(
                    'currency').get, uuid=data['wallet_uuid'], user=django_user
            )

            transaction, updated_wallet = await self._create_transaction(state, django_user, wallet, category)

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ResponseFormatter.format_success_message(
                    "Транзакция добавлена!",
                    [
                        f"💰 Сумма: {data['amount']} {updated_wallet.currency.char_code}",
                        f"📝 Описание: {data['description']}",
                        f"📂 Категория: {category.title}",
                        f"💳 Кошелек: {updated_wallet.title}"
                    ]
                ),
                reply_markup=None
            )

            await state.clear()
            await callback.answer("Транзакция успешно добавлена!")

        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "выбор категории"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def callback_no_category(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Создание транзакции без категории."""
        from accounting.models.wallet import Wallet

        try:
            data = await state.get_data()

            if 'wallet_uuid' not in data:
                await callback.message.edit_text(
                    "❌ Ошибка: информация о кошельке потеряна. Начните транзакцию заново.",
                    reply_markup=None
                )
                await state.clear()
                await callback.answer("Произошла ошибка")
                return

            wallet = await asyncio.to_thread(
                Wallet.objects.select_related(
                    'currency').get, uuid=data['wallet_uuid'], user=django_user
            )

            transaction, updated_wallet = await self._create_transaction(state, django_user, wallet, None)

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ResponseFormatter.format_success_message(
                    "Транзакция добавлена!",
                    [
                        f"💰 Сумма: {data['amount']} {updated_wallet.currency.char_code}",
                        f"📝 Описание: {data['description']}",
                        f"💳 Кошелек: {updated_wallet.title}"
                    ]
                ),
                reply_markup=None
            )

            await state.clear()
            await callback.answer("Транзакция успешно добавлена!")

        except Exception as e:
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "создание транзакции"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def callback_cancel_transaction(self, callback: CallbackQuery, state: FSMContext):
        """Отмена транзакции."""
        await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
        await state.clear()
        await callback.message.edit_text("❌ Транзакция отменена", reply_markup=None)
        await callback.answer("Транзакция отменена")

    async def _create_transaction(self, state: FSMContext, django_user, wallet, category):
        """Создание транзакции."""
        from django.db.models import Sum

        from accounting.models.transaction import Transaction
        from accounting.models.wallet import Wallet

        data = await state.get_data()

        # Логируем данные для отладки
        self.logger.info(f"Creating transaction: user={django_user.username}, wallet={wallet.title}, "
                         f"type={data['transaction_type']}, amount={data['amount']}, "
                         f"description={data['description']}")

        transaction = await asyncio.to_thread(
            lambda: Transaction.objects.create(
                user=django_user,
                wallet=wallet,
                category=category,
                t_type=data['transaction_type'],
                amount=Decimal(str(data['amount'])),
                description=data['description']
            )
        )

        # Принудительно обновляем баланс кошелька
        await asyncio.to_thread(
            lambda: wallet.refresh_from_db()
        )

        # Пересчитываем баланс на основе всех транзакций
        total_income = await asyncio.to_thread(
            lambda: Transaction.objects.filter(wallet=wallet, t_type='IN').aggregate(
                total=Sum('amount'))['total'] or Decimal('0')
        )
        total_expense = await asyncio.to_thread(
            lambda: Transaction.objects.filter(wallet=wallet, t_type='EX').aggregate(
                total=Sum('amount'))['total'] or Decimal('0')
        )

        new_balance = total_income - total_expense
        await asyncio.to_thread(
            lambda: Wallet.objects.filter(
                uuid=wallet.uuid).update(balance=new_balance)
        )

        # Обновляем объект кошелька из базы данных
        wallet = await asyncio.to_thread(
            Wallet.objects.select_related('currency').get, uuid=wallet.uuid
        )

        # Логируем результат
        self.logger.info(
            f"Transaction created: {transaction.uuid}, wallet balance after: {wallet.balance}")

        return transaction, wallet

    async def callback_create_new_category(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Начало создания новой категории во время транзакции."""
        try:
            # Сохраняем текущие данные транзакции
            data = await state.get_data()
            await state.update_data(
                # Сохраняем данные транзакции
                transaction_amount=data.get('amount'),
                transaction_description=data.get('description'),
                transaction_type=data.get('transaction_type'),
                transaction_wallet_uuid=data.get('wallet_uuid'),
                # Флаг что мы создаем категорию для транзакции
                creating_category_for_transaction=True
            )

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await state.set_state(TransactionCategoryStates.waiting_for_title)

            await callback.message.edit_text(
                "📂 <b>Создание новой категории</b>\n\n"
                "Введите название категории:",
                reply_markup=None
            )
            await callback.answer()

        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "создание категории"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def process_transaction_category_title(self, message: Message, state: FSMContext):
        """Обработка названия категории для транзакции."""
        await state.update_data(category_title=message.text)
        await state.set_state(TransactionCategoryStates.waiting_for_description)

        sent_message = await message.answer(
            "📝 Введите описание категории:",
            reply_markup=skip_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def process_transaction_category_description(self, message: Message, state: FSMContext, django_user):
        """Обработка описания категории для транзакции."""
        description = message.text if message.text != "-" else ""
        await state.update_data(category_description=description)

        # Получаем существующие категории для выбора родительской
        from accounting.models.transactionCategory import \
            TransactionCategoryTree
        categories = await asyncio.to_thread(
            lambda: list(
                TransactionCategoryTree.objects.filter(user=django_user))
        )

        if categories:
            await state.set_state(TransactionCategoryStates.waiting_for_parent)
            sent_message = await message.answer(
                "📂 Выберите родительскую категорию:",
                reply_markup=self._transaction_category_parent_keyboard(
                    categories)
            )
            await StateManager.save_message_with_keyboard(sent_message, state)
        else:
            # Создаем корневую категорию
            await self._create_transaction_category(state, django_user, None, message)

    async def callback_create_transaction_category_root(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Создание корневой категории для транзакции."""
        try:
            await self._create_transaction_category(state, django_user, None, callback.message)
            await callback.answer("Категория успешно создана!")
        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "создание категории"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def callback_select_transaction_category_parent(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Выбор родительской категории для транзакции."""
        category_uuid = callback.data.split("_")[1]  # tcp_uuid -> uuid

        from accounting.models.transactionCategory import \
            TransactionCategoryTree

        try:
            parent_category = await asyncio.to_thread(
                TransactionCategoryTree.objects.get, uuid=category_uuid, user=django_user
            )

            await self._create_transaction_category(state, django_user, parent_category, callback.message)
            await callback.answer("Категория успешно создана!")

        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(
                    e, "выбор родительской категории"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def _create_transaction_category(self, state: FSMContext, django_user, parent_category, message_or_callback):
        """Создание категории и продолжение транзакции."""
        from accounting.models.transactionCategory import \
            TransactionCategoryTree

        data = await state.get_data()

        # Проверяем уникальность названия категории для пользователя
        existing_category = await asyncio.to_thread(
            lambda: TransactionCategoryTree.objects.filter(
                user=django_user,
                title=data['category_title'],
                parent=parent_category
            ).first()
        )

        if existing_category:
            error_msg = f"❌ Категория с названием '{data['category_title']}' уже существует"
            if hasattr(message_or_callback, 'edit_text'):
                await message_or_callback.edit_text(error_msg, reply_markup=None)
            else:
                await message_or_callback.answer(error_msg)
            return

        # Создаем категорию
        category = await asyncio.to_thread(
            lambda: TransactionCategoryTree.objects.create(
                user=django_user,
                parent=parent_category,
                title=data['category_title'],
                description=data['category_description']
            )
        )

        # Восстанавливаем данные транзакции
        await state.update_data(
            amount=data['transaction_amount'],
            description=data['transaction_description'],
            transaction_type=data['transaction_type'],
            wallet_uuid=data['transaction_wallet_uuid']
        )

        # Возвращаемся к состоянию выбора категории и сразу выбираем созданную
        await state.set_state(TransactionStates.waiting_for_category)

        # Получаем кошелек
        from accounting.models.wallet import Wallet
        wallet = await asyncio.to_thread(
            Wallet.objects.select_related('currency').get,
            uuid=data['transaction_wallet_uuid'],
            user=django_user
        )

        # Создаем транзакцию с новой категорией
        transaction, updated_wallet = await self._create_transaction(state, django_user, wallet, category)

        # Отправляем сообщение об успехе
        success_message = ResponseFormatter.format_success_message(
            "Транзакция добавлена!",
            [
                f"💰 Сумма: {data['transaction_amount']} {updated_wallet.currency.char_code}",
                f"📝 Описание: {data['transaction_description']}",
                f"📂 Категория: {category.title}",
                f"💳 Кошелек: {updated_wallet.title}"
            ]
        )

        if hasattr(message_or_callback, 'edit_text'):
            await StateManager.cleanup_previous_inline_keyboards(message_or_callback, state)
            await message_or_callback.edit_text(success_message, reply_markup=None)
        else:
            await message_or_callback.answer(success_message)

        await state.clear()

    def _transaction_category_parent_keyboard(self, categories):
        """Клавиатура для выбора родительской категории во время транзакции."""
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        from aiogram.utils.keyboard import InlineKeyboardBuilder

        builder = InlineKeyboardBuilder()

        for category in categories:
            indent = "  " * category.level
            # Используем более короткий callback_data
            builder.add(InlineKeyboardButton(
                text=f"{indent}{category.title}",
                callback_data=f"tcp_{category.uuid}"
            ))

        builder.add(InlineKeyboardButton(
            text="⏭️ Создать корневую категорию",
            callback_data="ctcr"
        ))
        builder.add(InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_transaction"
        ))

        builder.adjust(1)
        return builder.as_markup()

    async def callback_category_select_page(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик пагинации выбора категории в транзакции."""
        try:
            page = int(callback.data.split("_")[-1])
            data = await state.get_data()
            categories = data.get('all_categories', [])

            if not categories:
                await callback.answer("Категории не найдены")
                return

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                f"📂 Выберите категорию для транзакции:",
                reply_markup=paginated_category_selection_keyboard(
                    categories, page=page)
            )
            await state.update_data(current_page=page)
            await callback.answer()

        except Exception as e:
            self.logger.error(
                f"Error in callback_category_select_page: {str(e)}")
            await callback.answer("Произошла ошибка при переключении страницы")
