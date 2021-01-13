import random
import os
import logging
import json

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from datetime import datetime, timedelta

from constants import *
from persistence_with_sqlite import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def getRandomText(texts):
    return texts[random.randint(0, len(texts)-1)]

def message_received(update, context):
    text = update.effective_message.text
    ctext = update.effective_message.text.strip().lower()
    chat_id=update.effective_chat.id
    p = getPerson(chat_id)
    logger.info(f"Message received from {p['name'] if p else 'Desconocido'}: {text}")
    if p:
        if p["status"] == Status.ALARMA_ENVIADA:
            supervisorChatId = getSupervisorChatId(p["supervisor"])
            context.bot.send_message(supervisorChatId, text=f"Parece que {p['name']} está bien y dice: {text}")
        if "noche" in ctext or "dormir" in ctext:
            updatePerson(chat_id, Status.DURMIENDO)
            context.bot.send_message(chat_id=chat_id, text=getRandomText(night_texts))
        elif any([i in ctext for i in ["bañar","duchar","comprar","perro","pasear","rufo","sacar"]]):
            updatePerson(chat_id, Status.ESPERANDO_A_HACER_PING, ASKING_TIME - SHOWER_TIME)
            context.bot.send_message(chat_id=chat_id, text=getRandomText(answer_texts))
        else:
            updatePerson(chat_id, Status.ESPERANDO_A_HACER_PING)
            context.bot.send_message(chat_id=chat_id, text=getRandomText(answer_texts))
    else:
        context.bot.send_message(chat_id=chat_id, text="Parece que no estás dado de alta")

def check(context):
    for p in getAllPeople():
        chat_id = p["chat_id"]
        elapsed = (datetime.now() - p["time"]).total_seconds()
        logger.info(f"Vigilando usuario: {p['name']}, status: {p['status']}, elapsed: {elapsed}")
        if p["status"] == Status.ESPERANDO_A_HACER_PING:
            if elapsed > ASKING_TIME:
                logger.info("Preguntar que tal")
                context.bot.send_message(chat_id=chat_id, text=getRandomText(asking_texts))
                updatePerson(chat_id, Status.ESPERANDO_RESPUESTA)
            else:
                logger.info("Esperando para preguntar. No hacer nada")
        elif p["status"] == Status.ESPERANDO_RESPUESTA:
            if elapsed > ANSWER_TIME:
                logger.info("Enviar alarma")
                context.bot.send_message(chat_id=chat_id, text="Como no respondes he avisado a tu supervisor " + p["supervisor"])
                supervisorChatId = getSupervisorChatId(p["supervisor"])
                if supervisorChatId:
                    context.bot.send_message(supervisorChatId, text=f"¡Atención! {p['name']} no responde y puede que necesite ayuda")
                else:
                    logger.warning(f"El usuario {p['supervisor']} no está dado de alta como supervisor")
                    context.bot.send_message(chat_id=chat_id, text="No he podido avisar a tu supervisor porque no está dado de alta")
                updatePerson(chat_id, Status.ALARMA_ENVIADA)
            else:
                logger.info("Esperando respuesta. No hacer nada")
        elif p["status"] == Status.ALARMA_ENVIADA:
            logger.info("No hacer nada. Alarma ya enviada")
        elif p["status"] == Status.DURMIENDO:
            if elapsed > BED_TIME:
                logger.info("Dar buenos dias y preguntar que tal has dormido")
                context.bot.send_message(chat_id=chat_id, text=getRandomText(morning_texts))
                updatePerson(chat_id, Status.ESPERANDO_RESPUESTA)
            else:
                logger.info("Esperando para dar los buenos días. No hacer nada")


def supervise(update: Update, context: CallbackContext) -> None:
    logger.info("supervise command received: " + update.effective_message.text)
    createSupervisor(update.effective_message.chat_id, update.effective_message.from_user.username)
    update.effective_message.reply_text('Te has dado de alta como supervisor')

def watchme(update: Update, context: CallbackContext) -> None:
    logger.info("watchme command received: " + update.effective_message.text)
    if len(context.args) > 0:
        createPerson(update.effective_message.chat_id, update.effective_chat.first_name, context.args[0])
        update.effective_message.reply_text('Hecho! A partir de ahora te preguntaré de vez en cuando. Si no respondes avisare a ' + context.args[0])
    else:
        update.effective_message.reply_text('Tienes que decirme el nombre de usuario de tu supervisor: Ejemplo: "/vigilame superman"')

def bye(update: Update, context: CallbackContext) -> None:
    logger.info("bye command received: " + update.effective_message.text)
    remove(update.effective_message.chat_id, update.effective_message.from_user.username)
    update.effective_message.reply_text('Te has dado de baja del sistema')

def status(update: Update, context: CallbackContext) -> None:
    logger.info("status command received")
    p = getAllPeople()
    print(p)
    #p["time"] = str(p["time"])
    update.effective_message.reply_text(json.dumps(p, indent=4, sort_keys=True, default=str))

def start(update: Update, context: CallbackContext) -> None:
    logger.info("help command received: " + update.effective_message.text)
    update.effective_message.reply_text('''Usa "/supervisar" para darte de alta como supervisor
Usa "/vigilame USUARIO" para recibir preguntas sobre como estás de ven en cuando. Si no respondes se avisará al USUARIO.
El USUARIO tiene que estar dado de alta como supervisor
Usa "/adios" para darte de baja completamente del sistema''')

logger.info("ASKING_TIME: " + str(ASKING_TIME))
logger.info("ANSWER_TIME: " + str(ANSWER_TIME))
logger.info("BED_TIME: " + str(BED_TIME))
logger.info("CHECK_TIME: " + str(CHECK_TIME))
logger.info("DB_FILE: " + DB_FILE)

updater = Updater(os.environ['TELEGRAM_TOKEN'])
updater.dispatcher.add_handler(CommandHandler(['start','help'], start))
updater.dispatcher.add_handler(CommandHandler(['supervise','supervisar'], supervise))
updater.dispatcher.add_handler(CommandHandler(['watchme','vigilame'], watchme))
updater.dispatcher.add_handler(CommandHandler(['bye','adios'], bye))
updater.dispatcher.add_handler(CommandHandler(['status','estado'], status))
echo_handler = MessageHandler(Filters.text & (~Filters.command), message_received)
updater.dispatcher.add_handler(echo_handler)
updater.job_queue.run_repeating(check, CHECK_TIME)
updater.start_polling()
updater.idle()
