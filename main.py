import os
import sys
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler,\
     MessageHandler, filters, Application

import strings_en as st
import tictactoe as tct
import random as r
import calculator as Calc
import datetime as dt

# поиск токена для телеграмма
def getToken():
    token = ''
    if os.path.isfile(st.BOT_TOKEN_FILENAME):
        f = open(st.BOT_TOKEN_FILENAME, "r")
        token = f.read()
        f.close()
    else:
        print(st.ALERT_ABOUT_TOKEN)
        sys.exit()  # завершить работу скрипта0
    return token
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(st.ANSW_HELP)

async def newYearLeft(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        now = dt.datetime.today()
        NY = dt.datetime(dt.datetime.today().year + 1, 1, 1)
        d = NY-now           
        mm, ss = divmod(d.seconds, 60)
        hh, mm = divmod(mm, 60)  
        user = update.message.from_user
        await update.message.reply_text('Until the {} of New Year {}: {} days {} hours\
{} min {} sec.'.format(st.SYMBOL_NY, NY.year, d.days, hh, mm, ss))


async def sayhi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text('{} {}'.format(r.choice(st.greetings), user['username']))


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    text = update.message.text[5:]
    res = str(Calc.eval_(text))
    await update.message.reply_text(f'{text} = {res}')


def main():
    application = Application.builder().token(getToken()).build()
    # добавление обработчиков
    application.add_handler(CommandHandler('start', help_command))
    application.add_handler(CommandHandler('hello', sayhi))
    application.add_handler(CommandHandler('new_tiktaktoe', tct.newGame))
    application.add_handler(CommandHandler('calc', calc))
    application.add_handler(CommandHandler('new_year', newYearLeft))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT, help_command))  # обработчик на любое текстовое сообщение
    application.add_handler(CallbackQueryHandler(tct.button))  # добавление обработчика на CallBack кнопки
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
