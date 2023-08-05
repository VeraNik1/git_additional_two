import random as r
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import strings_en as st


#сочетания индексов для победы
victory = [(0, 1, 2),
           (3, 4, 5),
           (6, 7, 8),
           (0, 3, 6),
           (1, 4, 7),
           (2, 5, 8),
           (0, 4, 8),
           (2, 4, 6)]

#проверка наличия победителя
def chek_victory(field):
    if any(all(field[i] == st.SYMBOL_X for i in victory[j]) for j in range(8)):
        return st.SYMBOL_X
    if any(all(field[i] == st.SYMBOL_O for i in victory[j]) for j in range(8)):
        return st.SYMBOL_O
    return False

# возвращает количество неопределенных ячеек (т.е. количество ячеек, в которые можно сходить)
# cellArray - массив данных из callBackData, полученных после нажатия на callBack-кнопку
def countUndefinedCells(cellArray):
    return ''.join(cellArray).count(st.SYMBOL_UNDEF)


# выбор хода для бота сложность студент
def bot_choice_student(field):
#если в ряду два O и нет Х
    temp = []
    for index in victory:
        if (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_O) == 2\
            and (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_X) == 0:
            temp = [i for i in (index[0], index[1], index[2]) if field[i]!=st.SYMBOL_O][0]
            return temp
#если в ряду два X и нет О
    for index in victory:
        if (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_X) == 2\
            and (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_O) == 0:            
            temp = [i for i in (index[0], index[1], index[2]) if field[i] !=st.SYMBOL_X][0]
            return temp
#в ряду один О и нет X
    for index in victory:
        if (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_X) == 0 \
            and (field[index[0]], field[index[1]], field[index[2]]).count(st.SYMBOL_O) == 1:            
            temp = r.choice([i for i in (index[0], index[1], index[2]) if field[i]!=st.SYMBOL_O])
            return temp

#для первого хода компьютера в центр или в правый верхний угол
    if st.SYMBOL_O not in field:
        if field[4] != st.SYMBOL_X:
            return 4
        else:
            return 2
#для любого другого варианта
    else:
        temp = r.choice([i for i in range(9) if field[i] not in [st.SYMBOL_X, st.SYMBOL_O]])
        return temp

# callBackData формат:
# n????????? - общее описание
# n - номер кнопки
# ? - один из вариантов значения клетки: смотри модуль strings, раздел "символы, которые используются"
# пример: 5❎❎🅾🅾❎❎◻◻❎
# означает, что была нажата пятая кнопка, и текущий вид поля:
# ❎❎🅾
# 🅾❎❎
# ⬜ ⬜❎
# данные обо всем состоянии поля необходимо помещаются в кнопку, 
# т.к. бот имеет доступ к информации только из текущего сообщения
# игра: проверка возможности хода крестиком, проверка победы крестика, ход бота (ноликом), проверка победы ботом
# возвращает:
# message - сообщение, которое надо отправить
# callBackData - данные для формирования callBack данных обновленного игрового поля
# async def Choose_regime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [
#         [InlineKeyboardButton("Младенец", callback_data="1")],
#         [InlineKeyboardButton("Школьник", callback_data="2"),],
#         [InlineKeyboardButton("Студент", callback_data="3")],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Выберите сложность игры:", reply_markup=reply_markup)



async def newGame(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # сформировать callBack данные для первой игры, то есть строку, состояющую из 9 неопределенных символов
    data = ''
    for i in range(0, 9):
        data += st.SYMBOL_UNDEF
    # отправить сообщение для начала игры
    await update.message.reply_text(st.ANSW_YOUR_TURN, reply_markup=InlineKeyboardMarkup(getKeyboard(data)))
    

def game(callBackData):
    # message  -  использование глобальной переменной message
    message = st.ANSW_YOUR_TURN  # сообщение, которое вернется
    alert = None
    buttonNumber = int(callBackData[0])  # считывание нажатой кнопки, преобразуя ее из строки в число
    if not buttonNumber == 9:  # цифра 9 передается в первый раз в качестве заглушки. Т.е. если передана цифра 9, то клавиатура для сообщения создается впервые
        charList = list(callBackData)  # строчка callBackData разбивается на посимвольный список "123" -> ['1', '2', '3']
        charList.pop(0)  # удаление из списка первого элемента: который отвечает за выбор кнопки
        if charList[buttonNumber] == st.SYMBOL_UNDEF:  # проверка: если в нажатой кнопке не выбран крестик/нолик, то можно туда сходить крестику
            charList[buttonNumber] = st.SYMBOL_X  # эмуляция хода крестика
            if chek_victory(charList):  # проверка: выиграл ли крестик после своего хода
                message = st.ANSW_YOU_WIN
            else:  # если крестик не выиграл, то может сходит бот, т.е. нолик
                if countUndefinedCells(charList) != 0:  # проверка: есть ли свободные ячейки для хода
                    # если есть, то ходит бот (нолик)
                    buttonNumber = bot_choice_student(charList)
                    charList[buttonNumber] = st.SYMBOL_O
                    if chek_victory(charList):  # проверка: выиграл ли бот после своего хода
                        message = st.ANSW_BOT_WIN
        # если клетка, в которую хотел походить пользователь уже занята:
        else:
            alert = st.ALERT_CANNOT_MOVE_TO_THIS_CELL

        # проверка: остались ли свободные ячейки для хода и что изначальное сообщение не поменялось (означает, что победителя нет, и что это был не ошибочный ход)
        if countUndefinedCells(charList) == 0 and message == st.ANSW_YOUR_TURN:
            message = st.ANSW_DRAW

        # формирование новой строчки callBackData на основе сделанного хода
        callBackData = ''
        for c in charList:
            callBackData += c

    # проверка, что игра закончилась (message равно одному из трех вариантов: победил Х, 0 или ничья):
    if message == st.ANSW_YOU_WIN or message == st.ANSW_BOT_WIN or message == st.ANSW_DRAW:
        message += '\n'
    #вывод итогового поля
        for i in range(0, 3):
            message += '\n | '
            for j in range(0, 3):
                message += callBackData[j + i * 3] + ' | '
        callBackData = None  # обнуление callBackData

    return message, callBackData, alert

# Формат объекта клавиатуры InlineKeyboardMarkup(keyboard)
# возвращает клавиатуру для бота
# на вход получает callBackData - данные с callBack-кнопки

def getKeyboard(callBackData):
    keyboard = [[], [], []]  # заготовка объекта клавиатуры, которая вернется

    if callBackData != None:  # если
        # формирование объекта клавиатуры
        for i in range(0, 3):
            for j in range(0, 3):
                keyboard[i].append(InlineKeyboardButton(callBackData[j + i * 3], callback_data=str(j + i * 3) + callBackData))
    return keyboard


# возвращает данные после нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    callbackData = query.data
    message, callbackData, alert = game(callbackData)
    if alert is None:  # если не получен сигнал тревоги (alert==None), то редактируем сообщение и меняем клавиатуру
        await query.answer()  # обязательно нужно что-то отправить в ответ, иначе могут возникнуть проблемы с ботом
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(getKeyboard(callbackData)))
    else:
        await query.answer(text=alert, show_alert=True)

