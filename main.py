

import os
import random
import string
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext: (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Настройка логирования для отладки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Определяем состояния для нашего диалога
(MAIN_MENU, GETTING_INPUT, SUB_MENU) = range(3)

# --- Главное меню ---

def get_main_menu_keyboard():
    """Возвращает клавиатуру главного меню."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Монетка", callback_data='coin_flip'), InlineKeyboardButton("👍 Да/Нет", callback_data='yes_no')],
        [InlineKeyboardButton("🎲 Кости", callback_data='dice_menu'), InlineKeyboardButton("🔢 Число", callback_data='random_number')],
        [InlineKeyboardButton("🎨 Цвет", callback_data='random_color'), InlineKeyboardButton("🔮 Шар 8", callback_data='magic_8_ball')],
        [InlineKeyboardButton("🃏 Карта", callback_data='random_card'), InlineKeyboardButton("🔒 Пароль", callback_data='password_generator')],
        [InlineKeyboardButton("🔀 Выбрать из списка", callback_data='list_choice')],
        [InlineKeyboardButton("🔄 Перемешать список", callback_data='list_shuffle')],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 Разделить на команды", callback_data='team_divider')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start. Отображает приветствие и главное меню."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я бот-рандомайзер. Выбери одну из опций ниже:",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возвращает пользователя в главное меню из подменю."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Выберите одну из опций ниже:", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

# --- Обработчики мгновенных действий ---

async def instant_tools_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает кнопки, которые дают мгновенный результат."""
    query = update.callback_query
    await query.answer()
    choice = query.data
    response = ""

    if choice == 'coin_flip':
        response = f"Выпало: **{random.choice(['Орёл 🦅', 'Решка 🪙'])}**"
    elif choice == 'yes_no':
        response = f"Ответ: **{random.choice(['Да 👍', 'Нет 👎'])}**"
    elif choice == 'random_color':
        r, g, b = [random.randint(0, 255) for _ in range(3)]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        response = f"Случайный цвет:\n`{hex_color}` | `rgb({r}, {g}, {b})`"
    elif choice == 'random_card':
        suits = ["♥️", "♦️", "♣️", "♠️"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        response = f"Случайная карта: **{random.choice(ranks)}{random.choice(suits)}**"
    elif choice == 'magic_8_ball':
        answers = ["Бесспорно", "Предрешено", "Никаких сомнений", "Определённо да", "Можешь быть уверен в этом", "Мне кажется — «да»", "Вероятнее всего", "Хорошие перспективы", "Знаки говорят — «да»", "Да", "Пока не ясно, попробуй снова", "Спроси позже", "Лучше не рассказывать", "Сейчас нельзя предсказать", "Сконцентрируйся и спроси опять", "Даже не думай", "Мой ответ — «нет»", "По моим данным — «нет»", "Перспективы не очень хорошие", "Весьма сомнительно"]
        response = f"🔮 Шар говорит: **{random.choice(answers)}**"

    # Отправляем ответ и заново показываем меню
    await query.message.reply_text(response, parse_mode='Markdown')
    return MAIN_MENU

# --- Обработчики действий, требующих ввода ---

async def input_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрашивает у пользователя ввод данных для выбранного инструмента."""
    query = update.callback_query
    await query.answer()
    tool = query.data
    context.user_data['tool'] = tool

    prompts = {
        'random_number': "Введите диапазон чисел в формате `мин макс` (например, `1 100`).",
        'password_generator': "Введите желаемую длину пароля (число от 8 до 128).",
        'list_choice': "Отправьте мне список элементов, каждый с новой строки.",
        'list_shuffle': "Отправьте мне список элементов, каждый с новой строки.",
        'team_divider': "Отправьте список имен (каждое с новой строки), а затем, через ДВЕ пустые строки, укажите желаемое количество команд.",
    }

    await query.edit_message_text(prompts[tool], parse_mode='Markdown')
    return GETTING_INPUT

async def input_process_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает введенные пользователем данные."""
    tool = context.user_data.get('tool')
    text = update.message.text
    response = ""

    try:
        if tool == 'random_number':
            min_val, max_val = map(int, text.split())
            if min_val >= max_val:
                raise ValueError("Минимальное значение должно быть меньше максимального.")
            response = f"Случайное число от {min_val} до {max_val}: **{random.randint(min_val, max_val)}**"

        elif tool == 'password_generator':
            length = int(text)
            if not 8 <= length <= 128:
                raise ValueError("Длина должна быть от 8 до 128.")
            chars = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(chars) for _ in range(length))
            response = f"Ваш надежный пароль:\n`{password}`"

        elif tool in ['list_choice', 'list_shuffle']:
            items = [item.strip() for item in text.split('\n') if item.strip()]
            if len(items) < 2:
                raise ValueError("Нужно как минимум два элемента в списке.")
            if tool == 'list_choice':
                response = f"Я выбираю: **{random.choice(items)}**"
            else:
                random.shuffle(items)
                response = "Перемешанный список:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

        elif tool == 'team_divider':
            parts = text.strip().split('\n\n')
            names = [name.strip() for name in parts[0].split('\n') if name.strip()]
            num_teams = int(parts[1].strip())
            if num_teams <= 1 or num_teams > len(names):
                raise ValueError("Количество команд должно быть больше 1 и не больше количества участников.")
            random.shuffle(names)
            teams = [[] for _ in range(num_teams)]
            for i, name in enumerate(names):
                teams[i % num_teams].append(name)
            result = [f"**Команда {i + 1}:**\n- " + "\n- ".join(team) for i, team in enumerate(teams)]
            response = "Разделение на команды завершено!\n\n" + "\n\n".join(result)

    except (ValueError, IndexError) as e:
        # Отправляем ошибку и просим ввести данные заново
        await update.message.reply_text(f"Ошибка: {e}\nПожалуйста, попробуйте еще раз.")
        return GETTING_INPUT # Остаемся в состоянии ожидания ввода

    # Отправляем результат и возвращаемся в главное меню
    await update.message.reply_text(response, parse_mode='Markdown')
    await start(update, context) # Показываем главное меню
    return ConversationHandler.END

# --- Подменю для игральных костей ---

async def dice_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает меню выбора игральных костей."""
    query = update.callback_query
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"D{s}", callback_data=f"d{s}") for s in [4, 6, 8]],
        [InlineKeyboardButton(f"D{s}", callback_data=f"d{s}") for s in [10, 12, 20]],
        [InlineKeyboardButton("<< Назад", callback_data='back_to_main')]
    ])
    await query.edit_message_text("Выберите, какую кость бросить:", reply_markup=keyboard)
    return SUB_MENU

async def dice_roll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает бросок кости."""
    query = update.callback_query
    await query.answer()
    sides = int(query.data[1:])
    response = f"Бросок D{sides}: **{random.randint(1, sides)}**"
    await query.message.reply_text(response, parse_mode='Markdown')
    # Не возвращаемся в главное меню, остаемся в подменю костей для повторных бросков
    return SUB_MENU

# --- Общие команды ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text("Это бот-рандомайзер. Используйте кнопки для выбора инструмента. /start для начала работы.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущий диалог и возвращает в главное меню."""
    await update.message.reply_text("Действие отменено.")
    await start(update, context)
    return ConversationHandler.END

def main() -> None:
    """Основная функция для запуска бота."""
    if not BOT_TOKEN:
        logger.error("Переменная окружения BOT_TOKEN не найдена!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Диалог, управляющий всеми состояниями бота
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                # Кнопки, которые дают мгновенный результат
                CallbackQueryHandler(instant_tools_handler, pattern='^(coin_flip|yes_no|random_color|random_card|magic_8_ball)$'),
                # Кнопки, которые требуют ввода от пользователя
                CallbackQueryHandler(input_request_handler, pattern='^(random_number|password_generator|list_choice|list_shuffle|team_divider)$'),
                # Кнопка для перехода в подменю костей
                CallbackQueryHandler(dice_menu_handler, pattern='^dice_menu$'),
            ],
            GETTING_INPUT: [
                # Обработчик текстового ввода от пользователя
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_process_handler)
            ],
            SUB_MENU: [
                # Обработчик кнопок в подменю (броски костей)
                CallbackQueryHandler(dice_roll_handler, pattern='^d(4|6|8|10|12|20)$'),
                # Кнопка для возврата в главное меню
                CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == '__main__':
    main()
