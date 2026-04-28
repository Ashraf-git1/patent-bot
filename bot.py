import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# СОСТОЯНИЕ ПОЛЬЗОВАТЕЛЯ
# =========================
users = {}

# =========================
# КНОПКИ
# =========================
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Варианты")],
        [KeyboardButton(text="🎯 Экзамен")]
    ],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="🏠 В меню")]
    ],
    resize_keyboard=True
)

# =========================
# ВОПРОСЫ 1 ВАРИАНТА
# =========================
variant_1 = [
    {"q": "1. Они говорят", "a": ["в центре тестирования", "в магазине"], "correct": "в центре тестирования"},
    {"q": "2. С собой необходимо иметь", "a": ["миграционную карту", "паспорт"], "correct": "миграционную карту"},
    
    # АУДИО
    {"q": "3. Прослушайте аудио", "audio": "assets/audio/1-1.mp3", "a": ["вариант 1", "вариант 2"], "correct": "вариант 1"},
    {"q": "4. Прослушайте аудио", "audio": "assets/audio/1-1.mp3", "a": ["ответ 1", "ответ 2"], "correct": "ответ 2"},

    {"q": "5. Где он работает?", "a": ["на стройке", "в офисе"], "correct": "на стройке"},
    {"q": "6. Сколько стоит билет?", "a": ["100 рублей", "200 рублей"], "correct": "100 рублей"},

    # ТЕКСТ
    {"q": "7. Обзор Набиев приехал в Россию из Узбекистана. Он грузчик.\nКто вы по профессии?", "text": True, "correct": "грузчик"},

    {"q": "8. Где вы живёте?", "a": ["в Москве", "в Самаре"], "correct": "в Москве"},
    {"q": "9. Когда вы приехали?", "a": ["вчера", "сегодня"], "correct": "сегодня"},
    {"q": "10. Что вы делаете?", "a": ["работаю", "отдыхаю"], "correct": "работаю"},
    {"q": "11. Мы приехали в Россию, ___ здесь есть работа.", "a": ["потому что", "поэтому"], "correct": "потому что"},

    {"q": "12. День Победы", "a": ["9 мая", "4 ноября"], "correct": "9 мая"},

    {"q": "13. Столица РФ", "a": ["Москва", "Екатеринбург"], "correct": "Москва"},

    # ПРОБЛЕМНЫЙ ВОПРОС — ТУТ ВСЁ НОРМАЛЬНО СДЕЛАНО
    {"q": "14. Война закончилась", "a": ["1945", "1917", "1980"], "correct": "1945"},

    # ФЛАГ
    {"q": "15. Какая это страна?", "photo": "assets/flags/ru.png", "a": ["Россия", "Казахстан"], "correct": "Россия"},

    {"q": "16. Где находится Кремль?", "a": ["Москва", "Питер"], "correct": "Москва"},
    {"q": "17. Президент РФ", "a": ["Путин", "Байден"], "correct": "Путин"},
    {"q": "18. Столица Узбекистана", "a": ["Ташкент", "Самарканд"], "correct": "Ташкент"},
    {"q": "19. Валюта РФ", "a": ["рубль", "доллар"], "correct": "рубль"},
    {"q": "20. Сколько дней в неделе?", "a": ["7", "5"], "correct": "7"},
    {"q": "21. Какой сегодня день?", "a": ["понедельник", "вторник"], "correct": "понедельник"},
    {"q": "22. Вы работаете?", "a": ["да", "нет"], "correct": "да"},
]

# =========================
# СТАРТ
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🏠 Главное меню", reply_markup=menu_kb)

# =========================
# ВАРИАНТЫ
# =========================
@dp.message(F.text == "📚 Варианты")
async def variants_menu(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(i)) for i in range(1, 6)],
                  [KeyboardButton(text=str(i)) for i in range(6, 12)],
                  [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="🏠 В меню")]],
        resize_keyboard=True
    )
    await message.answer("Выбери вариант:", reply_markup=kb)

# =========================
# СТАРТ ВАРИАНТА
# =========================
@dp.message(F.text.in_([str(i) for i in range(1, 12)]))
async def start_variant(message: Message):
    user_id = message.from_user.id

    users[user_id] = {
        "q": 0,
        "score": 0,
        "data": variant_1
    }

    await message.answer(f"Вариант {message.text} начат")
    await send_question(message, user_id)

# =========================
# ОТПРАВКА ВОПРОСА
# =========================
async def send_question(message: Message, user_id):
    user = users[user_id]
    questions = user["data"]

    if user["q"] >= len(questions):
        await message.answer(f"🏁 Завершено\nРезультат: {user['score']}/{len(questions)}", reply_markup=menu_kb)
        return

    q = questions[user["q"]]

    # аудио
    if "audio" in q:
        await message.answer_audio(FSInputFile(q["audio"]))

    # фото
    if "photo" in q:
        await message.answer_photo(FSInputFile(q["photo"]))

    # текстовый вопрос
    if q.get("text"):
        await message.answer(q["q"] + "\n✍️ Напиши ответ", reply_markup=back_kb)
        return

    # кнопки
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=ans)] for ans in q["a"]] +
                 [[KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="🏠 В меню")]],
        resize_keyboard=True
    )

    await message.answer(q["q"], reply_markup=kb)

# =========================
# ОБРАБОТКА ОТВЕТА
# =========================
@dp.message()
async def handle_answer(message: Message):
    user_id = message.from_user.id

    if message.text == "🏠 В меню":
        await message.answer("🏠 Главное меню", reply_markup=menu_kb)
        return

    if user_id not in users:
        return

    user = users[user_id]
    questions = user["data"]

    if user["q"] >= len(questions):
        return

    q = questions[user["q"]]
    answer = message.text.lower().strip()

    correct = q["correct"].lower()

    if answer == correct:
        user["score"] += 1
        await message.answer("✅ Правильно")
    else:
        await message.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    user["q"] += 1
    await send_question(message, user_id)

# =========================
# ЗАПУСК
# =========================
async def main():
    print("БОТ ЗАПУЩЕН")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
