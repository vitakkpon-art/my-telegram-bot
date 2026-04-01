import asyncio
import urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from deep_translator import GoogleTranslator

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBG0NPe1gxS7X8wOJCNjrowIcpahhqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
CHANNEL_ID = "@pomocPolska"
MY_ID = 541171874 # Твой ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Умная ссылка: сообщение сразу на 3 языках
def get_universal_url():
    msg = "Привет! Хочу купить это / Hi! I want to buy this / Chcę это kupić 🛍️"
    return f"{MY_PROFILE_URL}?text={urllib.parse.quote(msg)}"

# Кнопки для публикации в канал
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ ЗАКАЗАТЬ / ORDER / ZAMÓW", url=get_universal_url())],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="alt_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="alt_pl"),
            InlineKeyboardButton(text="ℹ️ Info", callback_data="alt_info")
        ],
        [InlineKeyboardButton(text="✅ В наличии (Админ)", callback_data="admin_sold")]
    ])

# 1. ПОДГОТОВКА ПОСТА (В личке с ботом)
@dp.message(F.chat.type == "private")
async def draft_post(message: types.Message):
    text = message.text or message.caption or ""
    # Проверка на скидку
    if any(word in text.lower() for word in ["скидка", "sale", "promocja"]):
        prefix = "🔥 SALE / СКИДКА / PROMOCJA 🔥\n\n"
        if message.text: message.text = prefix + message.text
        else: message.caption = prefix + message.caption

    pub_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Опубликовать в канал", callback_data="confirm_pub")]
    ])
    await message.copy_to(chat_id=message.chat.id, reply_markup=pub_kb)

# 2. ПУБЛИКАЦИЯ
@dp.callback_query(F.data == "confirm_pub")
async def confirm_pub(call: types.CallbackQuery):
    await call.message.copy_to(chat_id=CHANNEL_ID, reply_markup=get_main_kb())
    await call.answer("Опубликовано в @pomocPolska!", show_alert=True)
    await call.message.delete()

# 3. ВСПЛЫВАЮЩИЕ ОКНА (ALERT) - Видит только нажавший
@dp.callback_query(F.data.startswith("alt_"))
async def handle_alerts(call: types.CallbackQuery):
    action = call.data.split('_')[1]
    
    if action == "info":
        info_text = (
            "🇷🇺 Отправка InPost / Tczew — 24ч\n"
            "🇵🇱 Wysyłka InPost / Tczew — 24h\n"
            "🇬🇧 Shipping InPost / Tczew — 24h"
        )
        await call.answer(text=info_text, show_alert=True)
        return

    # Для перевода
    original = call.message.text or call.message.caption or ""
    try:
        translated = GoogleTranslator(source='auto', target=action).translate(original)
        await call.answer(text=f"📍 {action.upper()}:\n\n{translated}", show_alert=True)
    except:
        await call.answer("Translation error", show_alert=True)

# 4. СТАТУС ПРОДАНО
@dp.callback_query(F.data == "admin_sold")
async def process_sold(call: types.CallbackQuery):
    if call.from_user.id != MY_ID:
        await call.answer("Только для админа 🔒", show_alert=True)
        return
    
    sold_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ПРОДАНО / SOLD / SPRZEDANE", callback_data="none")]
    ])
    await call.message.edit_reply_markup(reply_markup=sold_kb)
    await call.answer("Товар помечен как проданный!", show_alert=True)

# --- SERVER PART ---
async def handle(r): return web.Response(text="Live")
async def main():
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
