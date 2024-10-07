import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://lx941008:lx79112661@cluster0.16uwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Create a new client and connect to the server
client = MongoClient(MONGO_URI)

# Get the database
db = client["Users"]
collection = db["info"]

# Helper function to convert MongoDB ObjectId to string
def serialize_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# User model (as a dictionary, since MongoDB is schemaless)
def create_user(username: str, hashed_password: str, first_name:str, last_name:str, roles: str):
    return {
        "username": username,
        "hashed_password": hashed_password,
        "first_name": first_name,
        "last_name": last_name,
        "roles": roles
    }

# Database operations
def get_user(username: str):
    return db.users.find_one({"username": username})

def create_new_user(user):
    result = db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user

# You can add more database operations as needed