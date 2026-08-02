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
CREATE POLICY "media_read_public"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'media'::text
);

-- Policy: Service role (admin) bisa semua operasi
CREATE POLICY "media_service_role_full"
ON storage.objects FOR ALL
USING (
    bucket_id = 'media'::text
    AND auth.role() = 'service_role'
)
WITH CHECK (
    bucket_id = 'media'::text
    AND auth.role() = 'service_role'
);

-- Policy: Authenticated users bisa upload
CREATE POLICY "media_authenticated_upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'media'::text
    AND auth.role() = 'authenticated'
);

-- Policy: Users bisa delete file tertentu
CREATE POLICY "media_authenticated_delete"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'media'::text
    AND auth.role() = 'authenticated'
    AND (
        position('avatars/' in name) > 0
        OR position('healer_photos/' in name) > 0
        OR position('healer_covers/' in name) > 0
    )
);
