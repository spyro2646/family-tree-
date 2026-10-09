# Security

Passwords use Argon2id via `argon2-cffi`. Access tokens are signed HS256 JWTs with a short expiry. The signing key must be supplied through `APP_SECRET_KEY`; use a randomly generated value of at least 32 bytes and keep `.env` out of version control. Membership is verified on each community operation and role checks guard writes. Non-members receive a not-found response to reduce community enumeration. Composite database foreign keys prevent cross-community genealogy edges. Private profiles are omitted from community-wide list results.

This is a development foundation, not a production security sign-off. Login rate limiting, email verification and recovery, rotating refresh sessions, proposal approval, comprehensive living-person privacy, audit logging, media authorization, CSP/TLS deployment, and dependency/security scans remain to implement. Do not deploy with the example database password or a development secret.
