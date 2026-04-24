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
            [types.KeyboardButton(text="🎓 Обучение")],
            [types.KeyboardButton(text="👨‍💻 Админу")]
        ],
        resize_keyboard=True
    )

def variants_menu():
    buttons = []
    for i in range(1, 12):
        buttons.append([types.KeyboardButton(text=str(i))])
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ---------- START ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    users[message.from_user.id] = {
        "score": 0,
        "current": 0,
        "wrong": [],
        "mode": None,
        "questions": []
    }
    await message.answer("📚 Подготовка к патенту\nВыбери раздел:", reply_markup=main_menu())


# ---------- МЕНЮ ----------
@dp.message(lambda m: m.text == "📚 Варианты")
async def choose_variant(message: types.Message):
    await message.answer("Выбери вариант:", reply_markup=variants_menu())


@dp.message(lambda m: m.text.isdigit())
async def start_variant(message: types.Message):
    user = users.get(message.from_user.id)

    variant = int(message.text)

    if variant not in questions:
        return

    user["mode"] = "variant"
    user["questions"] = questions[variant]
    user["current"] = 0
    user["score"] = 0
    user["wrong"] = []

    await message.answer(f"Ты выбрал вариант {variant}")
    await send_question(message)


# ---------- ЭКЗАМЕН ----------
@dp.message(lambda m: m.text == "🎯 Экзамен")
async def exam(message: types.Message):
    user = users.get(message.from_user.id)

    all_questions = []
    for v in questions.values():
        all_questions.extend(v)

    user["mode"] = "exam"
    user["questions"] = random.sample(all_questions, min(10, len(all_questions)))
    user["current"] = 0
    user["score"] = 0
    user["wrong"] = []

    await message.answer("🎯 Начинаем экзамен")
    await send_question(message)


# ---------- ОШИБКИ ----------
@dp.message(lambda m: m.text == "❌ Ошибки")
async def errors(message: types.Message):
    user = users.get(message.from_user.id)

    if not user["wrong"]:
        await message.answer("У тебя нет ошибок 👍")
        return

    text = "Твои ошибки:\n\n"
    for q in user["wrong"]:
        text += f"{q['question']}\nПравильный: {q['correct']}\n\n"

    await message.answer(text)


# ---------- ОБУЧЕНИЕ ----------
@dp.message(lambda m: m.text == "🎓 Обучение")
async def learn(message: types.Message):
    await message.answer("🔒 Скоро будет доступно")


# ---------- АДМИН ----------
@dp.message(lambda m: m.text == "👨‍💻 Админу")
async def admin(message: types.Message):
    await message.answer("Напиши сюда: @your_username")


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

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=a)] for a in q["options"]],
        resize_keyboard=True
    )

    await message.answer(q["question"], reply_markup=keyboard)


# ---------- ОТВЕТ ----------
@dp.message()
async def answer(message: types.Message):
    user = users.get(message.from_user.id)

    if not user or not user["questions"]:
        return

    q = user["questions"][user["current"]]

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
