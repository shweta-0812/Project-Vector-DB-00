from pymongo.mongo_client import MongoClient

from common_utils import get_env_key

MONGO_URI = get_env_key("MONGO_URI")


class MongoConnection:
    _client = None

    @classmethod
    def initialise_client(cls):
        if cls._client is None:
            # maxIdleTimeMS=300000: ensures the connection will be closed automatically after 5 mins of inactivity.
            cls._client = MongoClient(MONGO_URI, appname="simple_mongo_app", maxIdleTimeMS=300000)
        return cls._client
