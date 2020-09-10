from credentials import bot_token, wallet_url
from reply_templates import *
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import logging
import requests
import random
from datetime import datetime
import json
import glob
import os

from mwt import MWT

def calc_pool_saturation(pool_stake, circ_supply, nOpt):
    sat_point = circ_supply/nOpt
    return pool_stake/sat_point

def calc_expected_blocks(pool_stake, total_stake, d_param):
    blocks_in_epoch = 21600
    blocks_available_pools = blocks_in_epoch * (1 - float(d_param))
    expected_blocks = blocks_available_pools * (pool_stake / total_stake)

    return expected_blocks

def get_block_symbol(produced_blocks):
    if produced_blocks > 0:
        return ' 🎉'
    else:
        return ''

def get_last_file(pathtofile):
    return max(
        glob.glob(f"{pathtofile}/*.json"), key=os.path.getmtime)

def get_saturat_symbol(saturat):
    saturat = float(saturat)
    if saturat < 0.75:
        return '🟢'
    elif saturat < 1.0:
        return '🟡'
    else:
        return '🔴'

def get_chat_filename(chat_id_int):
    cwd = os.getcwd()
    chat_id = str(chat_id_int)
    return cwd + '/chats/' + chat_id + '.json'


def get_chat_obj(chat_id_int):
    chat_filename = get_chat_filename(chat_id_int)

    # Create a new chat file if it doesn't exist
    if not os.path.exists(chat_filename):
        with open(chat_filename, 'w') as f:
            json_obj = {}
            json_obj['chat_id'] = chat_id_int
            json_obj['language'] = 'EN'
            json_obj['default_pool'] = 'EBS'

            json.dump(json_obj, f)

    # If the chat file already exist, just open it to return the object
    else:
        with open(chat_filename, 'r') as f:
            json_obj = json.load(f)

    return json_obj

def set_chat_obj(chat_obj):
    chat_filename = get_chat_filename(chat_obj['chat_id'])

    with open(chat_filename, 'w') as f:
        json.dump(chat_obj, f)

def set_language(chat_id_int, lang):
    chat = get_chat_obj(chat_id_int)
    chat['language'] = lang

    set_chat_obj(chat)

def set_default_pool(chat_id_int, pool):
    chat = get_chat_obj(chat_id_int)
    chat['default_pool'] = pool

    set_chat_obj(chat)


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


def beauty_time(timedelta, language):
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
            return "{} {}, {}h{}m".format(days, days_text[language], int(hours_intdiv), int(remaining_min_intdiv))
        else:
            return "{} {}, {}h{}m".format(days, day_text[language], int(hours_intdiv), int(remaining_min_intdiv))


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
        ada_str = '{:.0f}'.format(ada_int)
    else:
        ada_str = '{:.2f}{}'.format(float(ada_int/units[best_unit]), best_unit)

    return ada_str


def help_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']


    update.message.reply_html(help_reply[language])


@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

def change_lang_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']

    is_admin = False
    if update.effective_chat.type == 'group':
        if update.effective_user.id in get_admin_ids(
            context.bot,
            update.message.chat_id):
            is_admin = True
    else:
        is_admin = True

    if is_admin:
        # Extract language ID from message
        if context.args:
            user_lang = ' '.join(context.args).upper()
            if user_lang in supported_languages:
                language = user_lang
                set_language(update.effective_chat.id, language)
                update.message.reply_html(change_lang_reply[language])
            else:
                update.message.reply_html(f"I don't speak {user_lang} yet 😞")

        else:
            while True:
                random_lang = random.choice(supported_languages)
                if random_lang != language:
                    language = random_lang
                    break

            set_language(update.effective_chat.id, language)
            update.message.reply_html(change_lang_reply[language])

    else:
        update.message.reply_html(f"You're not authorized to do that 😞")

def change_default_pool_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']

    is_admin = False
    if update.effective_chat.type == 'group':
        if update.effective_user.id in get_admin_ids(
            context.bot,
            update.message.chat_id):
            is_admin = True
    else:
        is_admin = True

    if is_admin:
        # Extract language ID from message
        if context.args:
            user_pool = ' '.join(context.args).upper()

            set_default_pool(update.effective_chat.id, user_pool)
            update.message.reply_html(change_default_pool_reply[language])

        else:
            while True:
                random_lang = random.choice(supported_languages)
                if random_lang != language:
                    language = random_lang
                    break

            set_language(update.effective_chat.id, language)
            update.message.reply_html(change_lang_reply[language])

    else:
        update.message.reply_html(f"You're not authorized to do that 😞")


