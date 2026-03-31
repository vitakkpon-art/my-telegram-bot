import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
MY_PROFILE_URL = "https://t.me/Nygmad"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем меню (Купить + Языки)
def simple_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Купить / Buy / Kupić", url=MY_PROFILE_URL)],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
        ]
    ])

# Команда для получения заготовки поста
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(
        "Вот твой пост для канала. **Перешли** его в свой канал:",
        reply_markup=simple_menu()
    )

# Что пишет бот при нажатии на кнопки языков
@dp.callback_query(F.data.startswith("lang_"))
async def change_lang(call: types.CallbackQuery):
    if call.data == "lang_en":
        text = "Hello! Click the button above to contact the owner and make a purchase."
    else:
        text = "Cześć! Kliknij przycisk powyżej, aby skontaktować się z właścicielem i dokonać zakupu."
    
    await call.message.answer(text)
    await call.answer()

# --- ЗАГЛУШКА ДЛЯ RENDER (чтобы бот не отключался) ---
async def handle(request):
    return web.Response(text="Bot is Live")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    
    print("Бот успешно запущен!")
    await asyncio.gather(site.start(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
    
