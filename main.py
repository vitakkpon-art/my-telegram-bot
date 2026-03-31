import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- НАСТРОЙКИ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
ADMIN_URL = "https://t.me/Nygmad"

# ВПИШИ СВОЙ КАНАЛ ЗДЕСЬ (с собачкой @)
CHANNEL_ID = "@твой_канал" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", url=ADMIN_URL)],
        [
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="rate_usd"),
            InlineKeyboardButton(text="🇪🇺 EUR", callback_data="rate_eur")
        ]
    ])

# Команда только для тебя, чтобы выкинуть меню в канал
@dp.message(F.text == "/send_to_channel")
async def send_now(message: types.Message):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text="📊 **Актуальные курсы и покупка:**", reply_markup=main_menu(), parse_mode="Markdown")
        await message.answer("✅ Отправлено в канал!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: проверь, что бот админ в канале!\n{e}")

# Обработка кнопок в канале
@dp.callback_query(F.data.startswith("rate_"))
async def get_rate_call(call: types.CallbackQuery):
    currency = call.data.split("_")[1].upper()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.exchangerate-api.com/v4/latest/{currency}") as resp:
            data = await resp.json()
            rate = data['rates']['RUB']
    
    # Бот отвечает пользователю НОВЫМ сообщением (так работает в каналах)
    await call.message.answer(f"💵 Курс {currency}: **{rate} RUB**", parse_mode="Markdown")
    await call.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
