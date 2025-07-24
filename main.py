
import os
import random
import string
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Состояния для ConversationHandler
CHOOSING, GETTING_RANGE, GETTING_LIST, GETTING_PASSWORD_LENGTH = range(4)

# --- Функции для главного меню ---
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = "Выберите рандомайзер:"):
    """Отображает главное меню с кнопками."""
    keyboard = [
        [InlineKeyboardButton("🪙 Монетка", callback_data='coin_flip'), InlineKeyboardButton("👍 Да/Нет", callback_data='yes_no')],
        [InlineKeyboardButton("🎲 Кости", callback_data='dice_roll'), InlineKeyboardButton("🔢 Число", callback_data='random_number')],
        [InlineKeyboardButton("🎨 Цвет", callback_data='random_color'), InlineKeyboardButton("🤔 Цитата", callback_data='random_quote')],
        [InlineKeyboardButton("💡 Факт", callback_data='random_fact'), InlineKeyboardButton("🃏 Карта", callback_data='random_card')],
        [InlineKeyboardButton("🔒 Пароль", callback_data='password_generator')],
        [InlineKeyboardButton("🔀 Выбрать из списка", callback_data='list_choice')],
        [InlineKeyboardButton("🔄 Перемешать список", callback_data='list_shuffle')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога."""
    await show_main_menu(update, context, text=f"Привет, {update.effective_user.first_name}! Я бот-рандомайзер. Чем займемся?")
    return CHOOSING

# --- Обработчики кнопок ---
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает нажатия кнопок в главном меню."""
    query = update.callback_query
    await query.answer()
    choice = query.data

    # Просто и быстро
    if choice == 'coin_flip':
        result = random.choice(["Орёл 🦅", "Решка 🪙"])
        await query.edit_message_text(text=f"Выпало: **{result}**", parse_mode='Markdown')
    elif choice == 'yes_no':
        result = random.choice(["Да 👍", "Нет 👎"])
        await query.edit_message_text(text=f"Ответ: **{result}**", parse_mode='Markdown')
    elif choice == 'random_color':
        r, g, b = [random.randint(0, 255) for _ in range(3)]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        await query.edit_message_text(text=f"Случайный цвет:\nHEX: `{hex_color}`\nRGB: `({r}, {g}, {b})`", parse_mode='Markdown')
    elif choice == 'random_quote':
        quotes = ["Жизнь - это то, что с тобой происходит, пока ты строишь другие планы.", "Единственный способ делать великие дела — любить то, что вы делаете.", "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма."]
        await query.edit_message_text(text=f"Цитата дня:\n> _{random.choice(quotes)}_", parse_mode='Markdown')
    elif choice == 'random_fact':
        facts = ["У медуз нет мозга.", "Сердце синего кита настолько велико, что человек может плавать в его артериях.", "Бананы - это ягоды, а клубника - нет."]
        await query.edit_message_text(text=f"Случайный факт:\n> _{random.choice(facts)}_", parse_mode='Markdown')
    elif choice == 'random_card':
        suits = ["♥️", "♦️", "♣️", "♠️"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        card = f"{random.choice(ranks)}{random.choice(suits)}"
        await query.edit_message_text(text=f"Случайная карта: **{card}**", parse_mode='Markdown')

    # Переход в другие состояния
    elif choice == 'dice_roll':
        await show_dice_menu(update, context)
        return CHOOSING # Остаемся в том же состоянии для выбора кости
    elif choice == 'random_number':
        await query.edit_message_text(text="Введите диапазон чисел в формате `мин макс` (например, `1 100`).")
        return GETTING_RANGE
    elif choice == 'password_generator':
        await query.edit_message_text(text="Введите желаемую длину пароля (число от 8 до 128).")
        return GETTING_PASSWORD_LENGTH
    elif choice == 'list_choice' or choice == 'list_shuffle':
        context.user_data['list_mode'] = choice
        await query.edit_message_text(text="Отправьте мне список элементов, каждый с новой строки.")
        return GETTING_LIST

    # После простого действия, снова показать меню
    await show_main_menu(update, context, text="Готово! Что-нибудь еще?")
    return CHOOSING

# --- Меню для игральных костей ---
async def show_dice_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("D4", callback_data='d4'), InlineKeyboardButton("D6", callback_data='d6'), InlineKeyboardButton("D8", callback_data='d8')],
        [InlineKeyboardButton("D10", callback_data='d10'), InlineKeyboardButton("D12", callback_data='d12'), InlineKeyboardButton("D20", callback_data='d20')],
        [InlineKeyboardButton("<< Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text="Выберите, какую кость бросить:", reply_markup=reply_markup)

async def dice_roll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    dice = query.data
    sides = int(dice[1:])
    result = random.randint(1, sides)
    await query.edit_message_text(text=f"Бросок {dice.upper()}: **{result}**", parse_mode='Markdown')
    await show_main_menu(update, context, text="Готово! Что-нибудь еще?")
    return CHOOSING

# --- Обработчики ввода от пользователя ---
async def get_range_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        min_val, max_val = map(int, update.message.text.split())
        if min_val >= max_val:
            await update.message.reply_text("Минимальное значение должно быть меньше максимального. Попробуйте еще раз.")
            return GETTING_RANGE
        result = random.randint(min_val, max_val)
        await update.message.reply_text(f"Случайное число от {min_val} до {max_val}: **{result}**", parse_mode='Markdown')
    except (ValueError, IndexError):
        await update.message.reply_text("Неверный формат. Введите два числа через пробел (например, `1 100`).")
        return GETTING_RANGE

    await show_main_menu(update, context, text="Готово! Что-нибудь еще?")
    return CHOOSING

async def get_password_length_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        length = int(update.message.text)
        if not 8 <= length <= 128:
            await update.message.reply_text("Длина должна быть от 8 до 128. Попробуйте еще раз.")
            return GETTING_PASSWORD_LENGTH

        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        await update.message.reply_text(f"Ваш надежный пароль:\n`{password}`", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return GETTING_PASSWORD_LENGTH

    await show_main_menu(update, context, text="Готово! Что-нибудь еще?")
    return CHOOSING

async def get_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    items = [item.strip() for item in update.message.text.split('\n') if item.strip()]
    if len(items) < 2:
        await update.message.reply_text("Нужно как минимум два элемента в списке. Попробуйте еще раз.")
        return GETTING_LIST

    mode = context.user_data.get('list_mode')
    if mode == 'list_choice':
        result = random.choice(items)
        await update.message.reply_text(f"Я выбираю: **{result}**", parse_mode='Markdown')
    elif mode == 'list_shuffle':
        random.shuffle(items)
        result = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        await update.message.reply_text(f"Перемешанный список:\n{result}")

    await show_main_menu(update, context, text="Готово! Что-нибудь еще?")
    return CHOOSING

async def back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возвращает в главное меню."""
    await show_main_menu(update, context)
    return CHOOSING


def main() -> None:
    if not BOT_TOKEN:
        logger.error("Переменная окружения BOT_TOKEN не найдена!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(main_menu_handler, pattern='^(?!d[468]|d1[02]|d20|back_to_main$).*$'), # Все, кроме костей и назад
                CallbackQueryHandler(dice_roll_handler, pattern='^(d4|d6|d8|d10|d12|d20)$'),
                CallbackQueryHandler(back_to_main_handler, pattern='^back_to_main$')
            ],
            GETTING_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_range_handler)],
            GETTING_PASSWORD_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_length_handler)],
            GETTING_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_list_handler)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
