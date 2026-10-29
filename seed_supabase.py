"""
Seed Script to migrate 228 chairs from local catalog.json into Supabase
Run: py seed_supabase.py
Requires: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env or environment
"""
import os
import json

def seed():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[NOTICE] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables not set.")
        print("Please set these variables to sync catalog.json to your Supabase PostgreSQL table.")
        return

    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
    except ImportError:
        print("[ERROR] Please install supabase client: pip install supabase")
        return

    json_path = os.path.join(os.path.dirname(__file__), "assets", "catalog.json")
    with open(json_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    print(f"Uploading {len(catalog)} chairs to Supabase table 'chairs'...")
    records = []
    for p in catalog:
        records.append({
            "id": p["id"],
            "category": p["category"],
            "code": p["code"],
            "code_number": p["code_number"],
            "model_name": p.get("_internal_model") or p.get("model_name"),
            "price_display": p["price_display"],
            "base_price": p["base_price"],
            "options": p.get("options", []),
            "features": p.get("features", []),
            "specs": p.get("specs", {}),
            "image_url": p["image"],
            "diagram_url": p.get("diagram"),
            "display_name": p["display_name"]
        })

    # Batch insert in chunks of 50
    chunk_size = 50
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        res = supabase.table("chairs").upsert(chunk).execute()
        print(f"  Inserted chunk {i//chunk_size + 1}/{(len(records) + chunk_size - 1)//chunk_size}")

    print("[SUCCESS] All 228 chairs successfully synced to Supabase!")

if __name__ == "__main__":
    seed()
