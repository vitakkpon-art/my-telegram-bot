import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- НАСТРОЙКИ ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
ADMIN_URL = "https://t.me/Nygmad"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для получения курса в реальном времени
async def get_rate(currency):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.exchangerate-api.com/v4/latest/{currency}") as resp:
                data = await resp.json()
                return data['rates']['RUB']
    except:
        return "ошибка соединения"

# Главное меню (только нужные кнопки)
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", url=ADMIN_URL)],
        [
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="usd"),
            InlineKeyboardButton(text="🇪🇺 EUR", callback_data="eur")
        ],
        [InlineKeyboardButton(text="🌍 Перевести текст", callback_data="translate")]
    ])
    return keyboard

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Актуальные курсы и связь со мной здесь:", reply_markup=main_menu())

@dp.callback_query()
async def clicks(call: types.CallbackQuery):
    if call.data == "usd":
        rate = await get_rate("USD")
        await call.message.answer(f"💵 Курс доллара сейчас: {rate} RUB")
    elif call.data == "eur":
        rate = await get_rate("EUR")
        await call.message.answer(f"💶 Курс евро сейчас: {rate} RUB")
    elif call.data == "translate":
        await call.message.answer("Пришли текст для перевода!")
    await call.answer()

async def run():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run())
    
