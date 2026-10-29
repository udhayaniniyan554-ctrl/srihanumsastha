# Sri Hanum Sastha Enterprises — Commercial Seating Catalogue Website

Official commercial chair showcase and catalogue website for **Sri Hanum Sastha Enterprises**, Coimbatore, Tamil Nadu.

Inspired by [Featherlite](https://featherlitestore.com/collections/office-chairs), this platform presents 228 commercial and institutional chair models with high-resolution genuine PDF photographs, dimensional schematics, transparent catalogue rates, sequential `SHSE` codes, and instant direct WhatsApp enquiry actions.

---

## 🚀 Key Features

1. **Featherlite-Inspired Premium Browsing Experience**:
   - **Modern Palette**: Sleek Onyx Black (`#0a0a0a`), Crisp White (`#ffffff`), and Crimson Red (`#dc2626`).
   - Sticky navigation header with mobile off-canvas drawer.
   - Live real-time search across model names, SHSE codes, categories, and ergonomic features.
   - Interactive category filter pills with model counts.
   - Sorting options by price (low-to-high, high-to-low), code sequence, and model name.
   - Dedicated Product Detail Pages ([`product.html`](file:///product.html)) featuring dual-image switcher for photographic previews and technical dimensional schematics, configuration tables, and related chair recommendations.

2. **228 Verified Catalogue Items (100% Genuine PDF Photographs)**:
   - **Office Chairs** (128 models) — Task chairs, executive mesh high-backs, workstation chairs with nylon/chrome base variants.
   - **Visitor Chairs** (48 models) — Cantilever frames, 4-leg stackable, cushion conference chairs.
   - **Lounge & Soft Seating** (24 models) — Ergonomic mould seating and modern reception pieces with dimensional schematics.
   - **Dining Chairs** (21 models) — Solid wood legs, gold metallic frames, and upholstered hospitality seating.
   - **Stools & Additional Seating** (7 models) — Stainless steel, revolving gas-lift, and heavy-duty utility seating.

3. **Approved Enquiry Channels**:
   - **WhatsApp Enquiries**: Handled exclusively through **`8695706013`** (`https://wa.me/918695706013`) with pre-composed enquiry messages containing product code, model name, and category.
   - **Direct Telephone Lines**: Direct click-to-call links and dedicated buttons for both **`9688727284`** and **`8695706013`**.

4. **Strict Brand & Privacy Compliance**:
   - Zero email addresses exposed anywhere on the public website.
   - Zero PROMAX branding or catalogue publication years.
   - No shopping cart, checkout, or online payments (showroom enquiry model only).
   - Prominent pricing disclaimer across all pages: *"Prices may change. Please contact us to confirm current prices and availability."*

---

## 🛠 Tech Stack & Architecture

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3 Custom Properties (zero heavy frontend bundle overhead, instant page loads).
- **Backend API**: Python FastAPI (`app_server.py`) with Uvicorn ASGI server.
- **Database & Cloud Storage (Option B)**: Supabase PostgreSQL with Row Level Security (RLS) and Supabase Storage bucket `chair-photos`.
- **Local Fallback**: Automatically serves and persists from `assets/catalog.json` when running offline or without Supabase keys.
- **Hosting Target**: Render Web Service (`render.yaml`).

---

## 📦 Supabase Cloud Setup (Option B)

### Free-Tier Summary & Costs
- **Supabase Free Tier**: Includes 500 MB database storage, 1 GB file storage, and 50,000 monthly active users at **$0 / month**.
- **Security Guarantee**: Public anonymous users have read-only access (`SELECT`). Write operations (`INSERT`, `UPDATE`, `DELETE`) and storage uploads are restricted to the server-side service-role key or authenticated admin sessions. Frontend client code NEVER exposes secret service keys.

### Migration & Seeding Steps
1. Create a free project on [supabase.com](https://supabase.com).
2. In the Supabase SQL Editor, run [`supabase_schema.sql`](file:///supabase_schema.sql) to create the `chairs` table, indexes, and storage bucket security policies.
3. Seed the 228 verified chair items from `catalog.json` into Supabase by running:
   ```bash
   pip install supabase
   python seed_supabase.py --url YOUR_SUPABASE_URL --key YOUR_SUPABASE_SERVICE_ROLE_KEY
   ```

---

## 🌐 Deploying to Render

This project includes a native Render Blueprint specification ([`render.yaml`](file:///render.yaml)).

### Steps to Deploy:
1. Push this repository to your GitHub or GitLab account.
2. Log in to your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Select your repository. Render will automatically read [`render.yaml`](file:///render.yaml) and configure:
   - **Service Name**: `srihanumsastha-catalogue`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app_server:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, supply your credentials:
   - `ADMIN_PASSWORD`: Your chosen admin dashboard password (default: `shse2026`).
   - `SUPABASE_URL`: Your Supabase Project URL (`https://your-ref.supabase.co`).
   - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase Service Role secret key.
6. Click **Apply**. Render will build and deploy your web service with a free SSL certificate.

---

## 💻 Running Locally

### Prerequisites
- Python 3.10+
- Dependencies: `pip install -r requirements.txt`

### Start Web Server
```bash
python app_server.py
```
Open your browser at **`http://localhost:8080`**.

### Admin Dashboard
Access the admin portal at **`http://localhost:8080/admin.html`**.
- **Default Username**: `admin`
- **Default Password**: `shse2026`

---

## 🧪 Automated Verification Suite

Run the comprehensive test suite verifying all 5 phases (REST API, page statuses, exclusive WhatsApp routing, zero email leakage, and asset integrity):
```bash
python verify_master_dev.py
```
