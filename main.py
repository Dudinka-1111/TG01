import os
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен Telegram-бота
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # API-ключ OpenWeatherMap
CITY = "Moscow"  # Город по умолчанию

# Проверяем, что API_TOKEN и WEATHER_API_KEY заданы
if not API_TOKEN:
    raise ValueError("Токен Telegram-бота (TELEGRAM_BOT_TOKEN) не задан в файле .env")
if not WEATHER_API_KEY:
    raise ValueError("API-ключ для OpenWeatherMap (WEATHER_API_KEY) не задан в файле .env")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру
keyboard_builder = ReplyKeyboardBuilder()
keyboard_builder.row(
    KeyboardButton(text="/weather"), KeyboardButton(text="/help")
)
keyboard = keyboard_builder.as_markup(resize_keyboard=True)


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот, который может показать погоду. 🌤\n"
        "Для начала используй команду /weather, чтобы узнать прогноз погоды.\n"
        "Если нужна помощь, напиши /help.",
        reply_markup=keyboard,
    )


# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Я умею показывать погоду для города Москва. Используй команду:\n"
        "/weather — чтобы узнать текущую погоду."
    )


# Обработчик команды /weather
@dp.message(Command("weather"))
async def weather_command(message: Message):
    try:
        # Запрос к API погоды
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, что запрос успешен
        data = response.json()

        # Проверяем, что данные получены корректно
        if "main" not in data or "weather" not in data:
            await message.answer("Не удалось получить данные о погоде. Попробуйте позже.")
            return

        # Обработка данных
        city = data["name"]
        temp = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]

        # Формируем ответ
        weather_message = (
            f"Погода в городе {city}:\n"
            f"🌡 Температура: {temp}°C\n"
            f"🌥 Описание: {weather_description.capitalize()}"
        )
        await message.answer(weather_message)
    except requests.exceptions.RequestException as e:
        # Обработка ошибок HTTP-запроса
        await message.answer("Произошла ошибка при запросе к API погоды. Попробуйте позже.")
    except Exception as e:
        # Общая обработка ошибок
        await message.answer("Не удалось получить данные о погоде. Попробуйте позже.")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())