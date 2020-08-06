from credentials import bot_token, wallet_url
from reply_templates import *
from telegram.ext import Updater, CommandHandler
import logging
import requests
import random

def lovelace_to_ada(value):
    """ Take a value in lovelace and returns in ADA (str) """
    # Define units
    K = 1000
    M = 1000000
    B = 1000000000

    # Calculate ADA from lovelaces
    ada_int = int(value/M)

    # Select

    # Transform int to str
    ada_str = ada_int

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


def netinfo_callback(update, context):
    target = '/network/information'

    r = requests.get(url+target)

    if r.status_code == 200:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Here what we got...\n{r.text}")
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
    lov = 1000000

    for pool in json_data:
        if 'metadata' in pool and pool['metadata']['ticker'].upper() == typed_ticker.upper():
            gotpool = True
            pool_name = pool['metadata']['name']
            pool_ticker = pool['metadata']['ticker']
            desc = pool['metadata']['description']
            site = pool['metadata']['homepage']
            pledge = pool['pledge']['quantity']
            pledge_ada = str(int(pledge /lov))
            cost = pool['cost']['quantity']
            cost_ada = str(int(cost/lov))
            margin_perc = pool['margin']['quantity']
            saturat = pool['metrics']['saturation']
            rel_stake_perc = pool['metrics']['relative_stake']['quantity']
            blocks = pool['metrics']['produced_blocks']['quantity']
            rewards = pool['metrics']['non_myopic_member_rewards']['quantity']
            rewards_ada = str(int(rewards/lov))
            update.message.reply_html(
                poolinfo_reply[language].format(
                    quote=True,
                    ticker=pool_ticker,
                    pool_name=pool_name,
                    desc=desc,
                    pledge_ada=pledge_ada,
                    cost_ada=cost_ada,
                    margin_perc=margin_perc,
                    saturat=saturat,
                    rel_stake_perc=rel_stake_perc,
                    blocks=blocks,
                    rewards_ada=rewards_ada))
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

    # netinfo handler
    netinfo_handler = CommandHandler('netinfo', netinfo_callback)
    dispatcher.add_handler(netinfo_handler)

    # poolinfo handler
    poolinfo_handler = CommandHandler('poolinfo', poolinfo_callback)
    dispatcher.add_handler(poolinfo_handler)

    # language handler
    language_handler = CommandHandler('language', change_lang_callback)
    dispatcher.add_handler(language_handler)

    # help handler
    help_handler = CommandHandler('help', help_callback)
    dispatcher.add_handler(help_handler)


    updater.start_polling()
