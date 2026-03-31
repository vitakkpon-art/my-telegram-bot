import asyncio
import urllib.request
import json
import re
import os

# Исправление для Pydantic
os.environ["PYDANTIC_SKIP_VALIDATOR_STRINGS"] = "True"

from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from deep_translator import GoogleTranslator

# --- НАСТРОЙКИ ---
# Вставь сюда НОВЫЙ токен от @BotFather (старый уже не работает)
API_TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН" 
CHANNEL_ID = -1003728797088 
ADMIN_USERNAME = "@твой_ник" # Твой ник в ТГ

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/PLN"
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode())['rates']
    except:
        return {"USD": 0.25, "EUR": 0.23}

def get_combined_buttons():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🇬🇧 English", callback_data="tr_en"),
        types.InlineKeyboardButton(text="🇵🇱 Polski", callback_data="tr_pl")
    )
    builder.row(
        types.InlineKeyboardButton(text="💵 USD", callback_data="curr_USD"),
        types.InlineKeyboardButton(text="💶 EUR", callback_data="curr_EUR")
    )
    builder.row(
        types.InlineKeyboardButton(text="📦 Доставка", callback_data="info_ship"),
        types.InlineKeyboardButton(text="⭐️ Отзывы", callback_data="info_rev")
    )
    builder.row(
        types.InlineKeyboardButton(text="🛍️ Order / Zamów", url=f"https://t.me/{ADMIN_USERNAME.replace('@','')}")
    )
    return builder.as_markup()

@dp.channel_post()
async def handle_post(message: types.Message):
    if message.chat.id == CHANNEL_ID:
        try:
            await bot.edit_message_reply_markup(chat_id=CHANNEL_ID, message_id=message.message_id, reply_markup=get_combined_buttons())
        except: pass

@dp.callback_query(F.data.startswith("tr_"))
async def process_tr(callback: types.CallbackQuery):
    target = callback.data.replace("tr_", "")
    text = callback.message.text or callback.message.caption
    if text:
        res = GoogleTranslator(source='auto', target=target).translate(text)
        hint = "To order, click the button below!" if target == "en" else "Aby zamówić, kliknij przycisk poniżej!"
        await callback.answer(text=f"[{target.upper()}]\n{res}\n\n{hint}", show_alert=True)

@dp.callback_query(F.data.startswith("curr_"))
async def process_curr(callback: types.CallbackQuery):
    curr = callback.data.replace("curr_", "")
    text = callback.message.text or callback.message.caption
    price_matches = re.findall(r'(\d+)\s*zl', text, re.IGNORECASE)
    if price_matches:
        rate = get_rates().get(curr, 0)
        results = [f"📊 {p} PLN ≈ {round(int(p) * rate, 2)} {curr}" for p in price_matches]
        await callback.answer(text="\n".join(list(dict.fromkeys(results))), show_alert=True)
    else:
        await callback.answer(text="❌ Цены с 'zl' не найдены", show_alert=True)

@dp.callback_query(F.data.startswith("info_"))
async def process_info(callback: types.CallbackQuery):
    msg = "📦 ДОСТАВКА:\nInPost: 15 zl\nEU: от 40 zl" if callback.data == "info_ship" else "⭐️ ОТЗЫВЫ:\nМы работаем честно!"
    await callback.answer(text=msg, show_alert=True)

async def main():
    print("--- БОТ ЗАПУЩЕН ---")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
      
