import os
from datetime import timedelta
import time
import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, chat

from . import database
from . import utils
from .replies import HTMLReplies


class CardaBotCallbacks:
    def __init__(self) -> None:
        self.base_url = os.environ.get("CARDABOT_API_URL")
        self.cardabotdb = database.CardabotDB(self.base_url)
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
                language = self.cardabotdb.get_chat_language(chat_id)
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
            self.cardabotdb.set_chat_language(chat_id, default_language)
            update.message.reply_html(html.reply("change_lang_success.html"))
            return

        user_lang = "".join(context.args).upper()
        if html.set_language(user_lang):
            self.cardabotdb.set_chat_language(chat_id, user_lang)
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
            self.cardabotdb.set_default_pool(chat_id, self.ebs_pool)
            update.message.reply_html(html.reply("change_default_pool_success.html"))
            return

        user_pool = "".join(context.args)
        self.cardabotdb.set_default_pool(chat_id, user_pool)
        update.message.reply_html(html.reply("change_default_pool_success.html"))

    @_setup_callback
    def epoch_info(self, update, context, html: HTMLReplies = HTMLReplies()) -> None:
        """Get information about the current epoch (/epoch)."""
        endpoint = "epoch/"
        url = os.path.join(self.base_url, endpoint)
        headers = {'Authorization': 'Token ' + os.environ.get("CARDABOT_API_TOKEN")}
        r = requests.get(url, headers=headers, params={"currency_format": "ADA"})
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
        # get stake_id
        if context.args:
            stake_id = str("".join(context.args))
        else:
            chat_id = update.effective_chat.id
            stake_id = self.cardabotdb.get_chat_default_pool(chat_id)

        endpoint = f"pool/{stake_id}"
        url = os.path.join(self.base_url, endpoint)
        headers = {'Authorization': 'Token ' + os.environ.get("CARDABOT_API_TOKEN")}
        r = requests.get(url, headers=headers, params={"currency_format": "ADA"})

        # fmt: off
        if r.status_code == 404:
            template_args = {"ticker": stake_id}
            update.message.reply_html(html.reply("pool_info_error.html", **template_args))
            return

        data = r.json().get("data", None)

        template_args = {
            "ticker": data.get("ticker"),
            "name": data.get("name"),
            "description": data.get("description"),
            "homepage": data.get("homepage"),
            "pool_id": data.get("pool_id"),
            "pledge": utils.fmt_ada(data.get("pledge")),
            "fixed_cost": utils.fmt_ada(data.get("fixed_cost")),
            "margin": data.get("margin"),
            "saturation": data.get("saturation"),  # !TODO: fix
            "saturation_symbol": utils.get_saturation_icon(data.get("saturation")),  # !TODO: fix
            "controlled_stake_perc": data.get("controlled_stake_percentage"),  # !TODO: fix
            "active_stake_amount": utils.fmt_ada(data.get("active_stake_amount")),  # !TODO: fix
            "delegators_count": data.get("delegators_count"),
            "epoch_blocks_count": data.get("epoch_blocks_count"),
            "lifetime_blocks_count": data.get("lifetime_blocks_count"),
        }
        # fmt: on

        update.message.reply_html(html.reply("pool_info.html", **template_args))

    @_setup_callback
    def pots(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Get info about cardano pots (/pots)."""
        endpoint = "pots/"
        url = os.path.join(self.base_url, endpoint)
        headers = {'Authorization': 'Token ' + os.environ.get("CARDABOT_API_TOKEN")}
        r = requests.get(url, headers=headers, params={"currency_format": "ADA"})
        r.raise_for_status()  # captured by the _setup_callback decorator
        data = r.json().get("data", None)

        template_args = {
            "treasury": utils.fmt_ada(data.get("treasury")),
            "reserves": utils.fmt_ada(data.get("reserves")),
            "fees": utils.fmt_ada(data.get("fees")),
            "rewards": utils.fmt_ada(data.get("rewards")),
            "utxo": utils.fmt_ada(data.get("utxo")),
            "deposits": utils.fmt_ada(data.get("deposits")),
        }

        update.message.reply_html(html.reply("pots.html", **template_args))

    @_setup_callback
    def netparams(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Get network parameters (/netparams)."""
        endpoint = "netparams/"
        url = os.path.join(self.base_url, endpoint)
        headers = {'Authorization': 'Token ' + os.environ.get("CARDABOT_API_TOKEN")}
        r = requests.get(url, headers=headers, params={"currency_format": "ADA"})
        r.raise_for_status()  # captured by the _setup_callback decorator
        data = r.json().get("data", None)

        template_args = {
            "a0": data.get("a0"),
            "min_pool_cost": utils.fmt_ada(data.get("min_pool_cost")),
            "min_utxo_value": data.get("min_utxo_value"),
            "n_opt": data.get("n_opt"),
            "rho": data.get("rho"),
            "tau": data.get("tau"),
        }

        update.message.reply_html(html.reply("netparams.html", **template_args))

    @_setup_callback
    def netstats(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Get network statistics (/netstats)."""
        endpoint = "netstats/"
        url = os.path.join(self.base_url, endpoint)
        headers = {'Authorization': 'Token ' + os.environ.get("CARDABOT_API_TOKEN")}
        r = requests.get(url, headers=headers, params={"currency_format": "ADA"})
        r.raise_for_status()  # captured by the _setup_callback decorator
        data = r.json().get("data", None)

        template_args = {
            "ada_in_circulation": utils.fmt_ada(data.get("ada_in_circulation")),
            "percentage_in_stake": data.get("percentage_in_stake"),
            "stakepools": data.get("stakepools"),
            "delegations": data.get("delegations"),
            "load_15m": data.get("load_15m"),
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
