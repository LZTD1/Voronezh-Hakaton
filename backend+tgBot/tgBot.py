import logging
import os
import asyncio, json
from datetime import datetime
from database import Database
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from keyboardsTG import keyboards

bot = Bot(token="6280443347:AAF12weiKnWGuXC79coakcoIBAv4gu-PLKQ")
db = Database("localhost", "5432", "postgres", "123321", "fsb_database")
keyboards = keyboards()  # Определяем класс клавиатур
dp = Dispatcher(bot)

# import json
# data = {u'Processes': [[u'root', u'3606', u'0.0', u'0.2', u'76768', u'16664', u'?', u'Ss', u'20:40', u'0:01', u'/usr/local/bin/python2 /usr/local/bin/gunicorn app:app -b 0.0.0.0:80 --log-file - --access-logfile - --workers 4 --keep-alive 0'], [u'root', u'4088', u'0.0', u'0.2', u'88544', u'20156', u'?', u'S', u'20:40', u'0:00', u'/usr/local/bin/python2 /usr/local/bin/gunicorn app:app -b 0.0.0.0:80 --log-file - --access-logfile - --workers 4 --keep-alive 0'], [u'root', u'4090', u'0.0', u'0.2', u'88552', u'20140', u'?', u'S', u'20:40', u'0:00', u'/usr/local/bin/python2 /usr/local/bin/gunicorn app:app -b 0.0.0.0:80 --log-file - --access-logfile - --workers 4 --keep-alive 0'], [u'root', u'4097', u'0.0', u'0.2', u'88552', u'20112', u'?', u'S', u'20:40', u'0:00', u'/usr/local/bin/python2 /usr/local/bin/gunicorn app:app -b 0.0.0.0:80 --log-file - --access-logfile - --workers 4 --keep-alive 0'], [u'root', u'4110', u'0.0', u'0.2', u'88548', u'20160', u'?', u'S', u'20:40', u'0:00', u'/usr/local/bin/python2 /usr/local/bin/gunicorn app:app -b 0.0.0.0:80 --log-file - --access-logfile - --workers 4 --keep-alive 0']], u'Titles': [u'USER', u'PID', u'%CPU', u'%MEM', u'VSZ', u'RSS', u'TTY', u'STAT', u'START', u'TIME', u'COMMAND']}
# data = json.dumps(data) # dict to string
# data = json.loads(data) # string to json
# print data['Processes']

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    userData = await db.getAllbyTG(message.from_user.id)
    if userData:

        user_id = userData['id']
        role = userData['role']
        login = userData['login']
        first_name = userData['first_name']
        last_name = userData['last_name']
        petronymic = userData['petronymic']
        teams = userData['teams']
        actions = userData['actions']
        rating = userData['actions']


        if message.text == "/start":
            await message.reply("Меню:", reply_markup=keyboards.mainKeyboard(role))
        if message.text.lower() == "💬 помощь":
            msg = [
                "📃 <b>Контактные данные</b>",
                "\nПочта: emailtopaste@gmail.com",
                "Телефон: +79998886655",
                "\n...",
            ]

            await message.reply("\n".join(msg), parse_mode="HTML")
        if role == 0:
            if message.text.lower() == "💥 мои мероприятия":
                events = await db.getEvents(json.loads(teams))
                if events:
                    for k, val in enumerate(events):
                        eventsList = []
                        eventsList.append(f"<b>{k + 1}.</b> {val['name']}\n")
                        eventsList.append(f"\n<code>{val['description']}</code>\n")
                        people = await db.getPeopleOfTeams(json.loads(val['teams']))
                        eventsList.append(f"Команды участвуют: {len(json.loads(val['teams']))} ({people} чел.)")
                        eventsList.append(
                            f"\nНачало мероприятия: <code>{datetime.utcfromtimestamp(val['datestart']).strftime('%Y-%m-%d %H:%M')}</code>")
                        eventsList.append(
                            f"Конец мероприятия: <code>{datetime.utcfromtimestamp(val['dateend']).strftime('%Y-%m-%d %H:%M')}</code>")

                        if (val['photo'] == "null"):
                            await message.reply("\n".join(eventsList), parse_mode="HTML")
                        else:
                            await bot.send_photo(
                                message.chat.id, val['photo'], caption="\n".join(eventsList),
                                reply_to_message_id=message.message_id, parse_mode="HTML")

                else:
                    await message.reply("Упс, не нашел вас нигде!! ")
            elif message.text.lower() == "👥 моя команда":
                team = json.loads(teams)
                if (len(team) != 0):
                    teams = await db.getTeamsByUser(team)
                    if (len(teams) != 0):
                        for k, val in enumerate(teams):
                            msg = []
                            msg.append(f"\n<b>{k + 1}.</b> {teams[k]['name']}\n")
                            msg.append(f"<code>{teams[k]['description']}</code>\n")
                            msg.append(f"Участников: {len(json.loads(teams[k]['users']))};")
                            # msg.append(f"Задействована в кейсах: {len(json.loads(teams[k]['events']))};")

                            if (json.loads(teams[k]['users'])[0] == user_id):
                                msg.append("Лидер команды - Вы.")
                            else:
                                teamlid = db.getUserByID(json.loads(teams[k]['users'])[0])
                                if teamlid:
                                    msg.append(
                                        f"Лидер команды - {teamlid['first_name']} {teamlid['last_name']} {teamlid['petronymic']}")

                            if (teams[k]['photo'] == "null"):
                                await message.reply("\n".join(msg), parse_mode="HTML")
                            else:
                                await bot.send_photo(
                                    message.chat.id, teams[k]['photo'], caption="\n".join(msg),
                                    reply_to_message_id=message.message_id, parse_mode="HTML")
                    else:
                        await message.reply("Я не нашел за тобой никаких закрепленных команд...")
                else:
                    await message.reply("Я не нашел за тобой никаких закрепленных команд...")

        if role == 3: #  0(user teamlid), 1 - predstavitel, 2 - admin, 3 partner
            if message.text.lower() == "спонсированные":
                sponsor = json.loads(userData['sponspor'])
                if len(sponsor) == 0:
                    await message.reply("Вас не назначили представителем какой-либо компании")
                else:
                    array = []
                    for k, val in enumerate(sponsor): # Проходим по каждому представительному месту
                        res = await db.getActiveEvents(sponsored=True, id_transfer=val)
                        if res:
                            array.append(res)
                    if len(array) == 0:
                        await message.reply("Ближайшее время вы не организовывали мероприятия " + str(len(array)))
                    else:
                        for k, val in enumerate(array): # Осуществляем проход по всем позициям организатора человека
                            eventsList = []
                            for j, p in enumerate(val): # Осуществляем проход по конкретному организатор в конкретных мероприятих
                                eventsList = []
                                eventsList.append(f"<b>{j + 1}.</b> {p['name']}\n")
                                eventsList.append(f"\n<code>{p['description']}</code>\n")
                                people = await db.getPeopleOfTeams(json.loads(p['teams']))
                                eventsList.append(f"Команды участвуют: {len(json.loads(p['teams']))} ({people} чел.)")
                                eventsList.append(
                                    f"\nНачало мероприятия: <code>{datetime.utcfromtimestamp(p['datestart']).strftime('%Y-%m-%d %H:%M')}</code>")
                                eventsList.append(
                                    f"Конец мероприятия: <code>{datetime.utcfromtimestamp(p['dateend']).strftime('%Y-%m-%d %H:%M')}</code>")
                                currentEvent = json.loads(p['sponsors'])
                                eventsList.append(f"\nВсего спонсоров: {len(currentEvent)}")

                                for currentSponsor in currentEvent:
                                    eventsList.append(f"\n<code>Спонсируется: {currentSponsor['name']}")
                                    eventsList.append(f"На условиях: {currentSponsor['regulations']}</code>")
                                if (p['photo'] == "null"):
                                    await message.reply("\n".join(eventsList), parse_mode="HTML")
                                else:
                                    await bot.send_photo(
                                        message.chat.id, p['photo'], caption="\n".join(eventsList),
                                        reply_to_message_id=message.message_id, parse_mode="HTML")
            if message.text.lower() == "представляю":
                sponsor = json.loads(userData['sponspor'])
                if len(sponsor) == 0:
                    await message.reply("Вас не назначили представителем какой-либо компании")
                else:
                    array = []
                    for k, val in enumerate(sponsor):  # Проходим по каждому представительному месту
                        res = await db.getSponsorByid(val)
                        if res:
                            msg = []
                            msg.append(f"<b>{res['name']}</b>\n")
                            msg.append(f"<code>{res['about']}</code>\n")
                            if (res['photo'] == "null"):
                                await message.reply("\n".join(msg), parse_mode="HTML")
                            else:
                                await bot.send_photo(
                                    message.chat.id, res['photo'], caption="\n".join(msg),
                                    reply_to_message_id=message.message_id, parse_mode="HTML")
                        else:
                            message.reply("Похоже вы ни являетесь предствителем ни 1 организации")
        if role == 1:
            if message.text.lower() == "мои мероприятия":
                parent = json.loads(userData['parent'])
                if len(parent) == 0:
                    await message.reply("Вас не являетесь представителем какой-либо федерации")
                else:
                    array = []
                    for k, val in enumerate(parent):  # Проходим по каждому представительному месту
                        res = await db.getActiveEvents(parent=True, id_transfer=val)
                        if res:
                            array.append(res)
                    if len(array) == 0:
                        await message.reply("Ближайшее время вы не участвуете в мероприятиях" + str(len(array)))
                    else:
                        for k, val in enumerate(
                                array):  # Осуществляем проход по всем позициям представителя споносра человека
                            eventsList = []
                            for j, p in enumerate(
                                    val):  # Осуществляем проход по конкретному спонсору в конкретных мероприятих
                                eventsList = []
                                eventsList.append(f"<b>{j + 1}.</b> {p['name']}\n")
                                eventsList.append(f"\n<code>{p['description']}</code>\n")

                                print(json.loads(p['teams']))
                                people = await db.getPeopleOfTeams(json.loads(p['teams']))
                                eventsList.append(f"Команды участвуют: {len(json.loads(p['teams']))} ({people} чел.)")
                                eventsList.append(
                                    f"\nНачало мероприятия: <code>{datetime.utcfromtimestamp(p['datestart']).strftime('%Y-%m-%d %H:%M')}</code>")
                                eventsList.append(
                                    f"Конец мероприятия: <code>{datetime.utcfromtimestamp(p['dateend']).strftime('%Y-%m-%d %H:%M')}</code>")

                                currentEvent = json.loads(p['sponsors'])
                                eventsList.append(f"\nВсего спонсоров: {len(currentEvent)}")

                                for currentSponsor in currentEvent:
                                    eventsList.append(f"\n<code>Спонсируется: {currentSponsor['name']}")
                                    eventsList.append(f"На условиях: {currentSponsor['regulations']}</code>")
                                if (p['photo'] == "null"):
                                    await message.reply("\n".join(eventsList), parse_mode="HTML")
                                else:
                                    await bot.send_photo(
                                        message.chat.id, p['photo'], caption="\n".join(eventsList),
                                        reply_to_message_id=message.message_id, parse_mode="HTML")
    else:
        await message.reply("Упс, я вас не нашел.\nЗарегестрируйтесь на сайте!")
async def on_startup(dispatcher):
    print("open DB")

async def on_shutdown(dispatcher):
    print("closed DB")
    await db.disconnect()
async def main():
    await db.connect()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
