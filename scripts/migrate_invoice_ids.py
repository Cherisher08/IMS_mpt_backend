"""
Migration script to update invoice IDs for rental orders from April 1, 2026 onwards.
"""
from datetime import datetime
from pymongo import ASCENDING
from app.config import database
import re
import argparse

def migrate_invoices(dry_run=True):
    # Only target April 2026 onwards
    start_date = datetime(2026, 4, 1)
    
    # We want to match:
    # invoice_date >= start_date OR (invoice_date is missing AND created_at >= start_date)
    query = {
        "invoice_id": {"$exists": True, "$ne": None, "$ne": ""},
        "$or": [
            {"invoice_date": {"$gte": start_date}},
            {"invoice_date": {"$exists": False}, "created_at": {"$gte": start_date}},
            {"invoice_date": None, "created_at": {"$gte": start_date}}
        ]
    }
    
    collection = database["rental_orders"]
    
    orders = list(collection.find(query).sort([("invoice_date", ASCENDING), ("created_at", ASCENDING)]))
    
    branch_mapping = {
        "PADUR-1": "PD",
        "PUDPK-1": "PM",
        "KLMBK-1": "KL",
    }
    
    if dry_run:
        print(f"--- DRY RUN: Found {len(orders)} orders eligible for migration ---")
    else:
        print(f"--- EXECUTING: Found {len(orders)} orders eligible for migration ---")
        
    updated_count = 0
    skipped_count = 0
    
    counters = {}
    
    for order in orders:
        old_id = order.get("invoice_id")
        billing_mode = order.get("billing_mode", "B2B")
        branch_str = order.get("branch", "PADUR-1")
        branch_short = branch_mapping.get(branch_str, "XX")
        type_letter = "B" if billing_mode == "B2B" else "C"
        
        # Get year from invoice_date or created_at
        date_val = order.get("invoice_date") or order.get("created_at")
        year_full = date_val.year if date_val else 2026
        year_2 = str(year_full)[-2:]
        
        # The group key
        group_key = (type_letter, year_2, branch_short)
        if group_key not in counters:
            counters[group_key] = 1
            
        # Is this one of the 11 manual B2B Padur invoices?
        # They were formatted exactly as INV/B2B/PD/XXXX.
        if billing_mode == "B2B" and branch_short == "PD":
            match = re.match(r"^INV/B2B/PD/(\d{4})$", old_id)
            if match:
                num = int(match.group(1))
                if 1 <= num <= 11:
                    print(f"Skipping manual override: {old_id}")
                    # Update counter if needed so next is num + 1
                    counters[group_key] = max(counters[group_key], num + 1)
                    skipped_count += 1
                    continue
                    
        # Assign new ID
        new_num = counters[group_key]
        new_id = f"INV/{type_letter}{year_2}/{branch_short}/{new_num:04d}"
        
        if old_id == new_id:
            print(f"Order {order.get('order_id')} already has correct ID: {new_id}")
            # we must update counter
            counters[group_key] = max(counters[group_key], new_num + 1)
            continue
            
        print(f"Updating order {order.get('order_id')} (old ID: {old_id}) -> new ID: {new_id}")
        
        # We can update DB
        if not dry_run:
            collection.update_one(
                {"_id": order["_id"]},
                {"$set": {"invoice_id": new_id}}
            )
        
        updated_count += 1
        counters[group_key] += 1
        
    if dry_run:
        print(f"--- DRY RUN COMPLETE. Would update {updated_count} orders, skipped {skipped_count} manual overrides ---")
    else:
        print(f"--- MIGRATION COMPLETE. Updated {updated_count} orders, skipped {skipped_count} manual overrides ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Actually execute the database updates")
    args = parser.parse_args()
    
    migrate_invoices(dry_run=not args.execute)
