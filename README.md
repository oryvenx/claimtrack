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

## Reviewer endpoints

Reviewers authenticate with a shared secret in `X-Reviewer-Key` (set `REVIEWER_API_KEY` in `.env`).

    curl -X POST localhost:5001/claims/1/approve -H "X-Reviewer-Key: $KEY"
    curl -X POST localhost:5001/claims/1/reject  -H "X-Reviewer-Key: $KEY"

A claim can be decided once: deciding an already decided claim returns 409.
The check and update happen in a single atomic SQL statement to avoid races.

## Tests

Tests run against a separate Postgres database (`claimtrack_test`), built from the migrations.

    pip install -r requirements-dev.txt
    docker compose up -d
    docker compose exec db psql -U claimtrack -d claimtrack -c "CREATE DATABASE claimtrack_test;"   # once
    pytest

Override the database with `TEST_DATABASE_URL` (its name must end in `_test`).