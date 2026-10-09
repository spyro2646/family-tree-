# Operations

Local services: `docker compose up --build`; stop with `docker compose down`. Persistent development data is in the `postgres_data` volume. Before any production use, define an encrypted backup schedule, restore drills, retention/deletion policy, alerting, and secrets rotation. The repository does not yet include production backup or restore automation.
