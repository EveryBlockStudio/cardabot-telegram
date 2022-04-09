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

    @_setup_callback
    def pool_info(self, update, context):
        """Get pool basic info (/pool)."""
        currentEpochTip = self.gql.caller("currentEpochTip.graphql").get("data")

        var = {"epoch": currentEpochTip["cardano"]["currentEpoch"]["number"]}
        activeStake = self.gql.caller("epochActiveStakeNOpt.graphql", var).get("data")
        adaSupply = self.gql.caller("adaSupply.graphql").get("data")

        # get stake_id
        if context.args:
            stake_id = str("".join(context.args))
        else:
            chat_id = update.effective_chat.id
            stake_id = self.mongodb.get_chat_default_pool(chat_id)

        var = {
            "pool": stake_id,
            "epoch": currentEpochTip["cardano"]["currentEpoch"]["number"],
        }
        # !TODO: treat in case stake_id is not valid
        stakePoolDetails = self.gql.caller("stakePoolDetails.graphql", var).get("data")

        # get pool metadata
        url = stakePoolDetails["stakePools"][0]["url"]

        metadata = {}
        res = requests.get(url)
        if res.json():
            metadata = res.json()

        # fmt: off
        stake = stakePoolDetails["stakePools"][0]["activeStake_aggregate"]["aggregate"]["sum"]["amount"]
        total_stake = activeStake["epochs"][0]["activeStake_aggregate"]["aggregate"]["sum"]["amount"]
        # fmt: on

        controlled_stake_perc = (int(stake) / int(total_stake)) * 100
        circ_supply = adaSupply["ada"]["supply"]["circulating"]
        n_opt = activeStake["epochs"][0]["protocolParams"]["nOpt"]

        saturation = utils.calc_pool_saturation(
            int(stake), int(circ_supply), int(n_opt)
        )

        # fmt: off
        template_args = {
            "ticker": metadata.get("ticker", "NOT FOUND."),
            "name": metadata.get("name", "NOT FOUND."),
            "description": metadata.get("description", "NOT FOUND."),
            "homepage": metadata.get("homepage", "NOT FOUND."),
            "pool_id": stakePoolDetails["stakePools"][0]["id"],
            "pledge": utils.fmt_ada(utils.lovelace_to_ada(int(stakePoolDetails["stakePools"][0]["pledge"]))),
            "fixed_cost": utils.fmt_ada(utils.lovelace_to_ada(int(stakePoolDetails["stakePools"][0]["fixedCost"]))),
            "margin": stakePoolDetails["stakePools"][0]["margin"] * 100,
            "saturation": saturation * 100,  # !TODO: fix
            "saturation_symbol": utils.get_saturation_icon(saturation),  # !TODO: fix
            "controlled_stake_perc": controlled_stake_perc,  # !TODO: fix
            "active_stake_amount": utils.fmt_ada(utils.lovelace_to_ada(int(stake))),  # !TODO: fix
            "delegators_count": stakePoolDetails["stakePools"][0]["delegators_aggregate"]["aggregate"]["count"],
            "epoch_blocks_count": stakePoolDetails["blocksThisEpoch"][0]["blocks_aggregate"]["aggregate"]["count"],
            "lifetime_blocks_count": stakePoolDetails["lifetimeBlocks"][0]["blocks_aggregate"]["aggregate"]["count"],
        }
        # fmt: on

        update.message.reply_html(
            self.html_replies.reply("pool_info.html", **template_args)
        )

    @_setup_callback
    def pots(self, update, context):
        """Get info about cardano pots (/pots)."""
        currentEpochTip = self.gql.caller("currentEpochTip.graphql").get("data")
        var = {"epoch": currentEpochTip["cardano"]["currentEpoch"]["number"]}
        adaPot = self.gql.caller("adaPot.graphql", var).get("data")["epochs"][0]

        template_args = {
            "treasury": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["treasury"]))
            ),
            "reserves": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["reserves"]))
            ),
            "fees": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["fees"]))
            ),
            "rewards": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["rewards"]))
            ),
            "utxo": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["utxo"]))
            ),
            "deposits": utils.fmt_ada(
                utils.lovelace_to_ada(int(adaPot["adaPots"]["deposits"]))
            ),
        }

        update.message.reply_html(self.html_replies.reply("pots.html", **template_args))

    @_setup_callback
    def netparams(self, update, context):
        """Get network parameters (/netparams)."""
        currentEpochTip = self.gql.caller("currentEpochTip.graphql").get("data")
        var = {"epoch": currentEpochTip["cardano"]["currentEpoch"]["number"]}
        netParams = self.gql.caller("netParams.graphql", var).get("data")["epochs"][0]

        template_args = {
            "a0": netParams["protocolParams"]["a0"],
            "min_pool_cost": utils.fmt_ada(
                utils.lovelace_to_ada(int(netParams["protocolParams"]["minPoolCost"]))
            ),
            "min_utxo_value": utils.lovelace_to_ada(
                int(netParams["protocolParams"]["minUTxOValue"])
            ),
            "n_opt": netParams["protocolParams"]["nOpt"],
            "rho": netParams["protocolParams"]["rho"],
            "tau": netParams["protocolParams"]["tau"],
        }

        update.message.reply_html(
            self.html_replies.reply("netparams.html", **template_args)
        )

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
