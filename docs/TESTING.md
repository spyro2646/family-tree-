# Testing

Backend tests can run with `python -m pytest services/api/tests` after installing the `dev` extra. The current tests cover deterministic relationship graph behavior only. Endpoint, database integration, authorization matrix, concurrency, privacy, security, performance, and Flutter widget/integration tests are not yet implemented. They require PostgreSQL and Flutter/Android tooling respectively.
