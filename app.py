from credentials import bot_token, wallet_url
from reply_templates import *
from telegram.ext import Updater, CommandHandler
import logging
import requests
import random
from datetime import datetime


def get_progress_bar(perc):
    if perc < 10:
        return "▱▱▱▱▱▱▱▱▱▱"
    elif perc < 20:
        return "▰▱▱▱▱▱▱▱▱▱"
    elif perc < 30:
        return "▰▰▱▱▱▱▱▱▱▱"
    elif perc < 40:
        return "▰▰▰▱▱▱▱▱▱▱"
    elif perc < 50:
        return "▰▰▰▰▱▱▱▱▱▱"
    elif perc < 60:
        return "▰▰▰▰▰▱▱▱▱▱"
    elif perc < 70:
        return "▰▰▰▰▰▰▱▱▱▱"
    elif perc < 80:
        return "▰▰▰▰▰▰▰▱▱▱"
    elif perc < 90:
        return "▰▰▰▰▰▰▰▰▱▱"
    elif perc < 100:
        return "▰▰▰▰▰▰▰▰▰▱"

def beauty_time(timedelta):
    days = timedelta.days

    minute_limit = 60 * 60
    hour_limit = 60 * 60 * 24

    hours_intdiv = ((timedelta.seconds)/60)//60
    remaining_seconds = timedelta.seconds - (hours_intdiv * 60 * 60)
    remaining_min_intdiv = remaining_seconds//60

    if days == 0 and timedelta.seconds < minute_limit:
        return "{}m".format(int(timedelta.seconds//60))

    elif days == 0 and timedelta.seconds < hour_limit:
        return "{}h{}m".format(int(hours_intdiv), int(remaining_min_intdiv))

    else:
        if days > 1:
            return "{} days, {}h{}m".format(days, int(hours_intdiv), int(remaining_min_intdiv))
        else:
            return "{} day, {}h{}m".format(days, int(hours_intdiv), int(remaining_min_intdiv))

def lovelace_to_ada(value):
    """ Take a value in lovelace and returns in ADA (str) """

    # Define units
    K = 1000
    M = 1000000
    B = 1000000000
    units = {
        'no': 1,
        'K': K,
        'M': M,
        'B': B
    }

    # Calculate ADA from lovelaces
    ada_int = value//M

    # Select the best unit to show
    if ada_int/K < 1:
        best_unit = 'no'
    elif ada_int/M < 1:
        best_unit = 'K'
    elif ada_int/B < 1:
        best_unit = 'M'
    else:
        best_unit = 'B'

    # Transform int to str
    if best_unit == 'no':
        ada_str = '{}'.format(ada_int)
    else:
        ada_str = '{}{}'.format((ada_int/units[best_unit]), best_unit)

    return ada_str

def help_callback(update, context):
    update.message.reply_html(help_reply[language])

def change_lang_callback(update, context):
    global language

    # Extract language ID from message
    if context.args:
        user_lang = ' '.join(context.args).upper()
        if user_lang in supported_languages:
            language = user_lang
            update.message.reply_html(change_lang_reply[language])
        else:
            update.message.reply_html(f"I don't speak {user_lang} yet 😞")

    else:
        while True:
            random_lang = random.choice(supported_languages)
            if random_lang != language:
                language = random_lang
                break

        update.message.reply_html(change_lang_reply[language])


def epochinfo_callback(update, context):
    target = '/network/information'
    total_slot = 432000

    r = requests.get(url+target)

    if r.status_code == 200:

        json_data = r.json()

        # parse json
        current_epoch = json_data['network_tip']['epoch_number']
        current_slot = json_data['network_tip']['slot_number']
        next_epoch_time_str = json_data['next_epoch']['epoch_start_time']

        # get current time
        current_time =  datetime.utcnow()
        next_epoch_time = datetime.strptime(next_epoch_time_str, "%Y-%m-%dT%H:%M:%SZ")
        # calc diff time
        remaining_time = next_epoch_time - current_time

        # get perc bar and number
        perc = (current_slot / total_slot) * 100
        progress_bar = get_progress_bar(perc)

        update.message.reply_html(
            epoch_reply[language].format(
                progress_bar=progress_bar,
                perc=perc,
                current_epoch=current_epoch,
                current_slot=current_slot,
                remaining_time=beauty_time(remaining_time)))

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, no response from server :(")


def poolinfo_callback(update, context):
    update.message.reply_html(poolinfo_reply_wait[language])

    target = '/stake-pools?stake=0'
    r = requests.get(url+target)

    json_data = r.json()

    if context.args:
        typed_ticker = ' '.join(context.args)
    else:
        typed_ticker = 'EBS'

    gotpool = False

    for ind, pool in enumerate(json_data):
        if 'metadata' in pool and pool['metadata']['ticker'].upper() == typed_ticker.upper():
            gotpool = True
            pool_name = pool['metadata']['name']
            homepage = pool['metadata']['homepage']
            pool_ticker = pool['metadata']['ticker']
            desc = pool['metadata']['description']
            site = pool['metadata']['homepage']
            rank = ind
            pledge = pool['pledge']['quantity']
            pledge_ada = lovelace_to_ada(pledge)
            cost = pool['cost']['quantity']
            cost_ada = lovelace_to_ada(cost)
            margin_perc = pool['margin']['quantity']
            saturat = pool['metrics']['saturation']
            rel_stake_perc = pool['metrics']['relative_stake']['quantity']
            blocks = pool['metrics']['produced_blocks']['quantity']
            rewards = pool['metrics']['non_myopic_member_rewards']['quantity']
            rewards_ada = lovelace_to_ada(rewards)
            update.message.reply_html(
                poolinfo_reply[language].format(
                    quote=True,
                    ticker=pool_ticker,
                    pool_name=pool_name,
                    homepage=homepage,
                    desc=desc,
                    pool_rank=rank,
                    pledge_ada=pledge_ada,
                    cost_ada=cost_ada,
                    margin_perc=margin_perc))

                    # saturat=saturat,
                    # rel_stake_perc=rel_stake_perc,
                    # blocks=blocks,
                    # rewards_ada=rewards_ada
            break

    if not gotpool:
        update.message.reply_html(
            poolinfo_reply_error[language].format(
                ticker=typed_ticker))


def start_callback(update, context):
    update.message.reply_html(welcome_reply[language])


if __name__ == '__main__':
    # Global language definitions
    global supported_languages
    global language

    # Set URL default value
    url = wallet_url

    # Define languages
    supported_languages = ['EN','PT']
    language = 'PT'

    # set telegram object
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # set basic logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s %(message)s', level=logging.INFO)

    # start handler
    start_handler = CommandHandler('start', start_callback)
    dispatcher.add_handler(start_handler)

    # epochinfo handler
    epochinfo_handler = CommandHandler('epoch', epochinfo_callback)
    dispatcher.add_handler(epochinfo_handler)

    # poolinfo handler
    poolinfo_handler = CommandHandler('pool', poolinfo_callback)
    dispatcher.add_handler(poolinfo_handler)

    # language handler
    language_handler = CommandHandler('language', change_lang_callback)
    dispatcher.add_handler(language_handler)

    # help handler
    help_handler = CommandHandler('help', help_callback)
    dispatcher.add_handler(help_handler)


    updater.start_polling()
