# API

Run the API, then open `/docs` for the generated OpenAPI contract. All routes except `/health/live`, registration, and login require a short-lived bearer access token.

Implemented routes:

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- `POST /api/v1/communities`, `GET /api/v1/communities`
- `POST /api/v1/communities/{community_id}/invitations`, `POST /api/v1/invitations/accept`
- `GET|POST /api/v1/communities/{community_id}/persons`
- `POST /api/v1/communities/{community_id}/relationships/parents`
- `POST /api/v1/communities/{community_id}/relationships/partnerships`
- `GET /api/v1/communities/{community_id}/relationships/path?person_a=UUID&person_b=UUID`

Invitation creation returns a single-use raw token for the owner/admin to deliver manually; storage keeps only its SHA-256 hash. Acceptance requires a signed-in account with the invited email. Email delivery, revocation route, public community directory, refresh-token endpoint, and edit/delete routes are not implemented yet.
