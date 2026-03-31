import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from deep_translator import GoogleTranslator # Новый надежный переводчик

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
CHANNEL_ID = "@pomocPolska" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Купить / Buy / Kupić", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ]
    ])

@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_buttons())
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_buttons())
        await message.answer("✅ Опубликовано!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.callback_query(F.data.startswith("lang_"))
async def show_translation(call: types.CallbackQuery):
    original_text = call.message.text or call.message.caption or ""
    if not original_text:
        await call.answer("Текст не найден", show_alert=True)
        return

    target_lang = 'en' if call.data == "lang_en" else 'pl'
    
    try:
        # Новый способ перевода
        translated = GoogleTranslator(source='auto', target=target_lang).translate(original_text)
        await call.answer(text=f"Перевод:\n\n{translated}", show_alert=True)
    except Exception as e:
        await call.answer(f"Ошибка перевода: {e}", show_alert=True)

async def handle(request): return web.Response(text="Live")
async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
