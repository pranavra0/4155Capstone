from pymongo import MongoClient

client = None
db = None

def init_db():
    global client, db
    client = MongoClient("mongodb://localhost:27017")
    db = client["orchestrator"]
    print("Connected to MongoDB")
    
def get_collection(name: str):
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db[name]
