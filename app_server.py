import os
import json
import secrets
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Environment configuration
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "shse2026")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

# Initialize Supabase client if configured
supabase_client = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("[INFO] Connected to Supabase Cloud Database.")
    except Exception as e:
        print(f"[WARN] Supabase initialization failed ({e}), falling back to local JSON.")

app = FastAPI(
    title="Sri Hanum Sastha Enterprises API & Website",
    description="FastAPI Backend for Sri Hanum Sastha Enterprises Chair Catalogue and Admin",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

site_dir = os.path.dirname(os.path.abspath(__file__))
catalog_file = os.path.join(site_dir, "assets", "catalog.json")
products_dir = os.path.join(site_dir, "assets", "products")
active_tokens = set()

# Helper to load local catalog
def load_local_catalog() -> List[Dict[str, Any]]:
    if os.path.exists(catalog_file):
        with open(catalog_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_local_catalog(data: List[Dict[str, Any]]) -> None:
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Auth dependency
def verify_admin_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Admin authorization required")
    token = authorization.replace("Bearer ", "").strip()
    if token not in active_tokens and token != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin session token")
    return True

# ---------------- API ENDPOINTS ----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "supabase_connected": supabase_client is not None,
        "catalogue_items": len(load_local_catalog())
    }

@app.get("/api/chairs")
def get_chairs():
    # If Supabase is connected, query Supabase
    if supabase_client:
        try:
            res = supabase_client.table("chairs").select("*").order("category").order("code_number").execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[ERROR] Supabase fetch failed: {e}. Using local JSON fallback.")
    return load_local_catalog()

@app.get("/api/chairs/{chair_id}")
def get_chair(chair_id: str):
    chairs = get_chairs()
    for c in chairs:
        if c.get("id") == chair_id or c.get("code") == chair_id:
            return c
    raise HTTPException(status_code=404, detail="Chair not found")

@app.post("/api/admin/login")
def admin_login(payload: Dict[str, str]):
    user = payload.get("username", "")
    password = payload.get("password", "")
    if user == "admin" and password == ADMIN_PASSWORD:
        token = secrets.token_hex(24)
        active_tokens.add(token)
        return {"success": True, "token": token, "message": "Authenticated successfully"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/admin/chairs", dependencies=[Depends(verify_admin_token)])
def add_chair(chair: Dict[str, Any]):
    category = chair.get("category")
    code_number = chair.get("code_number")
    
    # Duplicate check within same category
    existing = get_chairs()
    for ex in existing:
        if ex.get("category") == category and ex.get("code_number") == code_number:
            raise HTTPException(status_code=400, detail=f"Duplicate code SHSE({code_number}) in {category}")

    # Generate id if missing
    if not chair.get("id"):
        chair["id"] = f"{category.lower().split(' ')[0]}_{code_number}"
    
    chair["code"] = f"SHSE({code_number})"
    chair["display_name"] = f"{category} — SHSE({code_number})"
    
    # Save to Supabase if available
    if supabase_client:
        try:
            supabase_client.table("chairs").insert(chair).execute()
        except Exception as e:
            print(f"[ERROR] Supabase insert failed: {e}")

    # Always persist to local catalog.json
    local_data = load_local_catalog()
    local_data.append(chair)
    save_local_catalog(local_data)

    return {"success": True, "chair": chair}

@app.put("/api/admin/chairs/{chair_id}", dependencies=[Depends(verify_admin_token)])
def update_chair(chair_id: str, chair: Dict[str, Any]):
    local_data = load_local_catalog()
    found = False
    for i, c in enumerate(local_data):
        if c.get("id") == chair_id:
            local_data[i] = chair
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Chair not found")

    save_local_catalog(local_data)

    if supabase_client:
        try:
            supabase_client.table("chairs").upsert(chair).execute()
        except Exception as e:
            print(f"[ERROR] Supabase update failed: {e}")

    return {"success": True, "chair": chair}

@app.delete("/api/admin/chairs/{chair_id}", dependencies=[Depends(verify_admin_token)])
def delete_chair(chair_id: str):
    local_data = load_local_catalog()
    new_data = [c for c in local_data if c.get("id") != chair_id]
    if len(new_data) == len(local_data):
        raise HTTPException(status_code=404, detail="Chair not found")

    save_local_catalog(new_data)

    if supabase_client:
        try:
            supabase_client.table("chairs").delete().eq("id", chair_id).execute()
        except Exception as e:
            print(f"[ERROR] Supabase delete failed: {e}")

    return {"success": True, "deleted_id": chair_id}

@app.post("/api/admin/upload", dependencies=[Depends(verify_admin_token)])
async def upload_image(file: UploadFile = File(...)):
    filename = file.filename
    clean_filename = f"upload_{secrets.token_hex(6)}_{filename}"
    file_path = os.path.join(products_dir, clean_filename)
    
    # Read and save locally
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    rel_url = f"assets/products/{clean_filename}"

    # Upload to Supabase Storage bucket 'chair-photos' if available
    if supabase_client:
        try:
            supabase_client.storage.from_("chair-photos").upload(
                path=clean_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )
            pub_url = supabase_client.storage.from_("chair-photos").get_public_url(clean_filename)
            rel_url = pub_url
        except Exception as e:
            print(f"[WARN] Supabase storage upload failed: {e}. Saved locally.")

    return {"success": True, "url": rel_url}

# ---------------- STATIC ROUTING ----------------

@app.get("/product.html")
def serve_product():
    return FileResponse(os.path.join(site_dir, "product.html"))

@app.get("/category.html")
def serve_category():
    return FileResponse(os.path.join(site_dir, "category.html"))

@app.get("/contact.html")
def serve_contact():
    return FileResponse(os.path.join(site_dir, "contact.html"))

@app.get("/admin.html")
def serve_admin():
    return FileResponse(os.path.join(site_dir, "admin.html"))

# Mount static assets and files
app.mount("/", StaticFiles(directory=site_dir, html=True), name="site")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Sri Hanum Sastha Web Service at http://127.0.0.1:{port}")
    uvicorn.run("app_server:app", host="0.0.0.0", port=port, reload=False)
