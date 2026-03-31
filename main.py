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

# Главные кнопки
def get_main_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Заказать / Order / Zamów", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="translate_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="translate_pl")
        ],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info_ru")] # По умолчанию RU
    ])

@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_main_buttons(), parse_mode="HTML")
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_main_buttons(), parse_mode="HTML")
        await message.answer("✅ Готово! Кнопка Info теперь переводит.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# Перевод текста поста
@dp.callback_query(F.data.startswith("translate_"))
async def handle_translation(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    original_text = call.message.text or call.message.caption or ""
    
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(original_text)
        header = "🇬🇧 ENGLISH" if lang == 'en' else "🇵🇱 POLSKI"
        
        # Обновляем кнопки под постом, чтобы Info вела на нужный язык
        new_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Order / Zamów", url=MY_PROFILE_URL)],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="translate_en"),
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="translate_pl")
            ],
            [InlineKeyboardButton(text="ℹ️ Info", callback_data=f"info_{lang}")]
        ])

        full_text = f"📍 {header}\n──────────────\n\n{translated}\n\n───── ⚡️ ─────\n👨‍💻 Contact: @Nygmad"
        await call.answer(text=full_text, show_alert=True)
    except:
        await call.answer("Error", show_alert=True)

# Обработка Info на разных языках
@dp.callback_query(F.data.startswith("info_"))
async def handle_info(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    
    if lang == 'pl':
        text = "ℹ️ INFORMACJA\n──────────────\n📦 Wysyłka InPost - do 24h\n🤝 Spotkanie w Tczewie - do 24h"
    elif lang == 'en':
        text = "ℹ️ INFORMATION\n──────────────\n📦 InPost shipping - up to 24h\n🤝 Meeting in Tczew - up to 24h"
    else:
        text = "ℹ️ ИНФОРМАЦИЯ\n──────────────\n📦 Отправка InPost - до 24ч\n🤝 Встреча в Tczew - до 24ч"
        
    await call.answer(text=text, show_alert=True)

async def handle(request): return web.Response(text="Live")
async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
