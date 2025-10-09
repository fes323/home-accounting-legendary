"""
Обработчики категорий транзакций.
"""

import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards import (categories_keyboard,
                                    category_parent_selection_keyboard,
                                    paginated_categories_keyboard,
                                    paginated_category_selection_keyboard,
                                    skip_keyboard)

from .base import BaseHandler, ErrorHandler, ResponseFormatter, StateManager
from .states import CategoryStates


class CategoryHandler(BaseHandler):
    """Обработчик категорий."""

    def _register_handlers(self):
        """Регистрация обработчиков категорий."""
        # Команды
        self.router.message.register(
            self.cmd_categories, Command("categories"))

        # Кнопки главного меню
        self.router.message.register(
            self.btn_categories, F.text == "📂 Категории")

        # FSM состояния
        self.router.message.register(
            self.process_category_title, CategoryStates.waiting_for_title)
        self.router.message.register(
            self.process_category_description, CategoryStates.waiting_for_description)

        # Callback обработчики
        self.router.callback_query.register(
            self.callback_create_category, F.data == "create_category")
        self.router.callback_query.register(
            self.callback_create_root_category, F.data == "create_root_category")
        self.router.callback_query.register(
            self.callback_select_parent_category, F.data.startswith("select_category_parent_"))
        self.router.callback_query.register(
            self.callback_cancel_category, F.data == "cancel_category")
        # Обработчики пагинации
        self.router.callback_query.register(
            self.callback_categories_page, F.data.startswith("categories_page_"))
        self.router.callback_query.register(
            self.callback_category_select_page, F.data.startswith("category_select_page_"))

    async def cmd_categories(self, message: Message, django_user, state: FSMContext):
        """Управление категориями."""
        from accounting.models.transactionCategory import \
            TransactionCategoryTree

        categories = await asyncio.to_thread(
            lambda: list(
                TransactionCategoryTree.objects.filter(user=django_user))
        )

        text = "📂 <b>Управление категориями</b>\n\n"

        if categories:
            text += f"Всего категорий: {len(categories)}\n"
            text += "Выберите действие:"
        else:
            text += "У вас пока нет категорий."

        sent_message = await message.answer(
            text,
            reply_markup=categories_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def btn_categories(self, message: Message, django_user, state: FSMContext):
        """Обработчик кнопки категории."""
        await self.cmd_categories(message, django_user, state)

    async def callback_create_category(self, callback: CallbackQuery, state: FSMContext):
        """Создание новой категории."""
        self.logger.info("Starting category creation process")
        await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
        await state.set_state(CategoryStates.waiting_for_title)
        await callback.message.edit_text(
            "📂 <b>Создание категории</b>\n\n"
            "Введите название категории:",
            reply_markup=None
        )
        await callback.answer()

    async def process_category_title(self, message: Message, state: FSMContext):
        """Обработка названия категории."""
        self.logger.info(f"Processing category title: {message.text}")
        await state.update_data(title=message.text)
        await state.set_state(CategoryStates.waiting_for_description)

        sent_message = await message.answer(
            "📝 Введите описание категории:",
            reply_markup=skip_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def process_category_description(self, message: Message, state: FSMContext, django_user):
        """Обработка описания категории."""
        description = message.text if message.text != "-" else ""
        self.logger.info(f"Processing category description: {description}")
        await state.update_data(description=description)

        # Получаем существующие категории для выбора родительской
        from accounting.models.transactionCategory import \
            TransactionCategoryTree
        categories = await asyncio.to_thread(
            lambda: list(
                TransactionCategoryTree.objects.filter(user=django_user))
        )

        self.logger.info(
            f"Found {len(categories)} existing categories for user {django_user}")

        if categories:
            await state.set_state(CategoryStates.waiting_for_parent)
            # Сохраняем все категории в состоянии для пагинации
            await state.update_data(all_categories=categories, current_page=0)
            sent_message = await message.answer(
                "📂 Выберите родительскую категорию:",
                reply_markup=paginated_categories_keyboard(categories, page=0)
            )
            await StateManager.save_message_with_keyboard(sent_message, state)
        else:
            # Создаем корневую категорию
            self.logger.info("No existing categories, creating root category")
            await self._create_category(state, django_user, None)
            await message.answer("✅ Категория создана!")
            await state.clear()

    async def callback_create_root_category(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Создание корневой категории."""
        try:
            await self._create_category(state, django_user, None)
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text("✅ Категория создана!", reply_markup=None)
            await state.clear()
            await callback.answer("Категория успешно создана!")
        except Exception as e:
            self.logger.error(
                f"Error in callback_create_root_category: {str(e)}")
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)

            # Более информативное сообщение об ошибке
            if "already exists" in str(e) or "unique constraint" in str(e).lower():
                error_msg = "❌ Категория с таким названием уже существует"
            else:
                error_msg = f"❌ Ошибка при создании категории: {str(e)}"

            await callback.message.edit_text(error_msg, reply_markup=None)
            await callback.answer("Произошла ошибка")

    async def callback_select_parent_category(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Выбор родительской категории."""
        category_uuid = callback.data.split("_")[-1]

        self.logger.info(
            f"Selecting parent category with UUID: {category_uuid}")

        from accounting.models.transactionCategory import \
            TransactionCategoryTree

        try:
            parent_category = await asyncio.to_thread(
                TransactionCategoryTree.objects.get, uuid=category_uuid, user=django_user
            )

            self.logger.info(f"Found parent category: {parent_category}")

            await self._create_category(state, django_user, parent_category)

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text("✅ Категория создана!", reply_markup=None)
            await state.clear()
            await callback.answer("Категория успешно создана!")

        except Exception as e:
            self.logger.error(
                f"Error in callback_select_parent_category: {str(e)}")
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)

            # Более информативное сообщение об ошибке
            if "already exists" in str(e) or "unique constraint" in str(e).lower():
                error_msg = "❌ Категория с таким названием уже существует в данной родительской категории"
            elif "not found" in str(e).lower():
                error_msg = "❌ Родительская категория не найдена"
            else:
                error_msg = f"❌ Ошибка при создании категории: {str(e)}"

            await callback.message.edit_text(error_msg, reply_markup=None)
            await callback.answer("Произошла ошибка")

    async def callback_cancel_category(self, callback: CallbackQuery, state: FSMContext):
        """Отмена создания категории."""
        await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
        await state.clear()
        await callback.message.edit_text("❌ Создание категории отменено", reply_markup=None)
        await callback.answer("Создание категории отменено")

    async def _create_category(self, state: FSMContext, django_user, parent_category):
        """Создание категории."""
        from accounting.models.transactionCategory import \
            TransactionCategoryTree

        data = await state.get_data()

        # Логируем данные для отладки
        self.logger.info(f"Creating category with data: {data}")
        self.logger.info(f"Parent category: {parent_category}")
        self.logger.info(f"Django user: {django_user}")

        try:
            # Проверяем уникальность названия категории для пользователя
            existing_category = await asyncio.to_thread(
                lambda: TransactionCategoryTree.objects.filter(
                    user=django_user,
                    title=data['title'],
                    parent=parent_category
                ).first()
            )

            if existing_category:
                self.logger.warning(
                    f"Category with title '{data['title']}' already exists for user {django_user}")
                raise ValueError(
                    f"Категория с названием '{data['title']}' уже существует")

            category = await asyncio.to_thread(
                lambda: TransactionCategoryTree.objects.create(
                    user=django_user,
                    parent=parent_category,
                    title=data['title'],
                    description=data['description']
                )
            )
            self.logger.info(f"Category created successfully: {category}")
            return category
        except Exception as e:
            self.logger.error(f"Error creating category: {str(e)}")
            raise

    async def callback_categories_page(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик пагинации категорий."""
        try:
            page = int(callback.data.split("_")[-1])
            data = await state.get_data()
            categories = data.get('all_categories', [])

            if not categories:
                await callback.answer("Категории не найдены")
                return

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                "📂 Выберите родительскую категорию:",
                reply_markup=paginated_categories_keyboard(
                    categories, page=page)
            )
            await state.update_data(current_page=page)
            await callback.answer()

        except Exception as e:
            self.logger.error(f"Error in callback_categories_page: {str(e)}")
            await callback.answer("Произошла ошибка при переключении страницы")

    async def callback_category_select_page(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик пагинации выбора категории."""
        try:
            page = int(callback.data.split("_")[-1])
            data = await state.get_data()
            categories = data.get('all_categories', [])

            if not categories:
                await callback.answer("Категории не найдены")
                return

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                "📂 Выберите родительскую категорию:",
                reply_markup=paginated_categories_keyboard(
                    categories, page=page)
            )
            await state.update_data(current_page=page)
            await callback.answer()

        except Exception as e:
            self.logger.error(
                f"Error in callback_category_select_page: {str(e)}")
            await callback.answer("Произошла ошибка при переключении страницы")
