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
MY_ID = 541171874

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция создания ссылки для заказа (текст зависит от языка)
def get_order_url(lang='ru'):
    messages = {
        'pl': "Dzień dobry! Chcę zamówić ten przedmiot z kanału @pomocPolska 🛍️",
        'en': "Hello! I want to order this item from @pomocPolska channel 🛍️",
        'ru': "Здравствуйте! Хочу заказать этот товар из канала @pomocPolska 🛍️"
    }
    msg = messages.get(lang, messages['ru'])
    return f"{MY_PROFILE_URL}?text={urllib.parse.quote(msg)}"

# Кнопки, которые всегда висят в канале (НЕ МЕНЯЮТСЯ)
def get_static_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ ЗАКАЗАТЬ / ORDER / ZAMÓW", url=get_order_url('ru'))],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info_start")]
    ])

# 1. ПУБЛИКАЦИЯ (Админ-логика)
@dp.message(F.chat.type == "private")
async def start_post(message: types.Message):
    # Проверка на скидку
    text = message.text or message.caption or ""
    if any(word in text.lower() for word in ["скидка", "sale", "promocja"]):
        prefix = "🔥 SALE / СКИДКА / PROMOCJA 🔥\n\n"
        if message.text: message.text = prefix + message.text
        else: message.caption = prefix + message.caption

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Опубликовать в канал", callback_data="publish")]
    ])
    await message.copy_to(chat_id=message.chat.id, reply_markup=admin_kb)

@dp.callback_query(F.data == "publish")
async def publish(call: types.CallbackQuery):
    # Добавляем кнопку "Продано", которую видишь только ты (проверка по ID позже)
    kb = get_static_kb()
    kb.inline_keyboard.append([InlineKeyboardButton(text="✅ В наличии (Админ)", callback_data="mark_sold")])
    await call.message.copy_to(chat_id=CHANNEL_ID, reply_markup=kb)
    await call.answer("Опубликовано!")
    await call.message.delete()

# 2. ОБРАБОТКА ЯЗЫКА (ПЕРСОНАЛЬНО ДЛЯ ЮЗЕРА)
@dp.callback_query(F.data.startswith("lang_"))
async def handle_lang(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    original = call.message.text or call.message.caption or ""
    
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(original)
        btn_text = "🛍️ ZAMÓW TERAZ" if lang == 'pl' else "🛍️ ORDER NOW"
        
        # Создаем ПЕРСОНАЛЬНУЮ клавиатуру для всплывающего сообщения
        user_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn_text, url=get_order_url(lang))]
        ])
        
        # Бот отвечает пользователю ЛИЧНЫМ сообщением, которое не видит канал
        # Или можно использовать Alert, но в Alert нельзя вставить кнопку. 
        # Поэтому мы отправляем перевод в ЛИЧКУ пользователю.
        await bot.send_message(
            chat_id=call.from_user.id, 
            text=f"📍 {lang.upper()} VERSION:\n\n{translated}", 
            reply_markup=user_kb
        )
        await call.answer("✅ Перевод отправлен вам в личные сообщения!", show_alert=True)
    except:
        await call.answer("Ошибка перевода / Error", show_alert=True)

# 3. СТАТУС ПРОДАНО (Только для тебя)
@dp.callback_query(F.data == "mark_sold")
async def mark_sold(call: types.CallbackQuery):
    if call.from_user.id != MY_ID:
        await call.answer("Это кнопка для администратора 🔒", show_alert=True)
        return
    
    sold_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ПРОДАНО / SOLD / SPRZEDANE", callback_data="none")]
    ])
    await call.message.edit_reply_markup(reply_markup=sold_kb)
    await call.answer("Статус обновлен!")

# --- СТАНДАРТНЫЙ ЗАПУСК ---
async def handle(r): return web.Response(text="Live")
async def main():
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
