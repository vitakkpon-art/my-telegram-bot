import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- НАСТРОЙКИ (ОБЯЗАТЕЛЬНО ПРОВЕРЬ) ---
API_TOKEN = "8371761898:AAEBg0nPe1gxS7X8wOJCNjroWIcpaHHqd3w"
ADMIN_URL = "https://t.me/Nygmad"
# Впиши сюда юзернейм своего канала С СОБАЧКОЙ @
CHANNEL_ID = "@ТВОЙ_ЮЗЕРНЕЙМ_КАНАЛА" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция получения курса валют
async def get_rate(currency):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.exchangerate-api.com/v4/latest/{currency}") as resp:
                data = await resp.json()
                return data['rates']['RUB']
    except Exception:
        return "недоступен"

# Создание меню (только нужные кнопки)
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="🛒 Купить", url=ADMIN_URL)],
        [
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="usd"),
            InlineKeyboardButton(text="🇪🇺 EUR", callback_data="eur")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start (работает только в личке)
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я обновлен.\n\n"
        "Чтобы отправить это меню в твой канал, напиши команду: /send",
        reply_markup=main_menu()
    )

# Команда /send (отправляет меню в канал)
@dp.message(F.text == "/send")
async def send_to_channel(message: types.Message):
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID, 
            text="📊 **Актуальные курсы и покупка:**", 
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
        await message.answer("✅ Меню успешно отправлено в канал!")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки в канал!\nПроверь:\n1. Правильно ли указан CHANNEL_ID в коде.\n2. Сделал ли ты бота АДМИНИСТРАТОРОМ канала.\n\nОшибка: {e}")

# Обработка нажатий на кнопки USD/EUR
@dp.callback_query(F.data.in_({"usd", "eur"}))
async def show_rate(call: types.CallbackQuery):
    currency = call.data.upper()
    rate = await get_rate(currency)
    await call.message.answer(f"💵 Курс {currency} к рублю: **{rate} RUB**", parse_mode="Markdown")
    await call.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
