# Phase 2 Task API

A backend API for managing personal tasks.

Users can create an account, log in, and manage their own tasks. Each user can only access their own data.

## What the Project Can Do

- Register new users
- Log users in
- Protect routes with JWT tokens
- Create tasks
- View tasks
- Update tasks
- Delete tasks
- Keep each user’s tasks private
- Filter, sort, and paginate tasks
- Save data in PostgreSQL
- Update the database with Alembic migrations
- Run automated tests with pytest
- Run the API and database with Docker
- Run tests automatically with GitHub Actions

## Main Technologies

- **FastAPI** — handles API requests and routes
- **PostgreSQL** — stores users and tasks
- **SQLAlchemy** — lets Python work with the database
- **Alembic** — updates the database structure
- **Pydantic** — checks incoming data
- **PyJWT** — creates and reads login tokens
- **pytest** — tests the project
- **Docker Compose** — runs the API and database together
- **GitHub Actions** — automatically runs tests after code is pushed

## Run the Project with Docker

Create a `.env` file using `.env.example` as a guide.

Start the API and PostgreSQL database:

```bash
docker compose up --build
```

Open the automatic API documentation:

```text
http://localhost:8000/docs
```

Stop the project:

```bash
docker compose down
```

## Environment Variables

The `.env` file should contain:

```env
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30

DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tasks_db
```

These values tell the application:

- what secret to use for login tokens
- how long login tokens should last
- how to connect to PostgreSQL

Do not upload the real `.env` file to GitHub.

## Run the Tests

```bash
python -m pytest
```

## Health Checks

Check whether the API is running:

```text
GET /health
```

Check whether the API can connect to PostgreSQL:

```text
GET /db-health
```

## Project Status

The main backend is complete.

It includes:

- user registration and login
- password hashing
- JWT authentication
- task ownership and authorization
- PostgreSQL database storage
- Alembic database migrations
- automated tests
- Docker support
- GitHub Actions continuous integration