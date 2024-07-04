from telegram.ext import CommandHandler, Application, ContextTypes, MessageHandler, filters
from telegram import Bot
import yaml
import asyncio
from datetime import datetime, timedelta
import pytz


TIMEZONE = pytz.timezone('Europe/Moscow')


async def send_msg(chat_id, message):
    bot = Bot(token='7340463442:AAHTj9njBjsXHnLmL-Wbrek575z9e840Sxc')
    await bot.send_message(chat_id=chat_id, text=message)


async def reminder(chat_id, message, per_day):
    start_hour = 8
    end_hour = 21
    while True:
        now = datetime.now(TIMEZONE)
        today_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        if now < today_start:
            wait_time = (today_start - now).total_seconds()
        elif now > today_end:
            wait_time = ((today_start + timedelta(days=1)) - now).total_seconds()
        else:
            interval = (today_end - today_start).total_seconds() / per_day
            next_reminder_time = today_start + timedelta(seconds=interval)
            while next_reminder_time < now:
                next_reminder_time += timedelta(seconds=interval)
            wait_time = (next_reminder_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        await send_msg(chat_id, f'Не забудьте принять {message}!')


async def reminder_runner(chat_id, message, duration, per_day):
    reminder_task = asyncio.create_task(reminder(chat_id, message, per_day))
    await asyncio.sleep(duration)
    reminder_task.cancel()
    try:
        await reminder_task
    except asyncio.CancelledError:
        await send_msg(chat_id, f'{message} можно больше не принимать.')


async def link_user(id, fio):
    try:
        with open('data.yaml', 'r+', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            medlist = ''
            for i in data[fio]["Лекарства"]:
                medlist += f"\n{i['Название']}, {i['Кол-во']}, {i['Сколько дней']} суток"
                msg = i['Название']
                per_day = int(i['Кол-во'].split()[0])
                dur = int(i['Сколько дней']) * 86400
                asyncio.create_task(reminder_runner(id, msg, dur, per_day))
            data[fio]['chat_id'] = id
            file.seek(0)
            yaml.dump(data, file, allow_unicode=True)
            reply_string = (
                f'Здравствуйте, {fio}. '
                'Здесь вы будете получать напоминания о '
                'приеме ваших лекарств. '
                'Вам прописано:\n'
                f'{medlist}\n'
                '\nПожалуйста, отправляйте в чат отчет о своем '
                'самочувствии каждый день!'
            )
            return reply_string
    except yaml.YAMLError as exc:
        return f"Ошибка! \n{exc}"


async def start(update, _):
    await update.message.reply_text(
        'Добро пожаловать в программу для отслеживания приема лекарств. Пожалуйста, введите ваши ФИО'
    )


async def common(update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    chat_id = context._chat_id
    try:
        with open('data.yaml', 'r+', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            if msg in data:
                msg = await link_user(chat_id, fio=msg)
            else:
                now = datetime.now(TIMEZONE)
                today = now.strftime("%d.%m.%Y")
                status = 'записан.'
                found = False
                for key, val in data.items():
                    if 'chat_id' in val:
                        if val['chat_id'] == chat_id:
                            if 'Отчёты' not in data[key]:
                                data[key]['Отчёты'] = []
                            buff = data[key]['Отчёты']
                            if len(buff) > 0:
                                if buff[-1]['Дата'] != today:
                                    buff.append({'Дата': today, 'Содержание': msg})
                                else:
                                    buff[-1] = {'Дата': today, 'Содержание': msg}
                                    status = 'перезаписан. Предыдущий отчёт за сегодня удалён.'
                            else:
                                buff.append({'Дата': today, 'Содержание': msg})
                            data[key]['Отчёты'] = buff
                            file.seek(0)
                            yaml.dump(data, file, allow_unicode=True)
                            msg = f'Ваш отчет за {today} {status}'
                            found = True
                            break
                if not found:
                    msg = 'Вы не найдены в базе пациентов.'
            await update.message.reply_text(msg)
    except yaml.YAMLError as exc:
        print(exc)
        return f"Ошибка! \n{exc}"


if __name__ == '__main__':
    app = Application.builder().token('7340463442:AAHTj9njBjsXHnLmL-Wbrek575z9e840Sxc').build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, common))
    app.run_polling()
