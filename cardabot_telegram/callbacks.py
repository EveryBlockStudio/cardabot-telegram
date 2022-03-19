import random
import os
from datetime import datetime, timedelta
import time
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from . import utils
from . import reply_templates


class CardaBotCallbacks:
    def __init__(self, mongodb_account, blockfrost_headers) -> None:
        self.mongodb_account = mongodb_account
        self.blockfrost_headers = blockfrost_headers

    def help(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        update.message.reply_html(reply_templates.help_reply[language])

    def change_lang(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        is_admin = False
        if update.effective_chat.type == "group":
            if update.effective_user.id in utils.get_admin_ids(
                context.bot, update.message.chat_id
            ):
                is_admin = True
        else:
            is_admin = True

        if is_admin:
            # Extract language ID from message
            if context.args:
                user_lang = " ".join(context.args).upper()
                if user_lang in reply_templates.supported_languages:
                    language = user_lang
                    utils.set_language(
                        update.effective_chat.id, language, self.mongodb_account
                    )
                    update.message.reply_html(
                        reply_templates.change_lang_reply[language]
                    )
                else:
                    update.message.reply_html(f"I don't speak {user_lang} yet 😞")

            else:
                while True:
                    random_lang = random.choice(reply_templates.supported_languages)
                    if random_lang != language:
                        language = random_lang
                        break

                utils.set_language(
                    update.effective_chat.id, language, self.mongodb_account
                )
                update.message.reply_html(reply_templates.change_lang_reply[language])

        else:
            update.message.reply_html(f"You're not authorized to do that 😞")

    def change_default_pool(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        is_admin = False
        if update.effective_chat.type == "group":
            if update.effective_user.id in utils.get_admin_ids(
                context.bot, update.message.chat_id
            ):
                is_admin = True
        else:
            is_admin = True

        if is_admin:
            # Extract language ID from message
            if context.args:
                user_pool = " ".join(context.args).upper()

                utils.set_default_pool(
                    update.effective_chat.id, user_pool, self.mongodb_account
                )
                update.message.reply_html(
                    reply_templates.change_default_pool_reply[language]
                )

            else:
                while True:
                    random_lang = random.choice(reply_templates.supported_languages)
                    if random_lang != language:
                        language = random_lang
                        break

                utils.set_language(
                    update.effective_chat.id, language, self.mongodb_account
                )
                update.message.reply_html(reply_templates.change_lang_reply[language])

        else:
            update.message.reply_html(f"You're not authorized to do that 😞")

    def epochinfo(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        total_blocks = 21600
        total_supply = 45000000000000000

        target = "/epochs/latest"

        r = requests.get(
            os.environ.get("BLOCKFROST_URL") + target, headers=self.blockfrost_headers
        )

        if r.status_code == 200:

            json_data_netinfo = r.json()

            # parse json
            current_epoch = int(json_data_netinfo["epoch"])
            current_block = int(json_data_netinfo["block_count"])
            next_epoch_time = int(json_data_netinfo["end_time"])

            # get current time
            current_time = int(datetime.utcnow().timestamp())

            # calc diff time
            remaining_time_int = next_epoch_time - current_time
            remaining_time = timedelta(seconds=remaining_time_int)

            # get perc bar and number
            perc = (current_block / total_blocks) * 100
            progress_bar = utils.get_progress_bar(perc)

            total_active_stake = int(json_data_netinfo["active_stake"])

            update.message.reply_html(
                reply_templates.epoch_reply[language].format(
                    progress_bar=progress_bar,
                    perc=perc,
                    current_epoch=current_epoch,
                    current_block=current_block,
                    remaining_time=utils.fmt_time(
                        remaining_time,
                        # language,
                        reply_templates.days_text[language],
                    ),
                    active_stake=utils.fmt_ada(
                        utils.lovelace_to_ada(total_active_stake)
                    ),
                )
            )

        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, no response from server :(",
            )

    def ebs(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        update.message.reply_text(
            "Subscribe to us on Twitter and Instagram:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="on Twitter", url="https://twitter.com/EveryBlockStd"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="on Instagram",
                            url="https://instagram.com/EveryBlockStudio",
                        )
                    ],
                ]
            ),
        )

        return ""

    def tip(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        chat_id = update.effective_chat.id
        language = chat["language"]

        message = context.bot.send_message(
            chat_id=chat_id,
            text="Click the button below to sign your transaction using Nami wallet: ⬇️",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔑 Sign Tx",
                            url="https://www.figma.com/proto/RBHzvMaK7XrasZ6Vv0JOwM/Untitled?node-id=0%3A3&scaling=scale-down&page-id=0%3A1&hide-ui=1",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📖 Learn more",
                            url="https://instagram.com/EveryBlockStudio",
                        )
                    ],
                ]
            ),
        )

        time.sleep(10)

        message.edit_text(
            text="✅ Your transaction was submitted!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Check Tx on CardanoScan",
                            url="https://cardanoscan.io/transaction/5ce7e1af847acadb7f954cd15db267566427020648b9cae9e9ffcc23d920808d",
                        )
                    ],
                ]
            ),
        )

        return ""

    def poolinfo(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        update.message.reply_html("""Temporarily disabled, sorry 😞""")

        return ""

        update.message.reply_html(poolinfo_reply_wait[language])

        target = "/stake-pools?stake=1000000"
        r = requests.get(BLOCKFROST_URL + target)

        json_data = r.json()

        if context.args:
            typed_ticker = " ".join(context.args)
        else:
            typed_ticker = chat["default_pool"]

        gotpool = False

        for ind, pool in enumerate(json_data):

            if (
                "metadata" in pool
                and pool["metadata"]["ticker"].upper() == typed_ticker.upper()
            ):
                # print(ind,pool)

                # update.message.reply_html(pool)

                # Wallet data
                gotpool = True
                pool_name = pool["metadata"]["name"]
                homepage = pool["metadata"]["homepage"]
                pool_ticker = pool["metadata"]["ticker"]
                desc = pool["metadata"]["description"]

                pool_id_bech32 = pool["id"]
                pool_id = bech32_to_hex(pool_id_bech32)

                site = pool["metadata"]["homepage"]
                rank = ind + 1
                pledge = pool["pledge"]["quantity"]
                cost = pool["cost"]["quantity"]
                margin_perc = pool["margin"]["quantity"]

                # Metrics from wallet
                # saturat = pool['metrics']['saturation']
                rel_stake_perc = pool["metrics"]["relative_stake"]["quantity"]
                blocks = pool["metrics"]["produced_blocks"]["quantity"]
                rewards = pool["metrics"]["non_myopic_member_rewards"]["quantity"]

                try:
                    # ledger-state data
                    # get information from db files
                    cwd = os.getcwd()
                    db_filename = get_last_file(cwd + "/db")
                    with open(db_filename, "r") as f:
                        json_data_db = json.load(f)

                    total_active_stake = json_data_db["total_active_stake"]
                    d_param = json_data_db["esPp"]["decentralisationParam"]

                    stake_data = json_data_db["pools_stake"][pool_id]
                    pool_live_stake = stake_data["live"]["amount_stake"]
                    pool_n_live_delegators = stake_data["live"]["n_delegators"]

                    pool_active_stake = stake_data["active"]["amount_stake"]
                    pool_n_active_delegators = stake_data["active"]["n_delegators"]

                except:
                    gotpool = False
                    break

                # get current time
                current_time = datetime.utcnow()
                last_update_time = datetime.strptime(
                    json_data_db["timestamp"], "%Y-%m-%dT%H-%M-%S"
                )
                # calc diff time of last update
                updated_time_ago = current_time - last_update_time

                # get expected blocks for the pool
                expected_blocks = calc_expected_blocks(
                    pool_active_stake, total_active_stake, d_param
                )

                # calculate saturation from live stake
                total_supply = 45000000000000000
                reserves = json_data_db["esAccountState"]["_reserves"]
                treasury = json_data_db["esAccountState"]["_treasury"]
                circulating_supply = total_supply - (reserves + treasury)
                saturat = calc_pool_saturation(
                    pool_live_stake, circulating_supply, nOpt=500
                )

                update.message.reply_html(
                    poolinfo_reply[language].format(
                        quote=True,
                        ticker=pool_ticker,
                        pool_id=pool_id,
                        pool_name=pool_name,
                        homepage=homepage,
                        desc=desc,
                        pool_rank=rank,
                        pledge=lovelace_to_ada(pledge),  # update this later
                        cost=lovelace_to_ada(cost),  # update this later
                        margin_perc=margin_perc,
                        saturat=saturat * 100,
                        saturat_symbol=get_saturat_symbol(saturat),
                        rel_stake_perc=rel_stake_perc,
                        expected_blocks=expected_blocks,
                        blocks=blocks,
                        block_produced_symbol=get_block_symbol(blocks),
                        live_stake=lovelace_to_ada(
                            pool_live_stake
                        ),  # update this later
                        n_live_delegators=pool_n_live_delegators,
                        active_stake=lovelace_to_ada(
                            pool_active_stake
                        ),  # update this later
                        n_active_delegators=pool_n_active_delegators,
                        updated_time_ago=beauty_time(updated_time_ago, language),
                    )
                )
                break

        if not gotpool:
            update.message.reply_html(
                poolinfo_reply_error[language].format(ticker=typed_ticker)
            )

    def start(self, update, context):
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )
        language = chat["language"]

        update.message.reply_html(reply_templates.welcome_reply[language])

    def callback_minute(self, context):
        context.bot.send_message(chat_id="162210437", text="One message every minute")
