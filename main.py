import asyncio
import urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from deep_translator import GoogleTranslator

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
CHANNEL_ID = "@pomocPolska" 
MY_ID = 541171874 # Твой ID для админ-кнопок

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Умная ссылка для заказа
def get_order_url():
    text = "Здравствуйте! Хочу заказать этот товар из канала @pomocPolska 🛍️"
    return f"{MY_PROFILE_URL}?text={urllib.parse.quote(text)}"

# ГЛАВНЫЕ КНОПКИ (Обычные)
def get_main_kb(is_sold=False):
    if is_sold:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ ПРОДАНО / SOLD", callback_data="none")],
            [InlineKeyboardButton(text="ℹ️ Info", callback_data="info_choose")]
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ ЗАКАЗАТЬ / ORDER", url=get_order_url())],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="translate_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="translate_pl")
        ],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info_choose")]
    ])

# АДМИН-КНОПКА (Добавляется только в твоем превью)
def get_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Опубликовать со статусом 'В наличии'", callback_data="admin_publish")]
    ])

# КНОПКА СМЕНЫ СТАТУСА (Видна в канале всем, но работает только для тебя)
def get_status_kb():
    kb = get_main_kb()
    kb.inline_keyboard.append([InlineKeyboardButton(text="✅ В наличии (Админ)", callback_data="admin_mark_sold")])
    return kb

# --- ОБРАБОТЧИКИ ---

@dp.message(F.chat.type == "private")
async def start_post(message: types.Message):
    # Добавляем оформление "Скидка дня", если есть ключевое слово
    text = message.text or message.caption or ""
    if any(word in text.lower() for word in ["скидка", "sale", "promocja"]):
        prefix = "🔥 ВНИМАНИЕ: СКИДКА ДНЯ! / SALE! 🔥\n\n"
        if message.text: message.text = prefix + message.text
        else: message.caption = prefix + message.caption

    await message.copy_to(chat_id=message.chat.id, reply_markup=get_admin_kb())

@dp.callback_query(F.data == "admin_publish")
async def publish_post(call: types.CallbackQuery):
    await call.message.copy_to(chat_id=CHANNEL_ID, reply_markup=get_status_kb())
    await call.answer("🚀 Опубликовано в канал!", show_alert=True)
    await call.message.delete()

@dp.callback_query(F.data == "admin_mark_sold")
async def mark_as_sold(call: types.CallbackQuery):
    if call.from_user.id != MY_ID:
        await call.answer("🔒 Это кнопка только для админа", show_alert=True)
        return
    
    await call.message.edit_reply_markup(reply_markup=get_main_kb(is_sold=True))
    await call.answer("✅ Статус изменен на 'ПРОДАНО'", show_alert=True)

# --- ПЕРЕВОД И INFO (Оставляем твою лучшую версию) ---

@dp.callback_query(F.data == "info_choose")
async def info_choose_lang(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 RU", callback_data="it_ru"),
         InlineKeyboardButton(text="🇵🇱 PL", callback_data="it_pl"),
         InlineKeyboardButton(text="🇬🇧 EN", callback_data="it_en")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])
    await call.message.edit_reply_markup(reply_markup=kb)

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=get_status_kb())

@dp.callback_query(F.data.startswith("it_"))
async def show_info(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    texts = {
        'ru': "ℹ️ ИНФОРМАЦИЯ\n📦 Отправка InPost — 24ч\n🤝 Встреча в Tczew — 24ч",
        'pl': "ℹ️ INFORMACJA\n📦 Wysyłka InPost — 24h\n🤝 Spotkanie w Tczewie — 24h",
        'en': "ℹ️ INFO\n📦 InPost shipping — 24h\n🤝 Meeting in Tczew — 24h"
    }
    await call.answer(text=texts.get(lang), show_alert=True)

@dp.callback_query(F.data.startswith("translate_"))
async def translate_post(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    original = call.message.text or call.message.caption or ""
    try:
        tr = GoogleTranslator(source='auto', target=lang).translate(original)
        await call.answer(text=f"📍 TRANSLATION:\n\n{tr}", show_alert=True)
    except:
        await call.answer("Error")

# --- SERVER ---
async def handle(r): return web.Response(text="Live")
async def main():
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
