import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

from variant_1 import questions

API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

# ===== КНОПКИ =====

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 Варианты")
    kb.add("❌ Ошибки", "🎯 Экзамен")
    kb.add("🎓 Обучение", "👨‍💻 Админу")
    return kb

def answer_kb(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        kb.add(opt)
    kb.add("⬅️ Назад", "🏠 В меню")
    return kb

# ===== СТАРТ =====

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("🏠 Главное меню", reply_markup=main_menu())

# ===== МЕНЮ =====

@dp.message_handler(lambda m: m.text == "🏠 В меню")
async def menu(msg: types.Message):
    user_data.pop(msg.from_user.id, None)
    await msg.answer("🏠 Главное меню", reply_markup=main_menu())

@dp.message_handler(lambda m: m.text == "📚 Варианты")
async def variants(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1")
    kb.add("⬅️ Назад", "🏠 В меню")
    await msg.answer("Выбери вариант", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "⬅️ Назад")
async def back(msg: types.Message):
    await msg.answer("🏠 Главное меню", reply_markup=main_menu())

# ===== СТАРТ ВАРИАНТА =====

@dp.message_handler(lambda m: m.text == "1")
async def start_test(msg: types.Message):
    user_data[msg.from_user.id] = {"i": 0, "score": 0}
    await send_q(msg)

# ===== ВОПРОС =====

async def send_q(msg):
    data = user_data[msg.from_user.id]
    q = questions[data["i"]]

    if q["type"] == "audio":
        try:
            await bot.send_audio(msg.chat.id, open(q["audio"], "rb"))
        except:
            pass

    if q["type"] == "image":
        for img in q["images"]:
            await bot.send_photo(msg.chat.id, img["url"])
        options = [i["text"] for i in q["images"]]
    else:
        options = q.get("options", [])

    await msg.answer(q["text"], reply_markup=answer_kb(options))

# ===== ОТВЕТ =====

@dp.message_handler()
async def answer(msg: types.Message):
    if msg.from_user.id not in user_data:
        return

    if msg.text in ["⬅️ Назад", "🏠 В меню"]:
        return

    data = user_data[msg.from_user.id]
    q = questions[data["i"]]

    if msg.text.lower() == q["correct"].lower():
        data["score"] += 1
        await msg.answer("✅")
    else:
        await msg.answer(f"❌ Правильный: {q['correct']}")

    data["i"] += 1

    if data["i"] >= len(questions):
        await msg.answer(f"🎉 Результат: {data['score']}/{len(questions)}")
        user_data.pop(msg.from_user.id)
        await msg.answer("🏠 Главное меню", reply_markup=main_menu())
        return

    await send_q(msg)

# ===== ЗАПУСК =====

if __name__ == "__main__":
    print("🚀 БОТ ЗАПУЩЕН")
    executor.start_polling(dp, skip_updates=True)
