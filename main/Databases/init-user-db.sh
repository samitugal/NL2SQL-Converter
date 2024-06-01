#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER myuser WITH PASSWORD 'mysecretpassword';
    CREATE DATABASE northwind;
    GRANT ALL PRIVILEGES ON DATABASE northwind TO myuser;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "northwind" <<-EOSQL
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myuser;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO myuser;
EOSQL

{
  sleep 10
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "northwind" <<-EOSQL
    \i /docker-entrypoint-initdb.d/northwind.sql
EOSQL
} || {
  echo "SQL dosyası içe aktarılamadı."
}
