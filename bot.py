print("БОТ ЗАПУЩЕН")

import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TOKEN
from questions import questions

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

# ---------- МЕНЮ ----------
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📚 Варианты")],
            [types.KeyboardButton(text="❌ Ошибки"), types.KeyboardButton(text="🎯 Экзамен")],
            [types.KeyboardButton(text="🏠 В меню")]
        ],
        resize_keyboard=True
    )

def variants_menu():
    buttons = []
    for i in range(1, 12):
        buttons.append([types.KeyboardButton(text=str(i))])
    buttons.append([types.KeyboardButton(text="🏠 В меню")])
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ---------- START ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    users[message.from_user.id] = {
        "score": 0,
        "current": 0,
        "wrong": [],
        "questions": []
    }
    await message.answer("📚 Подготовка к патенту", reply_markup=main_menu())

# ---------- МЕНЮ ----------
@dp.message(lambda m: m.text == "🏠 В меню")
async def back_to_menu(message: types.Message):
    await message.answer("Главное меню", reply_markup=main_menu())

@dp.message(lambda m: m.text == "📚 Варианты")
async def choose_variant(message: types.Message):
    await message.answer("Выбери вариант:", reply_markup=variants_menu())

# ---------- ВАРИАНТ ----------
@dp.message(lambda m: m.text.isdigit())
async def start_variant(message: types.Message):
    user = users.get(message.from_user.id)

    variant = int(message.text)

    if variant not in questions:
        return

    user["questions"] = questions[variant]
    user["current"] = 0
    user["score"] = 0
    user["wrong"] = []

    await message.answer(f"Вариант {variant} начат")
    await send_question(message)

# ---------- ВОПРОС ----------
async def send_question(message):
    user = users.get(message.from_user.id)

    if user["current"] >= len(user["questions"]):
        await message.answer(
            f"🏁 Завершено\nРезультат: {user['score']}/{len(user['questions'])}",
            reply_markup=main_menu()
        )
        return

    q = user["questions"][user["current"]]

    if q["type"] == "choice":
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=a)] for a in q["options"]] + [[types.KeyboardButton(text="🏠 В меню")]],
            resize_keyboard=True
        )
        await message.answer(q["question"], reply_markup=keyboard)

    elif q["type"] == "input":
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="🏠 В меню")]],
            resize_keyboard=True
        )
        await message.answer(q["question"] + "\n\n✍️ Напиши ответ текстом", reply_markup=keyboard)

# ---------- ОТВЕТ ----------
@dp.message()
async def answer(message: types.Message):
    user = users.get(message.from_user.id)

    if not user or not user["questions"]:
        return

    q = user["questions"][user["current"]]

    # INPUT
    if q["type"] == "input":
        if message.text.lower() == q["correct"].lower():
            user["score"] += 1
            await message.answer("✅ Правильно")
        else:
            user["wrong"].append(q)
            await message.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    # CHOICE
    elif q["type"] == "choice":
        if message.text == q["correct"]:
            user["score"] += 1
            await message.answer("✅ Правильно")
        else:
            user["wrong"].append(q)
            await message.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    user["current"] += 1
    await send_question(message)

# ---------- ЗАПУСК ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
