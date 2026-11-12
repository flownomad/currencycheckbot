import requests
import matplotlib.pyplot as plt
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup


TOKEN = "..."
API_URL = "https://api.currencyapi.com/v3/latest?apikey=cur_live_GlWlgDluTrndD1siQbll5PPNKJ0QQqWkGDYIpHwW"

CURRENCY_FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "RUB": "🇷🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
    "BYN": "🇧🇾", "KRW": "🇰🇷", "UAH": "🇺🇦", "CNY": "🇨🇳"
}

def get_currency_menu():
    keyboard = [[f"{key} {flag}" for key, flag in CURRENCY_FLAGS.items()]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text("Выберите валюту для конвертации:", reply_markup=get_currency_menu())

async def convert_amount(update, context):
    user_input = update.message.text.split()
    
    if len(user_input) != 2 or not user_input[0].isdigit():
        await update.message.reply_text("❌ Ошибка! Введите число и валюту (например, `100 RUB`)")
        return

    amount = float(user_input[0]) 
    base_currency = user_input[1].upper()  
    print(f"Пользователь ввёл: {amount} {base_currency}")  

    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        print(f"JSON-ответ API: {data}")  

        if "data" not in data or base_currency not in data["data"]:
            await update.message.reply_text(f"❌ Ошибка: API не вернул курс валют для `{base_currency}`!")
            return
        
        base_rate = data["data"][base_currency]["value"]
        rates_text = f"💰 **Конвертация {amount} {base_currency} {CURRENCY_FLAGS.get(base_currency, '')} во все валюты**\n──────────────\n"

        for target_currency in CURRENCY_FLAGS.keys():
            if target_currency != base_currency and target_currency in data["data"]:
                rate = data["data"][target_currency]["value"]
                converted_amount = (amount / base_rate) * rate
                rates_text += f"🔹 `{target_currency}` {CURRENCY_FLAGS[target_currency]} → `{converted_amount:.2f}` {target_currency}\n"

        rates_text += "📌 Данные актуальны на текущий момент!"

        await update.message.reply_text(rates_text)
    else:
        await update.message.reply_text(f"❌ Ошибка загрузки курса! Код: `{response.status_code}`")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_amount))

app.run_polling()
