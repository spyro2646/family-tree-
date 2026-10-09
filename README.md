# FamilyRoots

FamilyRoots is a multi-community genealogy platform. The repository is a monorepo with a FastAPI/PostgreSQL backend and a Flutter Android client.

## Current implementation

The API foundation includes account registration and login, bearer token authentication, community creation/listing, role-checked person and kinship APIs, and ancestry cycle checks. Run it locally with Docker Compose or a Python virtual environment; see [DEVELOPMENT.md](docs/DEVELOPMENT.md). The Flutter client source is under `apps/mobile`.

This is an active implementation, not a production deployment. Email delivery, refresh-token rotation, media storage, mobile offline synchronization, and the remaining product modules are documented as pending in [docs/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).

## Quick start

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000`; OpenAPI is at `/docs` and liveness is at `/health/live`.

## Documentation

- [Development](docs/DEVELOPMENT.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Implementation checklist](docs/IMPLEMENTATION_PLAN.md)
- [Database](docs/database/DATABASE.md)
- [API](docs/api/API.md)
- [Security](docs/security/SECURITY.md)
- [Deployment](docs/deployment/DEPLOYMENT.md)
- [Android build](docs/deployment/ANDROID_BUILD.md)
- [Testing](docs/TESTING.md)
- [Operations](docs/OPERATIONS.md)
