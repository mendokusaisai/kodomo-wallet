-- Migration: Remove avatar_url column from profiles table
-- ユーザーアイコン機能の削除に伴い、profiles テーブルから avatar_url カラムを削除する
--
-- 注意: Supabase Storage の "avatars" バケットおよび RLS ポリシーの削除は
-- DB の GCP 移行時に手動で対応すること（03_storage_setup.sql 参照）

ALTER TABLE profiles DROP COLUMN IF EXISTS avatar_url;
