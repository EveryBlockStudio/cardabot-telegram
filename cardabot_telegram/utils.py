from collections import OrderedDict
import os
import subprocess
import glob
from cachetools import cached, TTLCache

import telegram


def bech32_to_hex(pool_bech32):
    cwd = os.getcwd()
    cmd = "{}/bin/bech32 <<< {}".format(cwd, pool_bech32)
    process = subprocess.run(
        cmd, shell=True, executable="/bin/bash", capture_output=True
    )
    return process.stdout.strip().decode()


def calc_pool_saturation(pool_stake, circ_supply, nOpt):
    sat_point = circ_supply / nOpt
    return pool_stake / sat_point


def calc_expected_blocks(pool_stake, total_stake, d_param):
    blocks_in_epoch = 21600
    blocks_available_pools = blocks_in_epoch * (1 - float(d_param))
    expected_blocks = blocks_available_pools * (pool_stake / total_stake)

    return expected_blocks


def get_block_symbol(produced_blocks):
    if produced_blocks > 0:
        return " 🎉"
    return ""


def get_last_file(pathtofile):
    return max(glob.glob(f"{pathtofile}/*.json"), key=os.path.getmtime)


def get_saturation_icon(saturation: float):
    saturation = float(saturation)

    if saturation < 0.75:
        return "🟢"
    elif saturation < 1.0:
        return "🟡"

    return "🔴"


def get_chat_obj(chat_id_int, telegram_acc):

    # Create a new chat file if it doesn't exist
    res = telegram_acc.find_one({"chat_id": chat_id_int})

    if not res:  # if the db response is empty
        json_obj = {}
        json_obj["chat_id"] = chat_id_int
        json_obj["language"] = "EN"
        json_obj["default_pool"] = "EBS"

        telegram_acc.insert_one(json_obj)

    # If the chat file already exist, just open it to return the object
    else:
        json_obj = res

    return json_obj


def set_language(chat_id_int, lang, telegram_acc):
    # first ensure that the user has an entry in db
    chat = get_chat_obj(chat_id_int, telegram_acc)

    # build the query and the new value
    query = {"chat_id": chat_id_int}
    newvalue = {"$set": {"language": lang}}

    # update the entry
    telegram_acc.update_one(query, newvalue)


def set_default_pool(chat_id_int, pool, telegram_acc):
    # first ensure that the user has an entry in db
    chat = get_chat_obj(chat_id_int, telegram_acc)

    # build the query and the new value
    query = {"chat_id": chat_id_int}
    newvalue = {"$set": {"default_pool": pool}}

    # update the entry
    telegram_acc.update_one(query, newvalue)


def get_progress_bar(percentage):
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


def beauty_time(timedelta, language, days_text, day_text):
    days = timedelta.days

    minute_limit = 60 * 60
    hour_limit = 60 * 60 * 24

    hours_intdiv = ((timedelta.seconds) / 60) // 60
    remaining_seconds = timedelta.seconds - (hours_intdiv * 60 * 60)
    remaining_min_intdiv = remaining_seconds // 60

    if days == 0 and timedelta.seconds < minute_limit:
        return "{}m".format(int(timedelta.seconds // 60))

    elif days == 0 and timedelta.seconds < hour_limit:
        return "{}h{}m".format(int(hours_intdiv), int(remaining_min_intdiv))

    else:
        if days > 1:
            return "{} {}, {}h{}m".format(
                days, days_text[language], int(hours_intdiv), int(remaining_min_intdiv)
            )
        else:
            return "{} {}, {}h{}m".format(
                days, day_text[language], int(hours_intdiv), int(remaining_min_intdiv)
            )


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
