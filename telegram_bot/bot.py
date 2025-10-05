import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import (SimpleRequestHandler,
                                            setup_application)
from aiohttp import web

from telegram_bot.config import (BOT_COMMANDS, TELEGRAM_BOT_TOKEN,
                                 TELEGRAM_WEBHOOK_SECRET, WEBHOOK_PATH,
                                 WEBHOOK_URL)
from telegram_bot.handlers import register_handlers
from telegram_bot.middleware import AuthMiddleware, DatabaseMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_bot():
    """Создание и настройка бота"""
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Установка команд бота
    await bot.set_my_commands(BOT_COMMANDS)

    return bot


async def create_dispatcher():
    """Создание диспетчера с middleware"""
    dp = Dispatcher()

    # Регистрация middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    # Регистрация обработчиков
    register_handlers(dp)

    return dp


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Бот запущен!")

    # Установка webhook
    if WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=TELEGRAM_WEBHOOK_SECRET
        )
        logger.info(f"Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Бот остановлен!")

    # Удаление webhook
    if WEBHOOK_URL:
        await bot.delete_webhook()
        logger.info("Webhook удален")


def create_webhook_app():
    """Создание приложения для webhook"""
    app = web.Application()

    # Создание бота и диспетчера
    bot = asyncio.run(create_bot())
    dp = asyncio.run(create_dispatcher())

    # Настройка webhook
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=TELEGRAM_WEBHOOK_SECRET
    )

    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Настройка приложения
    setup_application(app, dp, bot=bot)

    # Обработчики запуска и остановки
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    return app


def run_polling():
    """Запуск бота в режиме polling (для разработки)"""
    async def main():
        bot = await create_bot()
        dp = await create_dispatcher()

        await on_startup(bot)

        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown(bot)

    asyncio.run(main())
