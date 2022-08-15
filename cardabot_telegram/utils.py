import glob
import logging
import os
import subprocess
from collections import OrderedDict
from datetime import timedelta

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from cachetools import TTLCache, cached
from telegram.error import BadRequest

from . import database

cardabot_db = database.CardabotDB(url=os.environ.get("CARDABOT_API_URL"))


class Scheduler:
    queue = BackgroundScheduler()
    queue.start()  # start scheduler


def bech32_to_hex(pool_bech32):
    cwd = os.getcwd()
    cmd = "{}/bin/bech32 <<< {}".format(cwd, pool_bech32)
    process = subprocess.run(
        cmd, shell=True, executable="/bin/bash", capture_output=True
    )
    return process.stdout.strip().decode()


def calc_pool_saturation(pool_stake: int, circ_supply: int, n_opt: int) -> float:
    sat_point = circ_supply / n_opt
    return pool_stake / sat_point


def calc_expected_blocks(pool_stake, total_stake, d_param):
    blocks_in_epoch = 21600
    blocks_available_pools = blocks_in_epoch * (1 - float(d_param))
    expected_blocks = blocks_available_pools * (pool_stake / total_stake)

    return expected_blocks


def get_block_symbol(produced_blocks: int) -> str:
    if produced_blocks > 0:
        return " 🎉"
    return ""


def get_last_file(pathtofile: str) -> str:
    return max(glob.glob(f"{pathtofile}/*.json"), key=os.path.getmtime)


def get_saturation_icon(saturation: float) -> str:
    saturation = float(saturation)
    if saturation < 0.75:
        return "🟢"
    elif saturation < 1.0:
        return "🟡"

    return "🔴"


def get_progress_bar(percentage: float) -> str:
    assert percentage >= 0 and percentage <= 100
    pbar = {
        10: "[▰▱▱▱▱▱▱▱▱▱]",
        20: "[▰▰▱▱▱▱▱▱▱▱]",
        30: "[▰▰▰▱▱▱▱▱▱▱]",
        40: "[▰▰▰▰▱▱▱▱▱▱]",
        50: "[▰▰▰▰▰▱▱▱▱▱]",
        60: "[▰▰▰▰▰▰▱▱▱▱]",
        70: "[▰▰▰▰▰▰▰▱▱▱]",
        80: "[▰▰▰▰▰▰▰▰▱▱]",
        90: "[▰▰▰▰▰▰▰▰▰▱]",
        100: "[▰▰▰▰▰▰▰▰▰▰]",
    }
    tens, _ = divmod(int(percentage), 10)
    return pbar.get(tens * 10, "[▱▱▱▱▱▱▱▱▱▱]")


def fmt_time(remaning_time: timedelta, days_text: str) -> str:
    """Format a timedelta object to string in multiple languages."""
    hours, remainder = divmod(remaning_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    minute_limit, hour_limit = (60 * 60), (60 * 60 * 24)
    if remaning_time.days == 0 and remaning_time.seconds < minute_limit:
        return f"{minutes}m"
    elif remaning_time.days == 0 and remaning_time.seconds < hour_limit:
        return f"{hours}h{minutes}m"

    return f"{remaning_time.days} {days_text}, {hours}h{minutes}m"


def lovelace_to_ada(lovelace_value: float) -> float:
    """Take a value in lovelace and return it in ADA."""
    constant = 1e6
    return lovelace_value / constant


def fmt_ada(value: float) -> str:
    """Return string with formatted ADA value."""
    units = OrderedDict({"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3})

    for key in units.keys():
        if value > units.get(key):
            ada_fmt, best_unit = value / units.get(key), key
            return f"{float(ada_fmt):.2f}{best_unit}"

    return f"{float(value):.0f}"


@cached(cache=TTLCache(maxsize=2048, ttl=3600))
def get_admin_ids(bot, chat_id: int) -> list[int]:
    """Return a list of admin IDs for a given chat.

    Results are cached for 1 hour.

    """
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def user_is_adm(update, context):
    """Check if user is admin."""
    return update.effective_user.id in get_admin_ids(
        context.bot, update.message.chat_id
    )


def send_to_all(bot, chat_ids: list[str], text: str, parse_mode="Markdown"):
    """Send a message to several chats.

    Ignore invalid chat IDs.

    Args:
        bot: Telegram bot instance.
        chat_ids: List of chat IDs.
        text: Message text.

    """
    for chat_id in chat_ids:
        try:
            print("try to send to ", chat_id)
            bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except BadRequest as e:
            logging.debug(f"Invalid chat_id: {chat_id} ({repr(e)})")


def get_epoch_duration() -> int:
    """Return epoch length in seconds."""
    return 432000


def get_epoch_remaning_time() -> int:
    """Return epoch remaning time in seconds."""
    res = requests.get(
        os.path.join(cardabot_db.base_url, "epoch/"), headers=cardabot_db.headers
    )
    res.raise_for_status()

    return int(res.json().get("data").get("remaining_time"))


def isnumber(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def min_ada() -> float:
    """Return the minimum ADA value possible."""
    return 1e-6
