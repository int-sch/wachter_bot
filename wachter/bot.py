import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler

from custom_filters import filter_bot_added
import actions
import os
from log_handler import ErrorBroadcastHandler


logger = logging.getLogger(__name__)


def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", actions.on_help_command))
    dp.add_error_handler(actions.on_error)

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members & filter_bot_added,
                                  actions.on_new_chat_member, pass_job_queue=True))
    dp.add_handler(MessageHandler(Filters.entity('hashtag'), actions.on_hashtag_message,
                                  pass_job_queue=True, edited_updates=True, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.forwarded, actions.on_forward, pass_job_queue=True))

    dp.add_handler(CommandHandler('start', actions.on_start_command, pass_user_data=True))
    dp.add_handler(CommandHandler('skip', actions.on_skip_command, allow_edited=True, pass_job_queue=True))
    dp.add_handler(CallbackQueryHandler(actions.on_button_click, pass_user_data=True))
    dp.add_handler(MessageHandler((Filters.text | Filters.entity), actions.on_message, edited_updates=True, pass_user_data=True, pass_job_queue=True))
    
    error_chat_id = os.environ.get('TELEGRAM_ERROR_CHAT_ID')
    if error_chat_id is not None:
        for handler in logging.getLogger().handlers:
            logging.getLogger().removeHandler(handler)
        logging.getLogger().addHandler(ErrorBroadcastHandler(lambda msg: dp.bot.send_message(
            text=msg,
            chat_id=error_chat_id,
            disable_notification=True,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        ),))

    logger.error('started')

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
