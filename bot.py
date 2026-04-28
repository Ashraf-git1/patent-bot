from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging
import os


from variant_1 import questions as variant_1_questions

API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}


# ================== КЛАВИАТУРЫ ==================

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 Варианты")
    kb.add("❌ Ошибки", "🎯 Экзамен")
    kb.add("🎓 Обучение", "👨‍💻 Админу")
    return kb


def variants_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 12):
        kb.add(str(i))
    kb.add("⬅️ Назад", "🏠 В меню")
    return kb


def answer_keyboard(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        kb.add(opt)
    kb.add("⬅️ Назад", "🏠 В меню")
    return kb


# ================== СТАРТ ==================

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("🏠 Главное меню:", reply_markup=main_menu())


# ================== ГЛАВНОЕ МЕНЮ ==================

@dp.message_handler(lambda m: m.text == "🏠 В меню")
async def to_menu(msg: types.Message):
    user_data.pop(msg.from_user.id, None)
    await msg.answer("🏠 Главное меню:", reply_markup=main_menu())


# ================== ВАРИАНТЫ ==================

@dp.message_handler(lambda m: m.text == "📚 Варианты")
async def variants(msg: types.Message):
    await msg.answer("Выбери вариант:", reply_markup=variants_menu())


@dp.message_handler(lambda m: m.text == "⬅️ Назад")
async def back(msg: types.Message):
    user_data.pop(msg.from_user.id, None)
    await msg.answer("📚 Варианты:", reply_markup=variants_menu())


# ================== СТАРТ ВАРИАНТА 1 ==================

@dp.message_handler(lambda m: m.text == "1")
async def start_variant_1(msg: types.Message):
    user_data[msg.from_user.id] = {
        "variant": 1,
        "index": 0,
        "score": 0
    }
    await msg.answer("📘 Вариант 1 начат")
    await send_question(msg)


# ================== ОТПРАВКА ВОПРОСА ==================

async def send_question(msg: types.Message):
    data = user_data[msg.from_user.id]
    q = variant_1_questions[data["index"]]

    # аудио
    if q["type"] == "audio":
        if q.get("audio"):
            try:
                with open(q["audio"], "rb") as audio:
                    await bot.send_audio(msg.chat.id, audio)
            except:
                await msg.answer("⚠️ Ошибка аудио")

        await msg.answer(q["text"], reply_markup=answer_keyboard(q["options"]))

    # выбор
    elif q["type"] == "choice":
        await msg.answer(q["text"], reply_markup=answer_keyboard(q["options"]))

    # ввод текста
    elif q["type"] == "input":
        await msg.answer(q["text"] + "\n✍️ Напиши ответ текстом", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Назад", "🏠 В меню"))


# ================== ОБРАБОТКА ОТВЕТОВ ==================

@dp.message_handler()
async def handle_answer(msg: types.Message):
    if msg.from_user.id not in user_data:
        return

    # выход
    if msg.text in ["⬅️ Назад", "🏠 В меню"]:
        return

    data = user_data[msg.from_user.id]
    q = variant_1_questions[data["index"]]

    user_answer = msg.text.strip().lower()
    correct_answer = q["correct"].strip().lower()

    if user_answer == correct_answer:
        data["score"] += 1
        await msg.answer("✅ Правильно")
    else:
        await msg.answer(f"❌ Неправильно\nПравильный: {q['correct']}")

    data["index"] += 1

    # конец теста
    if data["index"] >= len(variant_1_questions):
        await msg.answer(f"🎉 Завершено\nРезультат: {data['score']}/{len(variant_1_questions)}", reply_markup=main_menu())
        user_data.pop(msg.from_user.id)
        return

    await send_question(msg)


# ================== ЗАПУСК ==================

if __name__ == "__main__":
    print("🚀 БОТ ЗАПУЩЕН")
    executor.start_polling(dp, skip_updates=True)
