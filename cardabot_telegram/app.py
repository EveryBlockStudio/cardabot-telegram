import argparse
import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

load_dotenv(override=True)
from . import utils
from .callbacks import CardaBotCallbacks

if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s %(message)s", level=logging.INFO
    )

    # telegram bot handlers
    updater = Updater(os.environ.get("BOT_TOKEN"), use_context=True)
    disp = updater.dispatcher
    cbs = CardaBotCallbacks()

    # schedule recurring jobs
    start_date = datetime.now() + timedelta(seconds=utils.get_epoch_remaning_time())
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        cbs.end_of_epoch_task,
        "interval",
        seconds=utils.get_epoch_duration(),
        start_date=start_date,
        args=[updater.bot],
        id="end_of_epoch_task",
    )
    scheduler.start()

    # telegram bot commands
    disp.add_handler(CommandHandler("start", cbs.start, run_async=True))
    disp.add_handler(CommandHandler("pool", cbs.pool_info, run_async=True))
    disp.add_handler(CommandHandler("language", cbs.change_language, run_async=True))
    disp.add_handler(CommandHandler("setpool", cbs.change_default_pool, run_async=True))
    disp.add_handler(CommandHandler("help", cbs.help, run_async=True))
    disp.add_handler(CommandHandler("ebs", cbs.ebs, run_async=True))
    disp.add_handler(CommandHandler("tip", cbs.tip))
    disp.add_handler(CommandHandler("epoch", cbs.epoch_info, run_async=True))
    disp.add_handler(CommandHandler("pots", cbs.pots, run_async=True))
    disp.add_handler(CommandHandler("netparams", cbs.netparams, run_async=True))
    disp.add_handler(CommandHandler("netstats", cbs.netstats, run_async=True))
    disp.add_handler(CommandHandler("connect", cbs.connect, run_async=True))
    disp.add_handler(CommandHandler("alert", cbs.alert, run_async=True))

    # parse command line arguments and start the bot accordingly
    parser = argparse.ArgumentParser()
    parser.add_argument("--prod", help="Run in production mode", action="store_true")
    args = parser.parse_known_args()

    if args[0].prod:
        updater.start_webhook(  # start bot with webhook (use in production)
            listen="0.0.0.0",
            port=int(os.environ.get("PORT")),
            url_path=os.environ.get("BOT_TOKEN"),
            webhook_url=os.environ.get("APP_DOMAIN") + os.environ.get("BOT_TOKEN"),
        )
    else:
        updater.start_polling()  # start bot with pooling (use when running local)

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT.
    updater.idle()
