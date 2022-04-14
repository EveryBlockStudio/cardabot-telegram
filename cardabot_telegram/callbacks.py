import os
from datetime import datetime, timedelta
import time
import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, chat

from . import mongodb
from . import utils
from .replies import HTMLReplies
from . import graphql_client


class CardaBotCallbacks:
    def __init__(
        self,
        mongodb: mongodb.MongoDatabase,
        graphql_client: graphql_client.GraphQLClient,
    ) -> None:
        self.mongodb = mongodb
        self.gql = graphql_client
        self.base_url = os.environ.get("CARDABOT_API_URL")
        self.ebs_pool = "pool1ndtsklata6rphamr6jw2p3ltnzayq3pezhg0djvn7n5js8rqlzh"

    def _inform_error(self, context, chat_id):
        context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, something went wrong 😔",
        )

    def _setup_callback(func):
        """Decorator to setup callback configs and handle exceptions."""

        def callback(self, update, context):
            try:
                chat_id = update.effective_chat.id
                language = self.mongodb.get_chat_language(chat_id)
                html = HTMLReplies()
                html.set_language(language)
                func(self, update, context, html)

            except Exception as e:
                self._inform_error(context, chat_id)
                logging.exception(e)
                return

        return callback

    @_setup_callback
    def help(self, update, context, html: HTMLReplies = HTMLReplies()) -> None:
        update.message.reply_html(
            html.reply("help.html", supported_languages=html.supported_languages)
        )

    @_setup_callback
    def start(self, update, context, html: HTMLReplies = HTMLReplies()) -> None:
        update.message.reply_html(html.reply("welcome.html"))
        self.help(update, context)

    @_setup_callback
    def change_language(
        self, update, context, html: HTMLReplies = HTMLReplies()
    ) -> None:
        """Change default language of the chat (/language)."""
        chat_id = update.effective_chat.id
        if update.effective_chat.type == "group":
            if not utils.user_is_adm(update, context):
                update.message.reply_html(html.reply("not_authorized.html"))
                return

        if not context.args:
            # set language to default (EN) when no args are passed by the user
            default_language = html.default_lang
            html.set_language(default_language)
            self.mongodb.set_chat_language(chat_id, default_language)
            update.message.reply_html(html.reply("change_lang_success.html"))
            return

        user_lang = "".join(context.args).upper()
        if html.set_language(user_lang):
            self.mongodb.set_chat_language(chat_id, user_lang)
            update.message.reply_html(html.reply("change_lang_success.html"))
        else:
            update.message.reply_html(
                html.reply("change_lang_error.html", user_lang=user_lang)
            )

    @_setup_callback
    def change_default_pool(
        self, update, context, html: HTMLReplies = HTMLReplies()
    ) -> None:
        """Change default pool of the chat (/setpool)."""

        if update.effective_chat.type == "group":
            if not utils.user_is_adm(update, context):
                update.message.reply_html(html.reply("not_authorized.html"))
                return

        chat_id = update.effective_chat.id
        if not context.args:
            # if there are no args, change default pool to `EBS`
            self.mongodb.set_default_pool(chat_id, self.ebs_pool)
            update.message.reply_html(html.reply("change_default_pool_success.html"))
            return

        user_pool = "".join(context.args)
        self.mongodb.set_default_pool(chat_id, user_pool)
        update.message.reply_html(html.reply("change_default_pool_success.html"))

    @_setup_callback
    def epoch_info(self, update, context, html: HTMLReplies = HTMLReplies()) -> None:
        """Get information about the current epoch (/epoch)."""
        endpoint = "epoch/"
        url = os.path.join(self.base_url, endpoint)
        r = requests.get(url, params={"currency_format": "ADA"})
        r.raise_for_status()  # captured by the _setup_callback decorator
        data = r.json().get("data", None)

        template_args = {
            "progress_bar": utils.get_progress_bar(data.get("percentage")),
            "perc": data.get("percentage"),
            "current_epoch": data.get("current_epoch"),
            "current_slot": data.get("current_slot"),
            "slot_in_epoch": data.get("slot_in_epoch"),
            "txs_in_epoch": data.get("txs_in_epoch"),
            "fees_in_epoch": utils.fmt_ada(data.get("fees_in_epoch")),
            "active_stake": utils.fmt_ada(data.get("active_stake")),
            "n_active_stake_pools": data.get("n_active_stake_pools"),
            "remaining_time": utils.fmt_time(
                timedelta(seconds=data.get("remaining_time")),
                html.reply("days.html"),
            ),
        }

        update.message.reply_html(html.reply("epoch_info.html", **template_args))

    @_setup_callback
    def pool_info(self, update, context, html: HTMLReplies = HTMLReplies()):
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

        update.message.reply_html(html.reply("pool_info.html", **template_args))

    @_setup_callback
    def pots(self, update, context, html: HTMLReplies = HTMLReplies()):
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

        update.message.reply_html(html.reply("pots.html", **template_args))

    @_setup_callback
    def netparams(self, update, context, html: HTMLReplies = HTMLReplies()):
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

        update.message.reply_html(html.reply("netparams.html", **template_args))

    @_setup_callback
    def netstats(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Get network statistics (/netstats)."""
        endpoint = "netstats/"
        url = os.path.join(self.base_url, endpoint)
        r = requests.get(url)
        r.raise_for_status()  # captured by the _setup_callback decorator
        data = r.json().get("data", None)

        template_args = {
            "ada_in_circulation": utils.fmt_ada(
                utils.lovelace_to_ada(int(data.get("ada_in_circulation")))
            ),
            "percentage_in_stake": data.get("percentage_in_stake"),
            "stakepools": data.get("stakepools"),
            "delegations": data.get("delegations"),
            "load_1h": data.get("load_1h"),
            "load_24h": data.get("load_24h"),
        }

        update.message.reply_html(html.reply("netstats.html", **template_args))

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
