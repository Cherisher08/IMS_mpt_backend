#!/usr/bin/env python3
"""Recover missing contact images by clearing broken address_proof values.

This script connects to MongoDB using MONGO_URI and DATABASE from the environment
or from a root .env file, scans files under app/public/contact, and updates
contacts whose stored address_proof points to a file that no longer exists.

Usage:
    python scripts/recover_contact_address_proof.py --dry-run
    python scripts/recover_contact_address_proof.py --commit
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from pymongo import MongoClient
from pymongo.errors import PyMongoError

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    if load_dotenv:
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        print(f"WARNING: {ENV_PATH} exists but python-dotenv is not installed. Using environment variables only.")
elif load_dotenv:
    load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE = os.getenv("DATABASE")
CONTACTS_DIR = ROOT_DIR / "app" / "public" / "contact"


def normalize_address_proof(value: str) -> str:
    if value is None:
        return ""

    value = str(value).strip()
    if not value:
        return ""

    parsed = urlparse(value)
    if parsed.path:
        return os.path.basename(parsed.path)

    return os.path.basename(value)


def contact_file_exists(filename: str) -> bool:
    if not filename:
        return False

    file_path = CONTACTS_DIR / filename
    return file_path.is_file()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recover contact address_proof values by clearing missing image references."
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Apply updates to MongoDB. Without this flag the script only prints what would change.",
    )
    parser.add_argument(
        "--contact-dir",
        default=str(CONTACTS_DIR),
        help="Override the contact images directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contact_dir = Path(args.contact_dir)

    if not MONGO_URI or not DATABASE:
        print("ERROR: MONGO_URI and DATABASE environment variables must be set.")
        return 1

    if not contact_dir.exists() or not contact_dir.is_dir():
        print(f"ERROR: Contact directory does not exist: {contact_dir}")
        return 1

    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE]
        collection = db["contacts"]
    except PyMongoError as exc:
        print(f"ERROR: Failed to connect to MongoDB: {exc}")
        return 1

    query = {"address_proof": {"$exists": True, "$ne": ""}}
    try:
        documents = list(collection.find(query, {"address_proof": 1}))
    except PyMongoError as exc:
        print(f"ERROR: Failed to query contacts: {exc}")
        return 1

    print(f"Found {len(documents)} contacts with non-empty address_proof.")

    broken_docs = []
    for doc in documents:
        original_value = doc.get("address_proof", "")
        filename = normalize_address_proof(original_value)
        if not filename:
            broken_docs.append((doc.get("_id"), original_value, filename, False))
            continue

        if not (contact_dir / filename).is_file():
            broken_docs.append((doc.get("_id"), original_value, filename, True))

    if not broken_docs:
        print("No broken address_proof values found. Nothing to update.")
        return 0

    print(f"Broken address_proof entries detected: {len(broken_docs)}")
    for doc_id, original_value, filename, missing_file in broken_docs:
        note = "missing file" if missing_file else "invalid filename"
        print(f"- {_format_id(doc_id)}: {original_value!r} -> filename {filename!r} ({note})")

    if not args.commit:
        print("\nDry run complete. Add --commit to apply updates.")
        return 0

    updated_count = 0
    for doc_id, original_value, filename, missing_file in broken_docs:
        try:
            result = collection.update_one(
                {"_id": doc_id},
                {"$set": {"address_proof": ""}},
            )
            if result.modified_count == 1:
                updated_count += 1
        except PyMongoError as exc:
            print(f"ERROR: Failed to update {_format_id(doc_id)}: {exc}")

    print(f"Updated {updated_count}/{len(broken_docs)} broken contacts.")
    return 0


def _format_id(value):
    return str(value)


if __name__ == "__main__":
    sys.exit(main())
