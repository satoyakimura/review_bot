-- create role
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'review_bot') THEN
        CREATE ROLE review_bot WITH LOGIN PASSWORD 'h6nvjwli';
    END IF;
END $$;

-- create database
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'review_bot') THEN
        CREATE DATABASE review_bot;
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE review_bot TO review_bot;
