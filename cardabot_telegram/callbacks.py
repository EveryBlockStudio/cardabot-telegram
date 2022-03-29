import os
from datetime import datetime, timedelta
import time
import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, chat

from . import mongodb
from . import utils
from . import replies
from . import graphql_client


class CardaBotCallbacks:
    def __init__(
        self,
        mongodb: mongodb.MongoDatabase,
        html_replies: replies.HTMLReplies,
        graphql_client: graphql_client.GraphQLClient,
    ) -> None:
        self.mongodb = mongodb
        self.html_replies = html_replies
        self.gql = graphql_client

    def _set_html_reply_lang(self, chat_id: int):
        """Set HTML template language to current chat language."""
        language = self.mongodb.get_chat_language(chat_id)
        self.html_replies.set_language(language)

    def _inform_error(self, context, chat_id):
        context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, something went wrong 😔",
        )

    def _setup_callback(func):
        """Decorator to setup callback configs and handle specific exceptions."""

        def callback(self, update, context):
            try:
                chat_id = update.effective_chat.id
                self._set_html_reply_lang(chat_id)
                func(self, update, context)

            # invalid GraphQL responses can cause KeyErrors, TypeErros, AttributeErrors,
            # and HTTPErrors depending on how you make the call or try to access the
            # response dictionary
            except Exception as e:
                self._inform_error(context, chat_id)
                logging.exception(e)
                return

        return callback

    def help(self, update, context) -> None:
        chat_id = update.effective_chat.id
        self._set_html_reply_lang(chat_id)

        update.message.reply_html(
            self.html_replies.reply(
                "help.html", supported_languages=self.html_replies.supported_languages
            )
        )

    def change_language(self, update, context) -> None:
        chat_id = update.effective_chat.id
        self._set_html_reply_lang(chat_id)

        if update.effective_chat.type == "group":
            if not utils.user_is_adm(update, context):
                update.message.reply_html(
                    self.html_replies.reply("not_authorized.html")
                )
                return

        if not context.args:
            # set language to default when no args are passed by the user
            default_language = self.html_replies.default_lang
            self.html_replies.set_language(default_language)
            self.mongodb.set_chat_language(chat_id, default_language)

            update.message.reply_html(
                self.html_replies.reply("change_lang_success.html")
            )
            return

        user_lang = "".join(context.args).upper()
        if self.html_replies.set_language(user_lang):
            self.mongodb.set_chat_language(chat_id, user_lang)
            update.message.reply_html(
                self.html_replies.reply("change_lang_success.html")
            )
        else:
            update.message.reply_html(
                self.html_replies.reply("change_lang_error.html", user_lang=user_lang)
            )

    def change_default_pool(self, update, context) -> None:
        chat_id = update.effective_chat.id
        self._set_html_reply_lang(chat_id)

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
            self.mongodb.set_default_pool(chat_id, default_pool)
            update.message.reply_html(
                # TODO: modify template to pass pool ticker as argument
                self.html_replies.reply("change_default_pool_success.html")
            )
            return

        user_pool = "".join(context.args).upper()
        self.mongodb.set_default_pool(chat_id, user_pool)
        update.message.reply_html(
            self.html_replies.reply("change_default_pool_success.html")
        )

    @_setup_callback
    def epoch_info(self, update, context) -> None:
        """Get information about the current epoch (/epoch)."""
        currentEpochTip = self.gql.caller("currentEpochTip.graphql").get("data")
        var = {"epoch": currentEpochTip["cardano"]["currentEpoch"]["number"]}
        epochInfo = self.gql.caller("epochInfo.graphql", var).get("data")

        started_at = datetime.fromisoformat(
            # [:-1] to remove the final "Z" from timestamp
            epochInfo["epochs"][0]["startedAt"][:-1]
        )
        remaining_time = started_at + timedelta(days=5) - datetime.utcnow()

        total_slots_epoch = 432000
        perc = currentEpochTip["cardano"]["tip"]["slotInEpoch"] / total_slots_epoch

        # fmt: off
        template_args = {
            "progress_bar": utils.get_progress_bar(perc * 100),
            "perc": perc * 100,
            "current_epoch": currentEpochTip["cardano"]["currentEpoch"]["number"],
            "current_slot": currentEpochTip["cardano"]["tip"]["slotNo"],
            "slot_in_epoch": currentEpochTip["cardano"]["tip"]["slotInEpoch"],
            "txs_in_epoch": epochInfo["epochs"][0]["transactionsCount"],
            "fees_in_epoch": utils.fmt_ada(utils.lovelace_to_ada(int(epochInfo["epochs"][0]["fees"]))),
            "active_stake": utils.fmt_ada(utils.lovelace_to_ada(int(epochInfo["epochs"][0]["activeStake_aggregate"]["aggregate"]["sum"]["amount"]))),
            "n_active_stake_pools": epochInfo["stakePools_aggregate"]["aggregate"]["count"],
            "remaining_time": utils.fmt_time(remaining_time, self.html_replies.reply("days.html")),
        }
        # fmt: on

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

    def start(self, update, context):
        self._set_html_reply_lang(update.effective_chat.id)

        update.message.reply_html(self.html_replies.reply("welcome.html"))
        self.help(update, context)

    def tip(self, update, context):
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⬇️ Click the button below to sign your transaction using Nami wallet:",
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

    def pool_info(self, update, context):
        language = self.mongodb.get_chat_language(update.effective_chat.id)
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

    # def callback_minute(self, context):
    #     context.bot.send_message(chat_id="162210437", text="One message every minute")
