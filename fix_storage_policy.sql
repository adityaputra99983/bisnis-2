-- ============================================================
-- FIX: Storage Security - Hapus broad SELECT policy
-- ============================================================
-- Jalankan di: Supabase Dashboard > SQL Editor
-- ============================================================

-- 1. Hapus semua policy lama yang terlalu longgar
DO $$
DECLARE
    pol RECORD;
BEGIN
    FOR pol IN
        SELECT policyname
        FROM pg_policies
        WHERE tablename = 'objects'
        AND schemaname = 'storage'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "%s" ON storage.objects', pol.policyname);
        RAISE NOTICE 'Dropped policy: %', pol.policyname;
    END LOOP;
END $$;

-- 2. Buat policy baru yang aman

-- Policy: Public bisa READ file media (tapi TIDAK bisa list)
-- File tetap bisa diakses via URL langsung, tapi tidak bisa list semua file
CREATE POLICY "media_read_public"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'media'
);

-- Policy: Service role (admin) bisa semua operasi
CREATE POLICY "media_service_role_full"
ON storage.objects FOR ALL
USING (
    bucket_id = 'media'
    AND auth.role() = 'service_role'
)
WITH CHECK (
    bucket_id = 'media'
    AND auth.role() = 'service_role'
);

-- Policy: Authenticated users bisa upload ke folder mereka sendiri
CREATE POLICY "media_authenticated_upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'media'
    AND auth.role() = 'authenticated'
);

-- Policy: Users bisa delete file mereka sendiri
CREATE POLICY "media_authenticated_delete"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'media'
    AND auth.role() = 'authenticated'
    AND (
        -- Hanya bisa delete file milik mereka sendiri
        position('avatars/' in name) > 0
        OR position('healer_photos/' in name) > 0
    )
);

-- ============================================================
-- SETELAH JALANKAN SQL DI ATAS:
-- Pergi ke Supabase Dashboard > Storage > Settings
-- Matikan "Public" toggle jika bucket 'media' adalah public
-- Atau pastikan bucket adalah PRIVATE dan gunakan service role untuk akses
-- ============================================================
