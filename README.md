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

## API

Members are identified with an `X-Member-Id` header (temporary stand-in for real auth).

    # create a member
    curl -X POST localhost:5001/members -H "Content-Type: application/json" \
      -d '{"email":"alice@example.com","name":"Alice"}'

    # create a claim
    curl -X POST localhost:5001/claims -H "Content-Type: application/json" -H "X-Member-Id: 1" \
      -d '{"category":"dental","amount_cents":4500,"description":"Dental cleaning","incurred_on":"2026-09-15"}'

Errors are always JSON: `{"error": "...", "details": [...]}`.

    # list my claims (optional filters: status, limit, offset)
    curl "localhost:5001/claims?status=pending&limit=10" -H "X-Member-Id: 1"

    # get one claim
    curl localhost:5001/claims/1 -H "X-Member-Id: 1"

List response: `{"items": [...], "total": 3, "limit": 20, "offset": 0}`.
Claims belonging to other members return 404.