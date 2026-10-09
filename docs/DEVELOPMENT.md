# Development

## Prerequisites

- Python 3.12+
- PostgreSQL 16, or Docker Compose
- Flutter stable and Android SDK for mobile builds

## API

```powershell
Copy-Item .env.example .env
# Edit APP_SECRET_KEY to a random secret before starting.
docker compose up --build
```

For a local Python process, create/activate a virtual environment, install `services/api` with its `dev` extra (`python -m pip install -e ".[dev]"` from `services/api`), ensure PostgreSQL is available, then run `python -m alembic -c services/api/alembic.ini upgrade head` and `python -m uvicorn app.main:app --reload --app-dir services/api` from the repository root.

## Mobile

From `apps/mobile`, run `flutter pub get`, `flutter analyze`, `flutter test`, then `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000`. Use the machine's LAN address for a physical device.

No seed credentials are shipped. Register via `POST /api/v1/auth/register`, then create a community with the returned bearer token. The first creator becomes owner.
