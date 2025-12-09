#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# --- DESACTIVAR MIGRACIONES PROBLEMÁTICAS ---
python manage.py migrate contenttypes zero --fake
python manage.py migrate contenttypes 0001 --fake

python manage.py migrate auth zero --fake
python manage.py migrate auth 0001 --fake

# --- Marcar todo como aplicado ---
python manage.py migrate --fake

# --- Static files ---
python manage.py collectstatic --noinput
