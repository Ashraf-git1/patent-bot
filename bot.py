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

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):
    users[message.from_user.id] = {
        "score": 0,
        "current": 0,
        "wrong": [],
        "mode": "all"
    }

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Тренировка")],
            [KeyboardButton(text="❌ Ошибки")],
            [KeyboardButton(text="🎯 Экзамен")]
        ],
        resize_keyboard=True
    )

    await message.answer("Выбери режим:", reply_markup=kb)


# 📚 ТРЕНИРОВКА
@dp.message(lambda message: message.text == "📚 Тренировка")
async def training(message: types.Message):
    users[message.from_user.id] = {
        "score": 0,
        "current": 0,
        "wrong": [],
        "mode": "all"
    }
    await test(message)


# ❌ ОШИБКИ
@dp.message(lambda message: message.text == "❌ Ошибки")
async def wrong_answers(message: types.Message):
    user = users.get(message.from_user.id)

    if not user or not user["wrong"]:
        await message.answer("У тебя нет ошибок 👍")
        return

    user["current"] = 0
    user["mode"] = "wrong"

    await message.answer("🔁 Работаем над ошибками")
    await test(message)


# 🎯 ЭКЗАМЕН
@dp.message(lambda message: message.text == "🎯 Экзамен")
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
    await test(message)


# ❓ ВЫДАЧА ВОПРОСА
@dp.message(Command("test"))
async def test(message: types.Message):
    user = users.get(message.from_user.id)

    if not user:
        await message.answer("Напиши /start")
        return

    # выбор режима
    if user["mode"] == "wrong":
        q_list = user["wrong"]
    elif user["mode"] == "exam":
        q_list = user["exam_questions"]
    else:
        q_list = questions

    # конец теста
    if user["current"] >= len(q_list):
        if user["mode"] == "exam":
            if user["score"] >= len(q_list) - 1:
                await message.answer(f"🎯 Экзамен СДАН\nРезультат: {user['score']}/{len(q_list)}")
            else:
                await message.answer(f"❌ Экзамен НЕ сдан\nРезультат: {user['score']}/{len(q_list)}")
        else:
            await message.answer(f"🏁 Завершено\nПравильно: {user['score']}/{len(q_list)}")
        return

    q = q_list[user["current"]]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=a)] for a in q["answers"]],
        resize_keyboard=True
    )

    await message.answer(q["question"], reply_markup=keyboard)


# ✅ ОТВЕТ
@dp.message()
async def answer(message: types.Message):
    user = users.get(message.from_user.id)

    if not user:
        await message.answer("Напиши /start")
        return

    # выбор режима
    if user["mode"] == "wrong":
        q_list = user["wrong"]
    elif user["mode"] == "exam":
        q_list = user["exam_questions"]
    else:
        q_list = questions

    # защита от ошибки
    if user["current"] >= len(q_list):
        await message.answer("🏁 Тест уже завершён. Напиши /start")
        return

    q = q_list[user["current"]]

    if message.text == q["correct"]:
        user["score"] += 1
        await message.answer("✅ Правильно")
    else:
        user["wrong"].append(q)
        await message.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    user["current"] += 1
    await test(message)


# 🚀 ЗАПУСК
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())