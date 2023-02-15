import os
import motor.motor_asyncio

db_url = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('MONGODB_DB_NAME', 'my_trading')
client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
db = client.get_default_database(db_name)
