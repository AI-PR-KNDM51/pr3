import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp

# Токен вашого бота, отриманий від BotFather
API_TOKEN = '8137252780:AAGrFqlpmOXe00EyQjc3cs3D_Ub3Q29FNpE'
# Ключ API для обміну валют, отриманий з exchangerate-api.com
EXCHANGE_RATE_API_KEY = 'e6a128704926c1ae26b5b22b'

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словник для зберігання даних користувачів (тимчасове зберігання вибору валюти)
user_data = {}
# Список доступних валют для вибору
currencies = ['USD', 'EUR', 'UAH']

# Обробник команди /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    # Створення Inline клавіатури з кнопками для вибору валюти
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=currency, callback_data=currency)] for currency in currencies
    ])
    # Відправлення повідомлення користувачу з клавіатурою
    await message.answer("Виберіть валюту для оплати:", reply_markup=keyboard)

# Обробник вибору валюти через callback_query
@dp.callback_query(lambda c: c.data in currencies)
async def process_currency_selection(callback: types.CallbackQuery):
    currency = callback.data  # Отримання вибраної валюти
    user_id = callback.from_user.id  # Отримання ID користувача
    # Збереження вибору валюти у словнику user_data
    user_data[user_id] = {'currency': currency}
    # Запит користувача ввести суму в USD
    await bot.send_message(chat_id=user_id, text="Введіть суму в USD:")
    # Підтвердження отримання callback_query
    await callback.answer()

# Обробник повідомлень з введеною сумою
@dp.message()
async def process_amount(message: types.Message):
    user_id = message.from_user.id  # Отримання ID користувача
    # Перевірка, чи користувач обрав валюту
    if user_id in user_data and 'currency' in user_data[user_id]:
        try:
            # Спроба конвертувати введений текст у число
            amount_usd = float(message.text.replace(',', '.'))
            currency = user_data[user_id]['currency']  # Отримання вибраної валюти
            # Використання aiohttp для асинхронного HTTP запиту до API обміну валют
            async with aiohttp.ClientSession() as session:
                url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"
                async with session.get(url) as response:
                    data = await response.json()
            # Перевірка, чи API повернув необхідні дані
            if 'conversion_rates' in data and currency in data['conversion_rates']:
                exchange_rate = data['conversion_rates'][currency]  # Отримання курсу обміну
                converted_amount = amount_usd * exchange_rate  # Обчислення конвертованої суми
                # Відправлення результату користувачу
                await message.reply(f"Сума в {currency}: {converted_amount:.2f}")
                # Видалення даних користувача з словника після завершення операції
                del user_data[user_id]
            else:
                # Повідомлення про помилку, якщо курс обміну не знайдено
                await message.reply("Не вдалося отримати курс обміну. Спробуйте пізніше.")
        except ValueError:
            # Повідомлення про помилку, якщо введена сума некоректна
            await message.reply("Будь ласка, введіть коректну числову суму.")
    else:
        # Повідомлення про необхідність вибору валюти перед введенням суми
        await message.reply("Будь ласка, спочатку виберіть валюту за допомогою /start")

# Основна асинхронна функція для запуску бота
async def main():
    await dp.start_polling(bot)

# Запуск бота при виконанні скрипту
if __name__ == '__main__':
    asyncio.run(main())