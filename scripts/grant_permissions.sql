-- Grant permissions to database user
-- Run this script as a superuser (e.g., postgres user)
-- Replace 'digifor' with your actual database username if different

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO digifor;

-- Grant all privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO digifor;

-- Grant all privileges on all sequences in public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO digifor;

-- Grant privileges on future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO digifor;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO digifor;

-- If you want to grant only specific permissions instead of ALL:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO digifor;

