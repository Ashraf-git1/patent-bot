from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging

from variant_1 import questions as variant_1_questions

API_TOKEN = "ТВОЙ_ТОКЕН"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# состояние пользователя
user_data = {}


def get_keyboard(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        kb.add(KeyboardButton(opt))
    return kb


# 🚀 СТАРТ
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 Варианты")
    await msg.answer("Выбери раздел:", reply_markup=kb)


# 📚 ВАРИАНТЫ
@dp.message_handler(lambda m: m.text == "📚 Варианты")
async def variants(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 12):
        kb.add(str(i))
    kb.add("⬅️ Назад")

    await msg.answer("Выбери вариант:", reply_markup=kb)


# 🎯 ВЫБОР ВАРИАНТА
@dp.message_handler(lambda m: m.text == "1")
async def start_variant_1(msg: types.Message):
    user_data[msg.from_user.id] = {
        "variant": 1,
        "index": 0,
        "score": 0
    }
    await send_question(msg)


# 📩 ОТПРАВКА ВОПРОСА
async def send_question(msg: types.Message):
    data = user_data[msg.from_user.id]
    q = variant_1_questions[data["index"]]

    # аудио
    if q["type"] == "audio":
        if q.get("audio") and q["audio"]:
            with open(q["audio"], "rb") as audio:
                await bot.send_audio(msg.chat.id, audio)
        await msg.answer(q["text"], reply_markup=get_keyboard(q["options"]))

    elif q["type"] == "choice":
        await msg.answer(q["text"], reply_markup=get_keyboard(q["options"]))

    elif q["type"] == "input":
        await msg.answer(q["text"])


# ✅ ОБРАБОТКА ОТВЕТА
@dp.message_handler()
async def handle_answer(msg: types.Message):
    if msg.from_user.id not in user_data:
        return

    data = user_data[msg.from_user.id]
    q = variant_1_questions[data["index"]]

    answer = msg.text.strip().lower()
    correct = q["correct"].lower()

    if answer == correct:
        data["score"] += 1
        await msg.answer("✅ Правильно")
    else:
        await msg.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    data["index"] += 1

    if data["index"] >= len(variant_1_questions):
        await msg.answer(f"🎉 Завершено\nРезультат: {data['score']}/{len(variant_1_questions)}")
        user_data.pop(msg.from_user.id)
        return

    await send_question(msg)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
