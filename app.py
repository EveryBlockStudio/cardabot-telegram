from reply_templates import *
from telegram.ext import Updater, CommandHandler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import requests
import random
from datetime import datetime, timedelta
import json
import glob
import os
import subprocess
import pymongo
from dotenv import load_dotenv
from mwt import MWT
import time

def bech32_to_hex(pool_bech32):
    cwd = os.getcwd()
    cmd = "{}/bin/bech32 <<< {}".format(cwd, pool_bech32)
    process = subprocess.run(cmd, shell=True, executable='/bin/bash', capture_output=True)
    return process.stdout.strip().decode()

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
        

def get_chat_obj(chat_id_int):

    # Create a new chat file if it doesn't exist
    res = telegram_acc.find_one({"chat_id": chat_id_int})

    if not res: #if the db response is empty
        json_obj = {}
        json_obj['chat_id'] = chat_id_int
        json_obj['language'] = 'EN'
        json_obj['default_pool'] = 'EBS'

        telegram_acc.insert_one(json_obj)

    # If the chat file already exist, just open it to return the object
    else:
        json_obj = res

    return json_obj
    

def set_language(chat_id_int, lang):
    # first ensure that the user has an entry in db
    chat = get_chat_obj(chat_id_int)
    
    # build the query and the new value
    query = { "chat_id": chat_id_int }
    newvalue = { "$set": { "language": lang} }

    # update the entry
    telegram_acc.update_one(query, newvalue)


def set_default_pool(chat_id_int, pool):
    # first ensure that the user has an entry in db
    chat = get_chat_obj(chat_id_int)
    
    # build the query and the new value
    query = { "chat_id": chat_id_int }
    newvalue = { "$set": { "default_pool": pool} }

    # update the entry
    telegram_acc.update_one(query, newvalue)


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

    total_blocks = 21600
    total_supply = 45000000000000000
   
    target = '/epochs/latest'

    r = requests.get(BLOCKFROST_URL+target, headers=blockfrost_header)

    if r.status_code == 200:

        json_data_netinfo = r.json()

        # parse json
        current_epoch = int(json_data_netinfo['epoch'])
        current_block = int(json_data_netinfo['block_count'])
        next_epoch_time = int(json_data_netinfo['end_time'])

        # get current time
        current_time =  int(datetime.utcnow().timestamp())
        
        # calc diff time
        remaining_time_int = next_epoch_time - current_time
        remaining_time = timedelta(seconds=remaining_time_int)

        # get perc bar and number
        perc = (current_block / total_blocks) * 100
        progress_bar = get_progress_bar(perc)


        total_active_stake = int(json_data_netinfo['active_stake'])
        
        update.message.reply_html(
            epoch_reply[language].format(
                progress_bar=progress_bar,
                perc=perc,
                current_epoch=current_epoch,
                current_block=current_block,
                remaining_time=beauty_time(remaining_time, language),
                active_stake=lovelace_to_ada(total_active_stake),
                ))

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, no response from server :(")

def ebs_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']


    update.message.reply_text(
        'Subscribe to us on Twitter and Instagram:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='on Twitter', url='https://twitter.com/EveryBlockStd')],
            [InlineKeyboardButton(text='on Instagram', url='https://instagram.com/EveryBlockStudio')],
        ])
        )
        
    
    

    return ''
    
    
def tip_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    chat_id = update.effective_chat.id
    language = chat['language']

    message = context.bot.send_message(chat_id=chat_id, text='Click the button below to sign your transaction using Nami wallet: ⬇️',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='🔑 Sign Tx', url='https://www.figma.com/proto/RBHzvMaK7XrasZ6Vv0JOwM/Untitled?node-id=0%3A3&scaling=scale-down&page-id=0%3A1&hide-ui=1')],
            [InlineKeyboardButton(text='📖 Learn more', url='https://instagram.com/EveryBlockStudio')],
        ])
        )


    time.sleep(10)
    
    message.edit_text(
        text='✅ Your transaction was submitted!', 
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Check Tx on CardanoScan', url='https://cardanoscan.io/transaction/5ce7e1af847acadb7f954cd15db267566427020648b9cae9e9ffcc23d920808d')],
            ])
        )

    return ''
    
def poolinfo_callback(update, context):
    chat = get_chat_obj(update.effective_chat.id)
    language = chat['language']
    
    update.message.reply_html('''Temporarily disabled, sorry 😞''')
        
    
    return ''
    
    update.message.reply_html(poolinfo_reply_wait[language])

    target = '/stake-pools?stake=1000000'
    r = requests.get(BLOCKFROST_URL+target)

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

            pool_id_bech32 = pool['id']
            pool_id = bech32_to_hex(pool_id_bech32)

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
                nOpt=500)


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

    load_dotenv(override=True)
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    BLOCKFROST_URL = os.environ.get("BLOCKFROST_URL")
    PROJECT_ID = os.environ.get("PROJECT_ID")
    CONN_STR = os.environ.get("CONN_STR")
    PORT = int(os.environ.get("PORT"))
    APP_DOMAIN = os.environ.get("APP_DOMAIN")


    # Set header for blockfrost calls
    blockfrost_header = {'project_id': PROJECT_ID}
    

    # Define languages
    supported_languages = ['EN', 'PT', 'KR', 'JP']

    # Set a with mongodb
    client = pymongo.MongoClient(CONN_STR)
    db = client.cardabotDatabase
    telegram_acc = db.account

    # set telegram object
    updater = Updater(
        BOT_TOKEN,
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
    
    # ebs handler
    ebs_handler = CommandHandler('ebs', ebs_callback)
    dispatcher.add_handler(ebs_handler)
    
    # tip handler
    tip_handler = CommandHandler('tip', tip_callback)
    dispatcher.add_handler(tip_handler)


    #updater.start_polling()

    # Start the Bot with webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook(APP_DOMAIN + BOT_TOKEN)



    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