def epochinfo_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']

    total_slot = 432000
    total_supply = 45000000000000000

    target = '/network/information'
    target_params = '/network/parameters'

    r = requests.get(url+target)

    r_params = requests.get(url+target_params)

    if r.status_code == 200 and r_params.status_code == 200:

        json_data_netinfo = r.json()
        json_data_params = r_params.json()


        decentralisation_level = json_data_params['decentralization_level']['quantity']
        #print(decentralisation_level.keys())


        # parse json
        current_epoch = json_data_netinfo['network_tip']['epoch_number']
        current_slot = json_data_netinfo['network_tip']['slot_number']
        next_epoch_time_str = json_data_netinfo['next_epoch']['epoch_start_time']

        # get current time
        current_time =  datetime.utcnow()
        next_epoch_time = datetime.strptime(next_epoch_time_str, "%Y-%m-%dT%H:%M:%SZ")
        # calc diff time
        remaining_time = next_epoch_time - current_time

        # get perc bar and number
        perc = (current_slot / total_slot) * 100
        progress_bar = get_progress_bar(perc)


        # get information from db files
        cwd = os.getcwd()
        db_filename = get_last_file(cwd+'/db')
        with open(db_filename, 'r') as f:
            json_data_db = json.load(f)
        d_param = json_data_db['esPp']['decentralisationParam']
        reserves = json_data_db['esAccountState']['_reserves']
        treasury = json_data_db['esAccountState']['_treasury']
        total_live_stake = json_data_db['total_live_stake']
        total_active_stake = json_data_db['total_active_stake']
        circulating_supply =  total_supply - (reserves + treasury)

        perc_live_stake_circulating_supply = (total_live_stake / circulating_supply) * 100
        perc_active_stake_circulating_supply = (total_active_stake / circulating_supply) * 100

        # get current time
        current_time =  datetime.utcnow()
        last_update_time = datetime.strptime(
            json_data_db['timestamp'],
            "%Y-%m-%dT%H-%M-%S")
        # calc diff time of last update
        updated_time_ago = current_time - last_update_time


        update.message.reply_html(
            epoch_reply[language].format(
                progress_bar=progress_bar,
                perc=perc,
                current_epoch=current_epoch,
                current_slot=current_slot,
                remaining_time=beauty_time(remaining_time, language),
                decentralization=decentralisation_level,
                reserves=lovelace_to_ada(reserves),
                treasury=lovelace_to_ada(treasury),
                live_stake=lovelace_to_ada(total_live_stake),
                active_stake=lovelace_to_ada(total_active_stake),
                updated_time_ago=beauty_time(updated_time_ago, language),
                live_perc_supply=perc_live_stake_circulating_supply,
                active_perc_supply=perc_active_stake_circulating_supply,
                circulating_supply=lovelace_to_ada(circulating_supply)))
               #d_param=(1-float(d_param))*100,

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, no response from server :(")


def poolinfo_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']

    update.message.reply_html(poolinfo_reply_wait[language])

    target = '/stake-pools?stake=1000000'
    r = requests.get(url+target)

    json_data = r.json()

    if context.args:
        typed_ticker = ' '.join(context.args)
    else:
        typed_ticker = chat['default_pool']

    gotpool = False

    for ind, pool in enumerate(json_data):

        if 'metadata' in pool and pool['metadata']['ticker'].upper() == typed_ticker.upper():
            #print(ind,pool)

            #update.message.reply_html(pool)

            # Wallet data
            gotpool = True
            pool_name = pool['metadata']['name']
            homepage = pool['metadata']['homepage']
            pool_ticker = pool['metadata']['ticker']
            desc = pool['metadata']['description']

            pool_id = pool['id']
            site = pool['metadata']['homepage']
            rank = ind + 1
            pledge = pool['pledge']['quantity']
            cost = pool['cost']['quantity']
            margin_perc = pool['margin']['quantity']

            # Metrics from wallet
            #saturat = pool['metrics']['saturation']
            rel_stake_perc = pool['metrics']['relative_stake']['quantity']
            blocks = pool['metrics']['produced_blocks']['quantity']
            rewards = pool['metrics']['non_myopic_member_rewards']['quantity']

            try:
                # ledger-state data
                # get information from db files
                cwd = os.getcwd()
                db_filename = get_last_file(cwd+'/db')
                with open(db_filename, 'r') as f:
                    json_data_db = json.load(f)

                total_active_stake = json_data_db['total_active_stake']
                d_param = json_data_db['esPp']['decentralisationParam']

                stake_data = json_data_db['pools_stake'][pool_id]
                pool_live_stake = stake_data['live']['amount_stake']
                pool_n_live_delegators = stake_data['live']['n_delegators']

                pool_active_stake = stake_data['active']['amount_stake']
                pool_n_active_delegators = stake_data['active']['n_delegators']

            except:
                gotpool = False
                break

            # get current time
            current_time =  datetime.utcnow()
            last_update_time = datetime.strptime(
                json_data_db['timestamp'],
                "%Y-%m-%dT%H-%M-%S")
            # calc diff time of last update
            updated_time_ago = current_time - last_update_time

            # get expected blocks for the pool
            expected_blocks = calc_expected_blocks(
                pool_active_stake,
                total_active_stake,
                d_param)

            # calculate saturation from live stake
            total_supply = 45000000000000000
            reserves = json_data_db['esAccountState']['_reserves']
            treasury = json_data_db['esAccountState']['_treasury']
            circulating_supply =  total_supply - (reserves + treasury)
            saturat = calc_pool_saturation(
                pool_live_stake,
                circulating_supply,
                nOpt=150)


            update.message.reply_html(
                poolinfo_reply[language].format(
                    quote=True,
                    ticker=pool_ticker,
                    pool_id=pool_id,
                    pool_name=pool_name,
                    homepage=homepage,
                    desc=desc,
                    pool_rank=rank,
                    pledge=lovelace_to_ada(pledge),
                    cost=lovelace_to_ada(cost),
                    margin_perc=margin_perc,
                    saturat=saturat*100,
                    saturat_symbol=get_saturat_symbol(saturat),
                    rel_stake_perc=rel_stake_perc,
                    expected_blocks=expected_blocks,
                    blocks=blocks,
                    block_produced_symbol=get_block_symbol(blocks),
                    live_stake=lovelace_to_ada(pool_live_stake),
                    n_live_delegators=pool_n_live_delegators,
                    active_stake=lovelace_to_ada(pool_active_stake),
                    n_active_delegators=pool_n_active_delegators,
                    updated_time_ago=beauty_time(updated_time_ago,language)))
                    #rewards=lovelace_to_ada(rewards),
            break

    if not gotpool:
        update.message.reply_html(
            poolinfo_reply_error[language].format(
                ticker=typed_ticker))


def start_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']

    update.message.reply_html(welcome_reply[language])

def callback_minute(context):
    context.bot.send_message(chat_id='162210437',
                             text='One message every minute')


if __name__ == '__main__':
    # Global language definitions
    global supported_languages


    # Set URL default value
    url = wallet_url

    # Define languages
    supported_languages = ['EN', 'PT', 'KR', 'JP']


    # Create cardabot persistence locally (DictPersistence)
    #cardabot_persistence = PicklePersistence()



    # set telegram object
    updater = Updater(
        bot_token,
        #persistence=cardabot_persistence,
        use_context=True)
    dispatcher = updater.dispatcher


    # start job queue for recurrent tasks
    #j = updater.job_queue

    # put job on queue
    #job_minute = j.run_repeating(callback_minute, interval=60, first=30)

    # set basic logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s %(message)s',
        level=logging.INFO)

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

    # default pool handler
    default_pool_handler = CommandHandler('setpool', change_default_pool_callback)
    dispatcher.add_handler(default_pool_handler)

    # help handler
    help_handler = CommandHandler('help', help_callback)
    dispatcher.add_handler(help_handler)


    updater.start_polling()



    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
