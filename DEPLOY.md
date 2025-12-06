# Deployment Guide

## Environment Variables (.env)
You must set these before running:

FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=<database url>
JWT_SECRET_KEY=<secret>
CORS_ORIGINS=<frontend url>
ORACLE_INSTANT_CLIENT_DIR=<optional>

## Running the Backend Locally
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask db upgrade
flask run

## Docker Deployment
docker build -t cris-backend .
docker run --env-file .env -p 5000:5000 cris-backend

## Database Migrations (Flask-Migrate)
Create migration:
flask db migrate -m "message"

Apply migration:
flask db upgrade

## Oracle Production Deployment (DBA)
Generate SQL migration file:
flask db upgrade --sql > migration_for_dba.sql

Give that file to your DBA for production execution.

## Health Check
GET /health
