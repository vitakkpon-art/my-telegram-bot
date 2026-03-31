import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
CHANNEL_ID = "@pomocPolska" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Кнопки под постом
def get_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Купить / Buy / Kupić", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ]
    ])

# Отправка поста в канал (пишешь боту в личку — он шлет в канал)
@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_buttons())
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_buttons())
        await message.answer("✅ Пост опубликован!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: проверь админку в канале.\n{e}")

# ОБРАБОТКА НАЖАТИЙ (Всплывающее окно)
@dp.callback_query(F.data.startswith("lang_"))
async def show_translation(call: types.CallbackQuery):
    # Здесь мы берем текст самого поста, под которым нажата кнопка
    original_text = call.message.text or call.message.caption or ""
    
    # Логика перевода (можешь вписать свой перевод или оставить общую фразу)
    if call.data == "lang_en":
        translation = f"🇬🇧 English Version:\n\n{original_text}\n\n(Contact @Nygmad to buy)"
    else:
        translation = f"🇵🇱 Polska Wersja:\n\n{original_text}\n\n(Kontakt @Nygmad w celu zakupu)"

    # show_alert=True создает модальное окно с кнопкой "ОК"
    # Это сообщение видит ТОЛЬКО нажавший, в канале ничего не дублируется
    await call.answer(text=translation, show_alert=True)

# Заглушка для Render
async def handle(request): return web.Response(text="Live")
async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
