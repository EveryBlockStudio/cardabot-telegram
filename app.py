from credentials import bot_token, wallet_url
from telegram.ext import Updater, CommandHandler
import logging
import requests
import json
from io import StringIO


# Set URL default value
url = wallet_url

def netinfo_callback(update, context):
    target = '/network/information'

    r = requests.get(url+target)

    if r.status_code == 200:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Here what we got...\n{r.text}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, no response from server :(")


def poolinfo_callback(update, context):
    html_reply = """
<b>Pool [{}] {}</b>
<i>{}</i>
    pledge: {} ada
    cost: {} ada
    margin: {}%

<b>Metrics</b>
    saturation: {}
    controlled stake: {}%
    produced blocks: {}
    rewards: {} ada
"""

    target = '/stake-pools?stake=0'
    r = requests.get(url+target)

    json_data = r.json()

    if context.args:
        ticker = ' '.join(context.args)
    else:
        ticker = 'EBS'

    gotpool = False
    lov = 1000000

    for pool in json_data:
        if 'metadata' in pool:
            if pool['metadata']['ticker']==ticker:
                gotpool = True
                pool_name = pool['metadata']['name']
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
                update.message.reply_html(html_reply.format(ticker, pool_name,desc,pledge_ada,cost_ada,margin_perc,saturat,rel_stake_perc,blocks,rewards_ada))
                break

    if not gotpool:
        update.message.reply_text(f"Sorry, I didn't find the {ticker} pool :(")


def start_callback(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, I'm a bot")


if __name__ == '__main__':
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

    updater.start_polling()
