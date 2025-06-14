from typing import Any

from pymongo import MongoClient

from .dependencies import ENV


# environmental variables
env = ENV()

# FastAPI configurations
fastapi_config: dict[str, Any] = {
    "title": "IMS API",
    "separate_input_output_schemas": False,
}

if env.mongo_db_url:
    mongo_url = env.mongo_db_url

# MongoDB connection
client = MongoClient(mongo_url,tz_aware=True)

# MongoDB database
database = client[env.database]
