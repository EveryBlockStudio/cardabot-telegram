"""Manage database data using MongoDB."""
import pymongo


class MongoDatabase:
    def __init__(self, connection_string: str) -> None:
        self.conn_str = connection_string
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.cardabotDatabase
        self.collection = self.db.account

    def create_chat(self, chat_id: int) -> dict:
        """Create chat object with default options."""
        json_obj = {"chat_id": chat_id, "language": "EN", "default_pool": "EBS"}
        self.collection.insert_one(json_obj)
        return json_obj

    def get_chat(self, chat_id: int) -> dict:
        """Returns chat object from database.

        If chat_id is not present, then create new chat object with default options.

        """
        json_obj = self.collection.find_one({"chat_id": chat_id})

        if not json_obj:  # if db response is empty, create new chat file
            json_obj = self.create_chat(chat_id)

        return json_obj

    def get_chat_language(self, chat_id: int) -> str:
        obj = self.get_chat(chat_id)
        return obj["language"]

    def set_chat_language(self, chat_id: int, lang: str) -> None:
        """Set chat default language."""
        # make sure chat is registered in database, otherwise create one
        if not self.collection.find_one({"chat_id": chat_id}):
            self.create_chat(chat_id)

        query = {"chat_id": chat_id}
        update = {"$set": {"language": lang}}

        self.collection.update_one(query, update)

    def set_default_pool(self, chat_id: int, pool: str) -> None:
        """Set the default pool using pool ticker."""
        # make sure chat is registered in database, otherwise create one
        if not self.collection.find_one({"chat_id": chat_id}):
            self.create_chat(chat_id)

        query = {"chat_id": chat_id}
        update = {"$set": {"default_pool": pool}}

        self.collection.update_one(query, update)
