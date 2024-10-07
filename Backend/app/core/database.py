import os
from pymongo import MongoClient
from bson import ObjectId
from .config import settings

# MongoDB's connection string
# MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lx941008:lx79112661@cluster0.16uwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Create a new client and connect to the server
client = MongoClient(settings.MONGO_URI)

# Get the database
db = client[settings.DATABASE_NAME]
users = db[settings.USER_COLLECTION_NAME]
files = db[settings.FILE_COLLECTION_NAME]

# Helper function to convert MongoDB ObjectId to string
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# User model (as a dictionary, since MongoDB is schemaless)
def create_user(username: str, hashed_password: str, first_name: str, last_name: str, roles: str):
    return {
        "username": username,
        "hashed_password": hashed_password,
        "first_name": first_name,
        "last_name": last_name,
        "roles": roles
    }

# Database operations
def get_user(username: str):
    return users.find_one({"username": username})

def create_new_user(user):
    result = users.insert_one(user)
    user['_id'] = result.inserted_id
    return user

def close_mongo_connection():
    client.close()
