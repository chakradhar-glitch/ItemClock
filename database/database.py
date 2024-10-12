from pymongo import MongoClient
import os
client = MongoClient(os.environ.get('DATABASE_URL'))

db = client['UserDB']

items_collection = db['items']
clockin_collection = db['clockin']

