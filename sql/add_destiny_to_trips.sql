-- Add 'destiny' column to trips table (Neon/PostgreSQL)
-- Run on your Neon database before deploying the API changes that start writing this column.

ALTER TABLE public.trips
    ADD COLUMN IF NOT EXISTS destiny TEXT NULL;

-- Optional: backfill or index examples
-- UPDATE public.trips SET destiny = NULL WHERE destiny IS NULL;
-- CREATE INDEX IF NOT EXISTS ix_trips_destiny ON public.trips (destiny);

