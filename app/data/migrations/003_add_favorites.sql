-- Add is_favorite column to vault_items
ALTER TABLE vault_items ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0;
