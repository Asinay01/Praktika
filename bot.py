import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, который вы получили от @BotFather в Telegram
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN)
# Создаем диспетчер для обработки обновлений
dp = Dispatcher(bot)
# Подключаем логгирование для отслеживания действий бота
dp.middleware.setup(LoggingMiddleware())

# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Отправляем сообщение с приветствием и кнопками
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(text="/start"), KeyboardButton(text="/help")]
    keyboard.add(*buttons)
    await message.answer("Привет! Я бот для телеграма. Напиши мне что-нибудь!", reply_markup=keyboard)

# Команда /help
@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    # Отправляем сообщение с информацией о командах
    await message.answer("Это бот для телеграма. Вот что я могу:\n"
                         "/start - начать диалог с ботом\n"
                         "/help - получить помощь")

# Обработка текстовых сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    # Отвечаем пользователю на его сообщение
    await message.answer(f"Ты написал: {message.text}")

# Функция для запуска бота
async def main():
    try:
        # Стартуем бота
        await bot.start_polling(dp)
    except KeyboardInterrupt:
        # Останавливаем бота при нажатии Ctrl+C
        await bot.close()

if __name__ == '__main__':
    # Запускаем цикл событий asyncio для работы бота
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
