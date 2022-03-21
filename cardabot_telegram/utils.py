from collections import OrderedDict
import os
import subprocess
import glob
from cachetools import cached, TTLCache
import datetime
import pymongo


def bech32_to_hex(pool_bech32):
    cwd = os.getcwd()
    cmd = "{}/bin/bech32 <<< {}".format(cwd, pool_bech32)
    process = subprocess.run(
        cmd, shell=True, executable="/bin/bash", capture_output=True
    )
    return process.stdout.strip().decode()


def calc_pool_saturation(pool_stake, circ_supply, n_opt):
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
    # TODO: refactor to dictionary
    if percentage < 10:
        return "▱▱▱▱▱▱▱▱▱▱"
    elif percentage < 20:
        return "▰▱▱▱▱▱▱▱▱▱"
    elif percentage < 30:
        return "▰▰▱▱▱▱▱▱▱▱"
    elif percentage < 40:
        return "▰▰▰▱▱▱▱▱▱▱"
    elif percentage < 50:
        return "▰▰▰▰▱▱▱▱▱▱"
    elif percentage < 60:
        return "▰▰▰▰▰▱▱▱▱▱"
    elif percentage < 70:
        return "▰▰▰▰▰▰▱▱▱▱"
    elif percentage < 80:
        return "▰▰▰▰▰▰▰▱▱▱"
    elif percentage < 90:
        return "▰▰▰▰▰▰▰▰▱▱"
    elif percentage < 100:
        return "▰▰▰▰▰▰▰▰▰▱"
    return ""


def fmt_time(timedelta: datetime.timedelta, days_text: str) -> str:
    """Format a timedelta object to string in multiple languages."""
    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    minute_limit, hour_limit = (60 * 60), (60 * 60 * 24)
    if timedelta.days == 0 and timedelta.seconds < minute_limit:
        return f"{minutes}m"
    elif timedelta.days == 0 and timedelta.seconds < hour_limit:
        return f"{hours}h{minutes}m"

    return f"{timedelta.days} {days_text}, {hours}h{minutes}m"


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
