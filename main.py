import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- НАСТРОЙКИ ---
API_TOKEN ="8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
ADMIN_URL = "https://t.me/Nygmad"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Меню кнопок
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", url=ADMIN_URL)],
        [
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="rate_usd"),
            InlineKeyboardButton(text="🇪🇺 EUR", callback_data="rate_eur")
        ]
    ])

# Эта команда нужна только тебе ОДИН РАЗ, чтобы бот выплюнул кнопки в канал
@dp.message(F.text == "/setup")
async def setup_channel(message: types.Message):
    # Бот отправит кнопки туда, где ты написал эту команду
    await message.answer("📊 **Актуальные курсы и заказ:**", reply_markup=main_menu(), parse_mode="Markdown")

# Обработка нажатий на кнопки (будет работать в канале)
@dp.callback_query(F.data.startswith("rate_"))
async def show_currency(call: types.CallbackQuery):
    currency = call.data.split("_")[1].upper()
    
    # Получаем свежий курс
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.exchangerate-api.com/v4/latest/{currency}") as resp:
            data = await resp.json()
            rate = data['rates']['RUB']
    
    # Бот отвечает пользователю всплывающим окном или сообщением
    await call.message.answer(f"💵 Курс {currency}: **{rate} RUB**", parse_mode="Markdown")
    await call.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
