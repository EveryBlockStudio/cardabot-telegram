import logging
import os
import re
import secrets
import time
from datetime import datetime, timedelta

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from . import database, utils
from .replies import HTMLReplies


class CardaBotCallbacks:
    def __init__(self) -> None:
        self.base_url = os.environ.get("CARDABOT_API_URL")
        self.cardabotdb = database.CardabotDB(self.base_url)
        self.ebs_pool = "pool1ndtsklata6rphamr6jw2p3ltnzayq3pezhg0djvn7n5js8rqlzh"
        self.headers = {
            "Authorization": "Token " + os.environ.get("CARDABOT_API_TOKEN")
        }

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
        r = requests.get(url, headers=self.headers, params={"currency_format": "ADA"})
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

        update.message.reply_text("⌛ Fetching pool info, please wait...")

        endpoint = f"pool/{stake_id}"
        url = os.path.join(self.base_url, endpoint)
        r = requests.get(url, headers=self.headers, params={"currency_format": "ADA"})

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
        r = requests.get(url, headers=self.headers, params={"currency_format": "ADA"})
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
        r = requests.get(url, headers=self.headers, params={"currency_format": "ADA"})
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
        r = requests.get(url, headers=self.headers, params={"currency_format": "ADA"})
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

    def _get_cardabot_user_id(self, chat_id: str | int) -> int:
        """Return the cardabor user id for the given chat_id.

        If chat is not connected, return None.
        """
        res = requests.get(
            os.path.join(self.base_url, f"chats/{chat_id}/"),
            headers=self.headers,
            params={"client_filter": "TELEGRAM"},
        )
        res.raise_for_status()

        return res.json().get("cardabot_user_id", None)

    @_setup_callback
    def connect(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Connect user wallet"""
        chat_id = update.effective_chat.id

        # only allow private chats
        if update.effective_chat.type != "private":
            update.message.reply_html(html.reply("connection_refused.html"))
            return

        ## Get token from chat_id
        r = requests.get(
            os.path.join(self.base_url, f"chats/{chat_id}/token/"),
            headers=self.headers,
            params={"client_filter": "TELEGRAM"},
        )
        r.raise_for_status()  # captured by the _setup_callback decorator
        tmp_token = r.json().get("tmp_token", None)

        ## Create unique URL for user
        cardabot_url = self.base_url.replace("api/", "")
        connect_url_link = f"{cardabot_url}connect?token={tmp_token}"

        message = context.bot.send_message(
            chat_id=chat_id,
            text=f"⬇️ Click the button below to connect your web wallet to CardaBot, so you can starting tipping",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔗 Connect Wallet",
                            url=connect_url_link,
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

        # task to run for a couple of minutes or until the user connects his wallet
        def update_message(message, cardabot_user, chat_id, job_id):
            cardabot_user_id = self._get_cardabot_user_id(chat_id)
            if cardabot_user != cardabot_user_id:
                message.edit_text(
                    html.reply("connection_success.html"), parse_mode="HTML"
                )
                utils.Scheduler.queue.remove_job(job_id)

        start_date = datetime.now() + timedelta(seconds=20)
        end_date = start_date + timedelta(seconds=7 * 60)
        job_id = secrets.token_urlsafe(6)  # generate tmp id for the job
        utils.Scheduler.queue.add_job(  # add job to scheduler
            update_message,
            "interval",
            seconds=10,
            start_date=start_date,
            end_date=end_date,
            args=[message, self._get_cardabot_user_id(chat_id), chat_id, job_id],
            id=job_id,
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

    def _get_network() -> str:
        """Return the network name"""
        network = os.environ.get("NETWORK", "mainnet").lower()
        if network not in ("mainnet", "testnet"):
            raise ValueError("Invalid network environment variable!")

        return network

    @_setup_callback
    def tip(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Tip a user"""
        if update.message.reply_to_message is None:
            # only allow tip if msg is a response to a user
            update.message.reply_html(html.reply("tip_refused.html"))
            return

        txt = update.message.text.split()
        lbound = utils.min_ada()
        if not (len(txt) == 2 and utils.isnumber(txt[1]) and float(txt[1]) > lbound):
            update.message.reply_html(html.reply("tip_refused.html"))
            return

        # get data for building tx
        data = {
            "chat_id_sender": update.message.from_user.id,
            "chat_id_receiver": update.message.reply_to_message.from_user.id,
            "username_receiver": update.message.reply_to_message.from_user.username,
            "amount": float(txt[1]),
            "client": "TELEGRAM",
        }

        # call cardabot-api to build the tx (get tx_id)
        r = requests.post(
            os.path.join(self.base_url, "unsignedtx/"), headers=self.headers, data=data
        )

        # verify the tx response
        if r.status_code >= 400:
            message = update.message.reply_text(
                r.json().get("detail", None)
            )  # TODO: improve this, should be an html reply
            return

        if r.status_code != 201:
            update.message.reply_text("💰 Tip failed!\n\n")
            return

        tx_id = r.json().get("tx_id")
        # create a link to sign the tx
        cardabot_url = self.base_url.replace("api/", "")
        pay_url_link = f"{cardabot_url}pay?tx_id={tx_id}"

        # create message with a button to send the tx
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⬇️ Click the button below to sign your transaction using your web wallet:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔑 Sign Tx",
                            url=pay_url_link,
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

        # task to run for a couple of minutes or until the tx is submitted to network
        def update_message(message, tx_id, network, job_id, end_date):
            r = requests.get(
                os.path.join(self.base_url, f"checktx/{tx_id}/"),
                headers=self.headers,
            )

            if r.status_code != 200:
                if datetime.now() > end_date - timedelta(seconds=30):
                    message.edit_text(
                        text=html.reply("tip_fail.html"), parse_mode="HTML"
                    )
                    utils.Scheduler.queue.remove_job(job_id)
                return

            net = network + "." if network == "testnet" else ""
            message.edit_text(
                text="✅ Your transaction was submitted!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Check Tx on CardanoScan",
                                url=f"https://{net}cardanoscan.io/transaction/{tx_id}",
                            )
                        ],
                    ]
                ),
            )
            utils.Scheduler.queue.remove_job(job_id)

        start_date = datetime.now() + timedelta(seconds=1)
        end_date = start_date + timedelta(seconds=600)
        job_id = secrets.token_urlsafe(6)  # generate tmp id for the job
        utils.Scheduler.queue.add_job(  # add job to scheduler
            update_message,
            "interval",
            seconds=30,
            start_date=start_date,
            end_date=end_date,
            args=[message, tx_id, self._get_network(), job_id, end_date],
            id=job_id,
        )

    def _get_all_cardabot_chats(self) -> list[str]:
        """Get all cardabot chats from database, excluding groups."""
        r = requests.get(
            os.path.join(self.base_url, "chats/"),
            headers=self.headers,
            params={"client_filter": "TELEGRAM"},
        )
        r.raise_for_status()

        chat_ids = [
            chat.get("chat_id") for chat in r.json() if int(chat.get("chat_id")) > 0
        ]  # exclude telegram group chats

        return chat_ids

    @_setup_callback
    def alert(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Send a message to all users."""
        sender_chat_id = os.environ.get("ADMIN_CHAT_ID")
        if str(update.effective_user.id) != sender_chat_id:
            update.message.reply_html(html.reply("endpoint_refused.html"))
            return

        message = update.message.text.split(" ", 1)[1]
        chat_ids = self._get_all_cardabot_chats()

        utils.send_to_all(bot=context.bot, chat_ids=chat_ids, text=message)

    def end_of_epoch_task(self, bot) -> None:
        """Send of epoch summary to all users."""
        html = HTMLReplies()
        message = html.reply("end_of_epoch_summary.html", epoch=299)
        chat_ids = self._get_all_cardabot_chats()
        utils.send_to_all(bot=bot, chat_ids=chat_ids, text=message, parse_mode="HTML")

    @_setup_callback
    def claim(self, update, context, html: HTMLReplies = HTMLReplies()):
        """Claim user funds that are being held temporarily."""
        update.message.reply_text(f"⌛️ We're transfering your funds, please wait...")

        chat_id = update.message.from_user.id
        r = requests.post(
            os.path.join(self.base_url, "claim/"),
            headers=self.headers,
            params={"client_filter": "TELEGRAM"},
            data={"chat_id_receiver": chat_id},
        )

        if r.status_code == 406 or r.status_code == 404:
            message = update.message.reply_text(
                r.json().get("detail", None)
            )  # TODO: improve this, should be an html reply
            return
        else:
            r.raise_for_status()

        network = self._get_network()
        net = network + "." if network == "testnet" else ""
        update.message.reply_text(
            text="✅ Your funds were successfuly transfered to you!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Check Tx on CardanoScan",
                            url=f"https://{net}cardanoscan.io/transaction/{r.json().get('tx_id')}",
                        )
                    ],
                ]
            ),
        )
        return
