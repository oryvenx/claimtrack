# ClaimTrack

A small health insurance claims API built with Flask, SQLAlchemy and PostgreSQL.
Practice project for the Alan stack.

## Run locally

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    docker compose up -d
    flask --app wsgi db upgrade
    flask --app wsgi run --debug --port 5001

Checks: `curl http://localhost:5001/health` and `curl http://localhost:5001/health/db`

## Database migrations

    flask --app wsgi db migrate -m "describe the change"   # generate
    flask --app wsgi db upgrade                            # apply
    flask --app wsgi db downgrade                          # roll back one step