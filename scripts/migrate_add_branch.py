"""
Migration script to add branch field to existing users.
Sets default branch to INV-PADUR-1 for all existing users.
"""
from datetime import datetime, timezone
from pymongo import MongoClient
from app.dependencies import env
from app.config import database

def migrate_add_branch():
    """Add branch field to all existing users without a branch."""
    users_without_branch = database["users"].find({"branch": {"$exists": False}})

    count = 0
    for user in users_without_branch:
        database["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"branch": "PADUR-1"}}
        )
        count += 1
        print(f"Updated user {user['email']} with branch PADUR-1")

    print(f"Migration complete. Updated {count} users.")

if __name__ == "__main__":
    migrate_add_branch()
