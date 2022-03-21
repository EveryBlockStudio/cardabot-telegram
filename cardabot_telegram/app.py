import logging
import os
import pymongo
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

from .callbacks import CardaBotCallbacks
from .replies import HTMLReplies


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s %(message)s", level=logging.INFO
    )

    load_dotenv(override=True)

    # mongodb config
    client = pymongo.MongoClient(os.environ.get("CONN_STR"))
    db = client.cardabotDatabase
    telegram_acc = db.account

    cbs = CardaBotCallbacks(
        mongodb_account=telegram_acc,
        blockfrost_headers={"project_id": os.environ.get("PROJECT_ID")},
        html_replies=HTMLReplies(),
    )

    # telegram bot handlers
    updater = Updater(os.environ.get("BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", cbs.start))
    dispatcher.add_handler(CommandHandler("pool", cbs.pool_info))
    dispatcher.add_handler(CommandHandler("language", cbs.change_language))
    dispatcher.add_handler(CommandHandler("setpool", cbs.change_default_pool))
    dispatcher.add_handler(CommandHandler("help", cbs.help))
    dispatcher.add_handler(CommandHandler("ebs", cbs.ebs))
    dispatcher.add_handler(CommandHandler("tip", cbs.tip))
    dispatcher.add_handler(CommandHandler("epoch", cbs.epoch_info))

    # start bot with pooling (use when running local)
    updater.start_polling()

    # Start bot with webhook (use in production)
    # updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=BOT_TOKEN)
    # updater.bot.setWebhook(APP_DOMAIN + BOT_TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT.
    updater.idle()
