from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.database = cls.client[settings.DATABASE_NAME]
        print("Connected to MongoDB!")

    @classmethod
    async def close_mongo_connection(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed!")
