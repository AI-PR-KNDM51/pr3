import telebot
from telebot import types

# Ініціалізація бота з використанням токену
bot = telebot.TeleBot('8137252780:AAGrFqlpmOXe00EyQjc3cs3D_Ub3Q29FNpE')

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Відправлення повідомлення користувачу з запитом типу кнопки
    bot.send_message(message.chat.id, "Вітаю! Вкажіть тип кнопки (inline або reply):")
    # Реєстрація наступного кроку для обробки відповіді користувача
    bot.register_next_step_handler(message, get_button_type)

# Функція для отримання типу кнопки від користувача
def get_button_type(message):
    # Отримання тексту повідомлення та приведення до нижнього регістру
    button_type = message.text.strip().lower()
    # Перевірка, чи введено правильний тип кнопки
    if button_type not in ['inline', 'reply']:
        # Відправлення повідомлення про помилку
        bot.send_message(message.chat.id, "Невірний тип кнопки. Спробуйте ще раз.")
        # Повторна реєстрація наступного кроку
        bot.register_next_step_handler(message, get_button_type)
    else:
        # Запит кількості кнопок у користувача
        bot.send_message(message.chat.id, "Вкажіть кількість кнопок:")
        # Реєстрація наступного кроку з передачею типу кнопки
        bot.register_next_step_handler(message, get_button_count, button_type)

# Функція для отримання кількості кнопок від користувача
def get_button_count(message, button_type):
    try:
        # Спроба перетворити введений текст на ціле число
        count = int(message.text.strip())
        if count <= 0:
            raise ValueError
    except ValueError:
        # Відправлення повідомлення про некоректне число
        bot.send_message(message.chat.id, "Невірне число. Спробуйте ще раз.")
        # Повторна реєстрація наступного кроку з передачею типу кнопки
        bot.register_next_step_handler(message, get_button_count, button_type)
        return

    # Виклик функції для створення кнопок
    create_buttons(message.chat.id, button_type, count)

# Функція для створення та відправлення кнопок користувачу
def create_buttons(chat_id, button_type, count):
    if button_type == 'inline':
        # Створення Inline клавіатури
        markup = types.InlineKeyboardMarkup()
        for i in range(count):
            # Створення кожної кнопки з відповідним текстом та callback_data
            button = types.InlineKeyboardButton(f"Кнопка {i+1}", callback_data=f"button_{i+1}")
            markup.add(button)
        # Відправлення повідомлення з Inline клавіатурою
        bot.send_message(chat_id, "Ваші кнопки:", reply_markup=markup)
    elif button_type == 'reply':
        # Створення Reply клавіатури з рядком по 2 кнопки
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for i in range(count):
            # Створення кожної кнопки з відповідним текстом
            button = types.KeyboardButton(f"Кнопка {i+1}")
            markup.add(button)
        # Відправлення повідомлення з Reply клавіатурою
        bot.send_message(chat_id, "Ваші кнопки:", reply_markup=markup)

# Обробник callback запитів для Inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Відповідь на натискання кнопки з повідомленням
    bot.answer_callback_query(call.id, f"Ви натиснули {call.data}")

# Запуск бота в нескінченному циклі
bot.polling(none_stop=True)