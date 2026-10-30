import os
import json
import secrets
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

CAT_PREFIX = {
    "Office Chairs": "OFFICE CHAIRS",
    "Visitor Chairs": "VISITOR CHAIRS",
    "Lounge & Soft Seating": "LOUNGE CHAIRS",
    "Dining Chairs": "DINING CHAIRS",
    "Stools & Additional Seating": "STOOLS"
}

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
concepts_file = os.path.join(site_dir, "assets", "concepts.json")
reviews_file = os.path.join(site_dir, "assets", "reviews.json")
products_dir = os.path.join(site_dir, "assets", "products")
active_tokens = set()

# Helper to load local catalog
def load_local_catalog() -> List[Dict[str, Any]]:
    if os.path.exists(catalog_file):
        with open(catalog_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_local_concepts() -> List[Dict[str, Any]]:
    if os.path.exists(concepts_file):
        with open(concepts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_local_catalog(data: List[Dict[str, Any]]) -> None:
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_local_reviews() -> List[Dict[str, Any]]:
    if os.path.exists(reviews_file):
        try:
            with open(reviews_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load reviews: {e}")
            return []
    return []

def save_local_reviews(data: List[Dict[str, Any]]) -> None:
    with open(reviews_file, "w", encoding="utf-8") as f:
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
        "catalogue_items": len(load_local_catalog()),
        "concepts_items": len(load_local_concepts()),
        "reviews_items": len(load_local_reviews())
    }

@app.get("/api/concepts")
def get_concepts():
    return load_local_concepts()

@app.get("/api/reviews")
def get_reviews():
    if supabase_client:
        try:
            res = supabase_client.table("customer_reviews").select("*").eq("status", "approved").order("created_at", desc=True).execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[WARN] Supabase reviews fetch failed: {e}. Falling back to local reviews.")
    reviews = load_local_reviews()
    approved = [r for r in reviews if r.get("status") == "approved"]
    return sorted(approved, key=lambda r: r.get("created_at", ""), reverse=True)

@app.get("/api/admin/reviews", dependencies=[Depends(verify_admin_token)])
def get_admin_reviews():
    if supabase_client:
        try:
            res = supabase_client.table("customer_reviews").select("*").order("created_at", desc=True).execute()
            if res.data:
                return res.data
        except Exception as e:
            print(f"[WARN] Supabase admin reviews fetch failed: {e}. Falling back to local reviews.")
    reviews = load_local_reviews()
    return sorted(reviews, key=lambda r: r.get("created_at", ""), reverse=True)

@app.put("/api/admin/reviews/{review_id}/status", dependencies=[Depends(verify_admin_token)])
def update_review_status(review_id: str, payload: Dict[str, str]):
    new_status = (payload.get("status") or "").strip().lower()
    if new_status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved', 'rejected', or 'pending'")

    local_reviews = load_local_reviews()
    found = False
    for r in local_reviews:
        if r.get("id") == review_id:
            r["status"] = new_status
            r["updated_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Review not found")

    save_local_reviews(local_reviews)

    if supabase_client:
        try:
            supabase_client.table("customer_reviews").update({"status": new_status}).eq("id", review_id).execute()
        except Exception as e:
            print(f"[ERROR] Supabase review status update failed: {e}")

    return {"success": True, "review_id": review_id, "status": new_status}

@app.post("/api/reviews")
def create_review(payload: Dict[str, Any]):
    name = (payload.get("name") or "").strip()
    rating_raw = payload.get("rating")
    comment = (payload.get("comment") or "").strip()
    location = (payload.get("location") or "").strip()

    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Please enter your name (minimum 2 characters).")
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Name must be 100 characters or fewer.")

    try:
        rating = int(rating_raw)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5.")

    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

    if not comment or len(comment) < 10:
        raise HTTPException(status_code=400, detail="Please provide your written feedback (minimum 10 characters).")
    if len(comment) > 2000:
        raise HTTPException(status_code=400, detail="Written feedback must be 2000 characters or fewer.")

    now = datetime.now(timezone.utc)
    review = {
        "id": f"rev_{int(now.timestamp())}_{secrets.token_hex(4)}",
        "name": name,
        "rating": rating,
        "comment": comment,
        "location": location if location else "Verified Customer",
        "status": "pending",
        "date": now.strftime("%d %b %Y"),
        "created_at": now.isoformat()
    }

    if supabase_client:
        try:
            supabase_client.table("customer_reviews").insert(review).execute()
        except Exception as e:
            print(f"[WARN] Supabase review insert failed: {e}")

    reviews = load_local_reviews()
    reviews.append(review)
    save_local_reviews(reviews)

    return {"success": True, "review": review}

@app.post("/api/chat")
def catalogue_chat(payload: Dict[str, Any]):
    user_msg = payload.get("message", "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message is required")
        
    catalog = get_chairs()
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("AI_API_KEY")
    
    # Check if Gemini AI key is present
    if gemini_key:
        try:
            prompt_context = f"""You are the official Catalogue Assistant for Sri Hanum Sastha Enterprises in Coimbatore, Tamil Nadu.
You answer strictly based on our 228 verified catalogue models and company information.
Showroom & Contact Details:
- Company Name: Sri Hanum Sastha Enterprises
- Address: 173, First Floor, KK Lane Street, Avinashi Road, Coimbatore, Tamil Nadu – 641018
- Phones: 9688727284 and 8695706013
- WhatsApp: 8695706013 (https://wa.me/918695706013)
- Total Models: 228 (Office Chairs: 128, Visitor Chairs: 48, Lounge & Soft Seating: 24, Dining Chairs: 21, Stools: 7)

Strict Rules:
- Never fabricate chair models, specifications, fake prices, or fake discounts.
- If information is not in the catalogue, explicitly state that it is not available.
- When recommending chairs, provide their name (e.g. OFFICE CHAIRS  SHSE 1), model name, starting rate, and markdown link to product.html?id=[id].
- Clarify that order finalization occurs via direct WhatsApp (8695706013) or phone calls; do not claim to complete checkout.

User Question: {user_msg}"""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            req_data = json.dumps({"contents": [{"parts": [{"text": prompt_context}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode("utf-8"))
                reply = res["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "reply": reply,
                    "source": "gemini_ai",
                    "disclaimer": "AI Catalogue Assistant (Live Gemini Integration)",
                    "matched_chairs": []
                }
        except Exception as e:
            print(f"[WARN] Gemini API call failed ({e}), using catalogue search engine.")

    # Explicitly Labelled Catalogue Search Engine Fallback
    q_lower = user_msg.lower()
    
    # 1. Contact / Address Queries
    if any(k in q_lower for k in ["address", "location", "where", "showroom", "visit", "phone", "contact", "email", "whatsapp", "number"]):
        reply = (
            "**Sri Hanum Sastha Enterprises — Showroom & Contact Details:**\n\n"
            "📍 **Showroom Address:** 173, First Floor, KK Lane Street, Avinashi Road, Coimbatore, Tamil Nadu – 641018\n"
            "📞 **Direct Phone Lines:** [9688727284](tel:+919688727284) & [8695706013](tel:+918695706013)\n"
            "💬 **Exclusive WhatsApp:** [8695706013](https://wa.me/918695706013)\n\n"
            "You are welcome to visit our Coimbatore showroom to inspect ergonomic models and material swatches in person!"
        )
        return {
            "reply": reply,
            "source": "catalogue_fallback",
            "disclaimer": "Catalogue Assistant (Direct Catalogue Mode — Verified Business Info)",
            "matched_chairs": []
        }
        
    # 2. Search for exact model, code, or category matches
    matched = []
    
    # Check for specific categories
    target_cat = None
    if "office" in q_lower: target_cat = "Office Chairs"
    elif "visitor" in q_lower: target_cat = "Visitor Chairs"
    elif "lounge" in q_lower or "sofa" in q_lower or "soft" in q_lower: target_cat = "Lounge & Soft Seating"
    elif "dining" in q_lower: target_cat = "Dining Chairs"
    elif "stool" in q_lower: target_cat = "Stools & Additional Seating"

    # Search items
    for item in catalog:
        code = item.get("code", "").lower()
        model = (item.get("_internal_model") or "").lower()
        cat = item.get("category", "")
        desc = (item.get("display_name") or "").lower()
        
        score = 0
        if model and model in q_lower: score += 10
        if code and code in q_lower: score += 10
        if target_cat and cat == target_cat: score += 3
        if any(word in model or word in code for word in q_lower.split() if len(word) > 2): score += 2
        
        if score > 0:
            matched.append((score, item))
            
    matched.sort(key=lambda x: x[0], reverse=True)
    top_matches = [m[1] for m in matched[:4]]
    
    if top_matches:
        lines = [f"Found {len(matched)} matching verified models in our commercial catalogue:\n"]
        for m in top_matches:
            c_code = m.get("code")
            c_model = m.get("_internal_model", "Standard")
            c_price = m.get("price_display", f"₹{m.get('base_price', 0):,}")
            c_cat = m.get("category")
            c_id = m.get("id")
            wa_text = urllib.parse.quote(f"Hello Sri Hanum Sastha Enterprises, I am interested in chair {c_code} (Model: {c_model}) from the {c_cat} category.")
            lines.append(f"- **[{c_code} — {c_model}](product.html?id={c_id})** ({c_cat})\n  *Listed Rate:* {c_price} • [View Details](product.html?id={c_id}) | [WhatsApp Enquiry](https://wa.me/918695706013?text={wa_text})")
            
        lines.append("\n*Prices may change. Please contact us via WhatsApp (8695706013) to confirm availability and exact configuration options.*")
        reply = "\n".join(lines)
    else:
        # Default helpful overview
        reply = (
            "We have 228 verified commercial chair models across 5 categories in our Coimbatore catalogue:\n\n"
            "- **Office Chairs (128 models):** Ergonomic task, executive high back, Korean mesh.\n"
            "- **Visitor Chairs (48 models):** Cantilever, 4-leg meeting, and conference seating.\n"
            "- **Lounge & Soft Seating (24 models):** Molded reception armchairs and sofas.\n"
            "- **Dining Chairs (21 models):** Solid wood and metallic cafe seating.\n"
            "- **Stools & Additional Seating (7 models):** Lab gas-lift stools.\n\n"
            "Try searching by model name (e.g. `ATLAS`, `4G`, `ALEX`), product code (`OFFICE CHAIRS  SHSE 1` or `SHSE 1`), or ask for our showroom contact details!"
        )

    return {
        "reply": reply,
        "source": "catalogue_fallback",
        "disclaimer": "Catalogue Assistant (Direct Mode — 228 Verified Catalog Items)",
        "matched_chairs": top_matches
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
            raise HTTPException(status_code=400, detail=f"Duplicate code SHSE {code_number} in {category}")

    # Generate id if missing
    if not chair.get("id"):
        chair["id"] = f"{category.lower().split(' ')[0]}_{code_number}"
    
    prefix = CAT_PREFIX.get(category, category.upper())
    chair["code"] = f"SHSE {code_number}"
    chair["display_name"] = f"{prefix}  SHSE {code_number}"
    chair["name"] = chair["display_name"]
    
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

@app.delete("/api/admin/reviews/{review_id}", dependencies=[Depends(verify_admin_token)])
def delete_review(review_id: str):
    local_reviews = load_local_reviews()
    new_reviews = [r for r in local_reviews if r.get("id") != review_id]
    if len(new_reviews) == len(local_reviews):
        raise HTTPException(status_code=404, detail="Review not found")

    save_local_reviews(new_reviews)

    if supabase_client:
        try:
            supabase_client.table("customer_reviews").delete().eq("id", review_id).execute()
        except Exception as e:
            print(f"[ERROR] Supabase review delete failed: {e}")

    return {"success": True, "deleted_id": review_id, "message": "Review permanently deleted"}

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
