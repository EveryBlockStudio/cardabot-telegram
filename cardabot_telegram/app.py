import logging
import os
from functools import partial

import pymongo
from dotenv import load_dotenv
import telegram
from telegram.ext import Updater, CommandHandler

from .bot_callbacks import CardaBotCallbacks


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s %(message)s", level=logging.INFO
    )

    load_dotenv(override=True)

    # mongodb config
    client = pymongo.MongoClient(os.environ.get("CONN_STR"))
    db = client.cardabotDatabase
    telegram_acc = db.account

    # telegram bot handlers
    updater = Updater(os.environ.get("BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher

    cbs = CardaBotCallbacks(
        mongodb_account=telegram_acc,
        blockfrost_headers={"project_id": os.environ.get("PROJECT_ID")},
    )

    dispatcher.add_handler(CommandHandler("start", cbs.start))
    dispatcher.add_handler(CommandHandler("pool", cbs.poolinfo))
    dispatcher.add_handler(CommandHandler("language", cbs.change_lang))
    dispatcher.add_handler(CommandHandler("setpool", cbs.change_default_pool))
    dispatcher.add_handler(CommandHandler("help", cbs.help))
    dispatcher.add_handler(CommandHandler("ebs", cbs.ebs))
    dispatcher.add_handler(CommandHandler("tip", cbs.tip))
    dispatcher.add_handler(CommandHandler("epoch", cbs.epochinfo))

    # start bot with pooling (use when running local)
    updater.start_polling()

    # Start bot with webhook (use in production)
    # updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=BOT_TOKEN)
    # updater.bot.setWebhook(APP_DOMAIN + BOT_TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT.
    updater.idle()