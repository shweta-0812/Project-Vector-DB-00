from django.apps import AppConfig
from memory.mongo_db.db.mongo_client import MongoConnection


class MemoryConfig(AppConfig):
    name = "memory"

    #  This method is called when Django starts.
    # Here, you call MongoConnection.get_client() to ensure that MongoDB is connected when the server starts.
    def ready(self):
        # Initialize MongoDB connection
        MongoConnection.initialise_client()
        print("MongoDB connection initialized.")
