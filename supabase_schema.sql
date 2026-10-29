-- ========================================================
-- Supabase Schema for Sri Hanum Sastha Enterprises
-- Table: chairs, Storage: chair-photos, Row Level Security
-- ========================================================

-- 1. Create Chairs Table
CREATE TABLE IF NOT EXISTS public.chairs (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    code TEXT NOT NULL,
    code_number INTEGER NOT NULL,
    model_name TEXT,
    price_display TEXT NOT NULL,
    base_price NUMERIC NOT NULL DEFAULT 0,
    options JSONB DEFAULT '[]'::jsonb,
    features JSONB DEFAULT '[]'::jsonb,
    specs JSONB DEFAULT '{}'::jsonb,
    image_url TEXT NOT NULL,
    diagram_url TEXT,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_chairs_category ON public.chairs (category);
CREATE INDEX IF NOT EXISTS idx_chairs_code ON public.chairs (code);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.chairs ENABLE ROW LEVEL SECURITY;

-- 3. RLS Policies:
-- Allow ANY anonymous visitor to read chairs (Public Catalogue)
CREATE POLICY "Public can view catalogue chairs"
    ON public.chairs
    FOR SELECT
    USING (true);

-- Only authenticated backend (via service_role or admin auth) can insert/update/delete
CREATE POLICY "Admin can insert chairs"
    ON public.chairs
    FOR INSERT
    TO authenticated, service_role
    WITH CHECK (true);

CREATE POLICY "Admin can update chairs"
    ON public.chairs
    FOR UPDATE
    TO authenticated, service_role
    USING (true);

CREATE POLICY "Admin can delete chairs"
    ON public.chairs
    FOR DELETE
    TO authenticated, service_role
    USING (true);

-- 4. Storage Bucket Setup
-- Note: Create bucket 'chair-photos' in Supabase Dashboard > Storage
-- Public Read Policy for bucket:
-- INSERT INTO storage.buckets (id, name, public) VALUES ('chair-photos', 'chair-photos', true);
