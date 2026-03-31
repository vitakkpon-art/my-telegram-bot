import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from deep_translator import GoogleTranslator

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
CHANNEL_ID = "@pomocPolska" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Теперь у нас один постоянный набор кнопок
def get_main_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Заказать / Order / Zamów", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="translate_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="translate_pl")
        ],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info_all")]
    ])

# --- ОБРАБОТЧИКИ ---

@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_main_buttons(), parse_mode="HTML")
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_main_buttons(), parse_mode="HTML")
        await message.answer("✅ Пост опубликован! Теперь перевод работает в личных окнах.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ОБРАБОТКА ПЕРЕВОДА (Всплывающее окно)
@dp.callback_query(F.data.startswith("translate_"))
async def handle_translation(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    original_text = call.message.text or call.message.caption or ""
    
    if not original_text:
        await call.answer("❕ Текст не найден", show_alert=True)
        return

    header = "🇬🇧 ENGLISH VERSION" if lang == 'en' else "🇵🇱 POLSKA WERSJA"
    
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(original_text)
        full_text = (
            f"📍 {header}\n"
            f"────────────────\n\n"
            f"{translated}\n\n"
            f"───── ⚡️ ─────\n"
            f"👨‍💻 Contact: @Nygmad"
        )
        # show_alert=True гарантирует, что окно будет большим и личным
        await call.answer(text=full_text, show_alert=True)
    except:
        await call.answer("⚠️ Ошибка перевода. Попробуйте еще раз.", show_alert=True)

# ОБРАБОТКА ИНФО (Сразу на всех языках в одном окне)
@dp.callback_query(F.data == "info_all")
async def handle_info(call: types.CallbackQuery):
    info_text = (
        "ℹ️ INFO / ИНФОРМАЦИЯ\n"
        "────────────────\n\n"
        "🇷🇺 Доставка InPost - до 24ч\n"
        "🇷🇺 Встреча в Tczew - до 24ч\n\n"
        "🇵🇱 Dostawa InPost - do 24h\n"
        "🇵🇱 Spotkanie w Tczewie - do 24h\n\n"
        "🇬🇧 InPost delivery - up to 24h\n"
        "🇬🇧 Meeting in Tczew - up to 24h"
    )
    await call.answer(text=info_text, show_alert=True)

# Запуск сервера и бота
async def handle(request): return web.Response(text="Live")
async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
