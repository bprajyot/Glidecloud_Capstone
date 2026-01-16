from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import configs
from app.core.logging import logger

class Database:    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    async def connect(self):
        try:
            logger.info("Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(configs.mongodb_uri)
            
            await self.client.admin.command('ping')
            
            self.db = self.client[configs.database_name]
            self.collection = self.db[configs.collection_name]
            
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self):
        return self.collection


db = Database()