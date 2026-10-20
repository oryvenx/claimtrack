# ClaimTrack

A small health insurance claims API built with Flask, SQLAlchemy and PostgreSQL.
Practice project for the Alan stack.

## Run locally

    source .venv/bin/activate
    flask --app wsgi run --debug --port 5001

Health check: `curl http://localhost:5001/health`