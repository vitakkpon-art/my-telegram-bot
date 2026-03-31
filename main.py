import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"
# ЗАМЕНИ НА СВОЙ КАНАЛ (с @)
CHANNEL_ID = "@твой_канал" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Кнопки, которые будут ПОД постом
def get_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Купить / Buy / Kupić", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ]
    ])

# Бот ловит любое твое сообщение (текст или фото с текстом) и шлет в канал с кнопками
@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_buttons())
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_buttons())
        
        await message.answer("✅ Пост опубликован в канале с кнопками!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: проверь, что бот админ в {CHANNEL_ID}\n{e}")

# Обработка кнопок языков
@dp.callback_query(F.data.startswith("lang_"))
async def change_lang(call: types.CallbackQuery):
    text = "Hello! Contact owner to buy." if call.data == "lang_en" else "Cześć! Skontaktuj się z właścicielem."
    await call.message.answer(text)
    await call.answer()

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
    
