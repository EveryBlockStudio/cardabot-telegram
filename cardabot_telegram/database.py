"""Manage chat objects in the CardaBot database."""
import os
import requests


class CardabotDB:
    def __init__(self, url: str, token: str = "") -> None:
        self.base_url = url
        self.token = token
        self.headers = {
            "Authorization": "Token " + os.environ.get("CARDABOT_API_TOKEN")
        }

    def create_chat(self, chat_id: int | str) -> dict:
        """Create chat object with default options."""
        data = {
            "chat_id": str(chat_id),
            "client": "TELEGRAM",
        }
        url = os.path.join(self.base_url, "chats/")
        r = requests.post(url, headers=self.headers, json=data)
        r.raise_for_status()
        return r.json()

    def get_or_create_chat(self, chat_id: int) -> dict:
        """Returns chat object from database.

        If chat_id is not present, then create new chat object with default options.
        """
        endpoint = f"chats/{chat_id}/"
        url = os.path.join(self.base_url, endpoint)
        r = requests.get(
            url, headers=self.headers, params={"client_filter": "TELEGRAM"}
        )

        # print(r.text)

        if r.status_code == 404 and "not found" in r.json()["detail"].lower():
            return self.create_chat(chat_id)

        r.raise_for_status()
        return r.json()

    def get_chat_default_pool(self, chat_id: int) -> str:
        res = self.get_or_create_chat(chat_id)
        return res["default_pool_id"]

    def get_chat_language(self, chat_id: int) -> str:
        res = self.get_or_create_chat(chat_id)
        return res["default_language"]

    def set_chat_language(self, chat_id: int, lang: str) -> None:
        """Set chat default language."""
        # make sure chat is registered in database, otherwise create one
        self.get_or_create_chat(chat_id)

        endpoint = f"chats/{chat_id}/"
        url = os.path.join(self.base_url, endpoint)
        data = {"default_language": lang}
        r = requests.patch(
            url, json=data, headers=self.headers, params={"client_filter": "TELEGRAM"}
        )
        r.raise_for_status()

    def set_default_pool(self, chat_id: int, pool: str) -> None:
        """Set the default pool using pool ticker."""
        # make sure chat is registered in database, otherwise create one
        self.get_or_create_chat(chat_id)

        endpoint = f"chats/{chat_id}/"
        url = os.path.join(self.base_url, endpoint)
        data = {"default_pool_id": pool}
        r = requests.patch(
            url, json=data, headers=self.headers, params={"client_filter": "TELEGRAM"}
        )
        r.raise_for_status()
