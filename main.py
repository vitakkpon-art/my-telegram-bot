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

# --- КНОПКИ ---

# 1. Стартовый вид (Выбор языка)
def get_lang_selection_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"),
            InlineKeyboardButton(text="🇵🇱 Polski", callback_data="setlang_pl")
        ]
    ])

# 2. Вид после выбора языка
def get_translated_buttons(lang):
    if lang == 'en':
        buy_text = "🛍️ Order / Buy"
        info_text = "ℹ️ Delivery Info"
        back_text = "⬅️ Back / Назад"
    else: # pl
        buy_text = "🛍️ Zamów / Kupić"
        info_text = "ℹ️ Info o dostawie"
        back_text = "⬅️ Powrót / Назад"
        
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buy_text, url=MY_PROFILE_URL)],
        [InlineKeyboardButton(text=info_text, callback_data=f"info_{lang}")],
        [InlineKeyboardButton(text=back_text, callback_data="reset_ru")]
    ])

# --- ОБРАБОТЧИКИ ---

@dp.message(F.chat.type == "private")
async def forward_to_channel(message: types.Message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, reply_markup=get_lang_selection_buttons(), parse_mode="HTML")
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=get_lang_selection_buttons(), parse_mode="HTML")
        await message.answer("✅ Пост опубликован!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ВЫБОР ЯЗЫКА (Перевод поста)
@dp.callback_query(F.data.startswith("setlang_"))
async def set_language(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    original_text = call.message.text or call.message.caption or ""
    
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(original_text)
        header = "🇬🇧 ENGLISH" if lang == 'en' else "🇵🇱 POLSKI"
        new_text = f"<b>{header}</b>\n──────────────\n\n{translated}"
        
        if call.message.text:
            await call.message.edit_text(text=new_text, reply_markup=get_translated_buttons(lang), parse_mode="HTML")
        else:
            await call.message.edit_caption(caption=new_text, reply_markup=get_translated_buttons(lang), parse_mode="HTML")
        await call.answer()
    except:
        await call.answer("Translation error", show_alert=True)

# ВОЗВРАТ НАЗАД К РУССКОМУ
@dp.callback_query(F.data == "reset_ru")
async def reset_to_ru(call: types.CallbackQuery):
    current_text = call.message.text or call.message.caption or ""
    
    # Очищаем текст от нашего заголовка и линии, чтобы вернуть оригинал
    if "──────────────" in current_text:
        original_part = current_text.split("──────────────")[-1].strip()
    else:
        original_part = current_text

    try:
        if call.message.text:
            await call.message.edit_text(text=original_part, reply_markup=get_lang_selection_buttons(), parse_mode="HTML")
        else:
            await call.message.edit_caption(caption=original_part, reply_markup=get_lang_selection_buttons(), parse_mode="HTML")
        await call.answer("Вернулись к оригиналу")
    except:
        await call.answer("Already in Russian")

# ИНФО
@dp.callback_query(F.data.startswith("info_"))
async def show_info_translated(call: types.CallbackQuery):
    lang = call.data.split('_')[1]
    if lang == 'pl':
        text = "ℹ️ INFORMACJA\n──────────────\n📦 Dostawa InPost - do 24h\n🤝 Spotkanie w Tczewie - do 24h"
    else:
        text = "ℹ️ INFORMATION\n──────────────\n📦 InPost delivery - up to 24h\n🤝 Meeting in Tczew - up to 24h"
    await call.answer(text=text, show_alert=True)

# Запуск
async def handle(request): return web.Response(text="Live")
async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
