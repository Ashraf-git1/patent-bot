from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging
import os

from variant_1 import questions

API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}


# ===== КЛАВИАТУРЫ =====

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 Вариант 1")
    return kb


def answer_kb(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        kb.add(opt)
    return kb


# ===== СТАРТ =====

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("Выбери вариант:", reply_markup=main_menu())


@dp.message_handler(lambda m: m.text == "📚 Вариант 1")
async def start_test(msg: types.Message):
    user_data[msg.from_user.id] = {
        "index": 0,
        "score": 0
    }
    await send_question(msg)


# ===== ВОПРОС =====

async def send_question(msg: types.Message):
    data = user_data[msg.from_user.id]
    q = questions[data["index"]]

    # АУДИО
    if q["type"] == "audio":
        try:
            await bot.send_audio(msg.chat.id, open(q["audio"], "rb"))
        except:
            await msg.answer("❌ Ошибка аудио")

        await msg.answer(q["text"], reply_markup=answer_kb(q["options"]))

    # ФЛАГ (картинка)
    elif q["type"] == "image":
        for img in q["images"]:
            await bot.send_photo(msg.chat.id, img["url"], caption=img["text"])

        await msg.answer(q["text"], reply_markup=answer_kb([i["text"] for i in q["images"]]))

    # ОБЫЧНЫЙ ВОПРОС
    else:
        await msg.answer(q["text"], reply_markup=answer_kb(q["options"]))


# ===== ОТВЕТ =====

@dp.message_handler()
async def handle_answer(msg: types.Message):
    if msg.from_user.id not in user_data:
        return

    data = user_data[msg.from_user.id]
    q = questions[data["index"]]

    user = msg.text.strip().lower()
    correct = q["correct"].lower()

    if user == correct:
        data["score"] += 1
        await msg.answer("✅ Правильно")
    else:
        await msg.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    data["index"] += 1

    if data["index"] >= len(questions):
        await msg.answer(f"🎉 Результат: {data['score']}/{len(questions)}")
        user_data.pop(msg.from_user.id)
        return

    await send_question(msg)


# ===== ЗАПУСК =====

if __name__ == "__main__":
    print("🚀 БОТ ЗАПУЩЕН")
    executor.start_polling(dp, skip_updates=True)
