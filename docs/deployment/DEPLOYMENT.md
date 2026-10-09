# Deployment

The Compose file is intended for local development. Production deployment still needs a managed PostgreSQL service, HTTPS reverse proxy, non-default secrets, restrictive network policy, persistent backups, monitoring, and a rollout process that runs Alembic migrations before API instances accept traffic. Configure allowed origins and email delivery before enabling browser clients or verification flows. No production environment is supplied.
