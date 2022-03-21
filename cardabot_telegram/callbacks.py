import os
from datetime import datetime, timedelta
import time
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from . import utils
from . import replies


class CardaBotCallbacks:
    def __init__(
        self,
        mongodb_account,
        blockfrost_headers: dict,
        html_replies: replies.HTMLReplies,
    ) -> None:
        self.mongodb_account = mongodb_account
        self.blockfrost_headers = blockfrost_headers
        self.html_replies = html_replies

    def help(self, update, context) -> None:
        chat = utils.get_chat_obj_database(
            update.effective_chat.id, self.mongodb_account
        )

        out = self.html_replies.set_language(chat["language"])

        update.message.reply_html(
            self.html_replies.reply(
                "help.html", supported_languages=self.html_replies.supported_languages
            )
        )

    def change_language(self, update, context) -> None:
        chat_id = update.effective_chat.id
        chat = utils.get_chat_obj_database(chat_id, self.mongodb_account)
        self.html_replies.set_language(chat["language"])

        if update.effective_chat.type == "group":
            if not utils.user_is_adm(update, context):
                update.message.reply_html(
                    self.html_replies.reply("not_authorized.html")
                )
                return

        if not context.args:
            # TODO: define the expected behaviour when lang is not selected.
            # Suggestion: set lang to the "default" language (EN).
            return

        user_lang = "".join(context.args).upper()
        if self.html_replies.set_language(user_lang):
            utils.set_user_language(chat_id, user_lang, self.mongodb_account)
            update.message.reply_html(
                self.html_replies.reply("change_lang_success.html")
            )
        else:
            update.message.reply_html(
                self.html_replies.reply("change_lang_error.html", user_lang=user_lang)
            )

    def change_default_pool(self, update, context) -> None:
        if update.effective_chat.type == "group":
            if not utils.user_is_adm(update, context):
                update.message.reply_html(
                    self.html_replies.reply("not_authorized.html")
                )
                return

        chat_id = update.effective_chat.id
        if not context.args:
            # if there are no args, change default pool to `EBS`
            default_pool = "EBS"
            utils.set_default_pool(chat_id, default_pool, self.mongodb_account)
            update.message.reply_html(
                # TODO: modify template to pass pool ticker as argument
                self.html_replies.reply("change_default_pool_success.html")
            )
            return

        user_pool = "".join(context.args).upper()
        utils.set_default_pool(chat_id, user_pool, self.mongodb_account)
        update.message.reply_html(
            self.html_replies.reply("change_default_pool_success.html")
        )

    def epoch_info(self, update, context) -> None:
        target = "/epochs/latest"
        response = requests.get(
            os.environ.get("BLOCKFROST_URL") + target, headers=self.blockfrost_headers
        )

        if not response.ok:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, no response from server :(",
            )
            return

        data = response.json()
        current_time = int(datetime.utcnow().timestamp())
        remaining_time = timedelta(seconds=int(data["end_time"]) - current_time)

        total_blocks = 21600  # total blocks/epoch
        current_block = int(data["block_count"])
        blocks_percentage = (current_block / total_blocks) * 100

        template_args = {
            "progress_bar": utils.get_progress_bar(blocks_percentage),
            "perc": blocks_percentage,
            "current_epoch": int(data["epoch"]),
            "current_block": current_block,
            "remaining_time": utils.fmt_time(
                remaining_time,
                self.html_replies.reply("days.html"),
            ),
            "active_stake": utils.fmt_ada(
                utils.lovelace_to_ada(int(data["active_stake"]))
            ),
        }

        update.message.reply_html(
            self.html_replies.reply("epoch_info.html", **template_args)
        )

    def ebs(self, update, context) -> None:
        update.message.reply_text(
            "🔔 Follow us on social media!",
            #
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="✨ Twitter ✨", url="https://twitter.com/EveryBlockStd"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="✨ Instagram ✨",
                            url="https://instagram.com/EveryBlockStudio",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="✨ LinkedIn ✨",
                            url="https://www.linkedin.com/company/everyblock-studio/",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="✨ Telegram ✨",
                            url="https://t.me/EveryBlockStudio",
                        )
                    ],
                ]
            ),
        )

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
