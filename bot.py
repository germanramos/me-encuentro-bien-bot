import os
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from datetime import datetime, timedelta

from constants import *
from persistence_with_sqlite import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def message_received(update, context):
    logger.info("message_received: " + update.effective_message.text)
    chat_id=update.effective_chat.id
    if personExists(chat_id):
        if update.effective_message.text.strip().lower() == "buenas noches":
            updatePerson(chat_id, Status.DURMIENDO)
            context.bot.send_message(chat_id=chat_id, text="Buenas noches, que tengas felices sueños")
        else:
            updatePerson(chat_id, Status.ESPERANDO_A_HACER_PING)
            context.bot.send_message(chat_id=chat_id, text="Me alegro de que estes bien")
    else:
        context.bot.send_message(chat_id=chat_id, text="Parece que no estás dado de alta")

def check(context):
    for p in getAllPeople():
        chat_id = p["chat_id"]
        elapsed = (datetime.now() - p["time"]).total_seconds()
        logger.info(f"Elapsed {int(elapsed)} seconds")
        if p["status"] == Status.ESPERANDO_A_HACER_PING:
            if elapsed > ASKING_TIME:
                logger.info("Preguntar que tal")
                context.bot.send_message(chat_id=chat_id, text="¿Como estas?")
                updatePerson(chat_id, Status.ESPERANDO_RESPUESTA)
            else:
                logger.info("Esperando para preguntar. No hacer nada")
        elif p["status"] == Status.ESPERANDO_RESPUESTA:
            if elapsed > ANSWER_TIME:
                logger.info("Enviar alarma")
                context.bot.send_message(chat_id=chat_id, text="Como no respondes voy a avisar a tu supervisor " + p["supervisor"])
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
                context.bot.send_message(chat_id=chat_id, text="Buenos días, ¿Qué tal has dormido?")
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

logger.info("ASKING_TIME: " + str(ASKING_TIME))
logger.info("ANSWER_TIME: " + str(ANSWER_TIME))
logger.info("BED_TIME: " + str(BED_TIME))
logger.info("DB_FILE: " + DB_FILE)

updater = Updater(os.environ['TELEGRAM_TOKEN'])
updater.dispatcher.add_handler(CommandHandler('supervise', supervise))
updater.dispatcher.add_handler(CommandHandler('supervisar', supervise))
updater.dispatcher.add_handler(CommandHandler('watchme', watchme))
updater.dispatcher.add_handler(CommandHandler('vigilame', watchme))
updater.dispatcher.add_handler(CommandHandler('bye', bye))
updater.dispatcher.add_handler(CommandHandler('adios', bye))
echo_handler = MessageHandler(Filters.text & (~Filters.command), message_received)
updater.dispatcher.add_handler(echo_handler)
updater.job_queue.run_repeating(check,5)
updater.start_polling()
updater.idle()
