#!/bin/sh
set -eu

: "${SECRET_KEY:?SECRET_KEY is required}"
: "${DATABASE_URL:?DATABASE_URL is required; do not use ephemeral SQLite in production}"
: "${SUPABASE_ENDPOINT:?SUPABASE_ENDPOINT is required for persistent uploads}"
: "${SUPABASE_ACCESS_KEY:?SUPABASE_ACCESS_KEY is required for persistent uploads}"
: "${SUPABASE_SECRET_KEY:?SUPABASE_SECRET_KEY is required for persistent uploads}"

python manage.py migrate --noinput
exec gunicorn pr_eni.wsgi:application \
    --bind "0.0.0.0:${PORT:-10000}" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -