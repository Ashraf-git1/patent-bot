print("БОТ ЗАПУЩЕН")

import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from config import TOKEN
from questions import questions

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

# =======================
# 🔹 ГЛАВНОЕ МЕНЮ
# =======================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Варианты")],
            [KeyboardButton(text="❌ Ошибки"), KeyboardButton(text="🎯 Экзамен")],
            [KeyboardButton(text="🎓 Обучение"), KeyboardButton(text="👨‍💬 Админу")]
        ],
        resize_keyboard=True
    )

# =======================
# 🔹 МЕНЮ ВАРИАНТОВ
# =======================
def variants_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1️⃣"), KeyboardButton(text="2️⃣"), KeyboardButton(text="3️⃣")],
            [KeyboardButton(text="4️⃣"), KeyboardButton(text="5️⃣"), KeyboardButton(text="6️⃣")],
            [KeyboardButton(text="7️⃣"), KeyboardButton(text="8️⃣"), KeyboardButton(text="9️⃣")],
            [KeyboardButton(text="🔟"), KeyboardButton(text="11")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

# =======================
# 🚀 START
# =======================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎓 Подготовка к патенту\n\nВыбери раздел:",
        reply_markup=main_menu()
    )

# =======================
# 📚 ВАРИАНТЫ
# =======================
@dp.message(lambda m: m.text == "📚 Варианты")
async def show_variants(message: types.Message):
    await message.answer("Выбери вариант:", reply_markup=variants_keyboard())

# =======================
# 🔙 НАЗАД
# =======================
@dp.message(lambda m: m.text == "⬅️ Назад")
async def back(message: types.Message):
    await start(message)

# =======================
# 🔢 ВЫБОР ВАРИАНТА (ПОКА ЗАГЛУШКА)
# =======================
@dp.message(lambda m: m.text in ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","11"])
async def variant_selected(message: types.Message):
    await message.answer(f"Ты выбрал вариант {message.text}\n(дальше подключим реальные вопросы)")

# =======================
# 🎯 ЭКЗАМЕН
# =======================
@dp.message(lambda m: m.text == "🎯 Экзамен")
async def exam(message: types.Message):

    exam_questions = random.sample(questions, min(5, len(questions)))

    users[message.from_user.id] = {
        "score": 0,
        "current": 0,
        "wrong": [],
        "mode": "exam",
        "exam_questions": exam_questions
    }

    await message.answer("🎯 Начинаем экзамен")
    await send_question(message)

# =======================
# ❌ ОШИБКИ
# =======================
@dp.message(lambda m: m.text == "❌ Ошибки")
async def errors(message: types.Message):
    user = users.get(message.from_user.id)

    if not user or not user["wrong"]:
        await message.answer("У тебя пока нет ошибок 👍")
        return

    user["current"] = 0
    user["mode"] = "wrong"

    await message.answer("🔁 Работаем над ошибками")
    await send_question(message)

# =======================
# 👨‍💬 АДМИНУ
# =======================
@dp.message(lambda m: m.text == "👨‍💬 Админу")
async def admin(message: types.Message):
    await message.answer("Напиши сюда: @your_username")

# =======================
# 🎓 ОБУЧЕНИЕ (ЗАГЛУШКА)
# =======================
@dp.message(lambda m: m.text == "🎓 Обучение")
async def study(message: types.Message):
    await message.answer("🔒 Скоро будет доступно")

# =======================
# ❓ ВЫДАЧА ВОПРОСА
# =======================
async def send_question(message: types.Message):
    user = users.get(message.from_user.id)

    if not user:
        await message.answer("Напиши /start")
        return

    if user["mode"] == "wrong":
        q_list = user["wrong"]
    elif user["mode"] == "exam":
        q_list = user["exam_questions"]
    else:
        q_list = questions

    if user["current"] >= len(q_list):
        await message.answer(f"🏁 Завершено\nРезультат: {user['score']}/{len(q_list)}")
        return

    q = q_list[user["current"]]

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=a)] for a in q["answers"]],
        resize_keyboard=True
    )

    await message.answer(q["question"], reply_markup=kb)

# =======================
# ✅ ОТВЕТ
# =======================
@dp.message()
async def answer(message: types.Message):
    user = users.get(message.from_user.id)

    if not user:
        return

    if user["mode"] == "wrong":
        q_list = user["wrong"]
    elif user["mode"] == "exam":
        q_list = user["exam_questions"]
    else:
        q_list = questions

    if user["current"] >= len(q_list):
        await message.answer("Тест завершён. Напиши /start")
        return

    q = q_list[user["current"]]

    if message.text == q["correct"]:
        user["score"] += 1
        await message.answer("✅ Правильно")
    else:
        user["wrong"].append(q)
        await message.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    user["current"] += 1
    await send_question(message)

# =======================
# 🚀 ЗАПУСК
# =======================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
