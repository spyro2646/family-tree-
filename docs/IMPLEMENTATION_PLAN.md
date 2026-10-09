# Implementation checklist

## Phase 0: repository and architecture

- [x] Monorepo layout, Python package, Flutter package manifest, Docker Compose, CI starting point
- [x] FastAPI app shell, PostgreSQL models, initial Alembic migration, health route
- [x] Architecture, development, security, database, API, deployment, Android, testing, and operations notes
- [ ] Flutter/Android generated platform and verified builds (toolchain unavailable in initial environment)

## Phase 1: identity and communities

- [x] Password registration/login and short-lived signed access token
- [x] Create/list communities and owner membership
- [x] Hashed, expiring invitation tokens with email-matched acceptance
- [ ] Verification/recovery email, refresh token rotation, rate limits, invitation email and revocation

## Phase 2: genealogy

- [x] Person create/list, community-scoped parent-child and partnership records
- [x] Directed ancestry cycle check and kinship path calculation
- [ ] Person edits with optimistic locking, richer date/name fields, graph endpoint and relationship-aware tree layout

## Phase 3: collaboration and privacy

- [ ] Proposed edits, approvals, immutable audit history, branch permissions, moderation, conflict handling
- [ ] Complete living-person privacy rules and authorization tests

## Phase 4: memories and discovery

- [ ] Private media, memories, privacy-aware indexed search, notifications and device tokens

## Phase 5: offline and portability

- [ ] Drift-backed offline cache, JSON/CSV/GEDCOM/PDF import/export

## Phase 6: production hardening

- [ ] PostgreSQL integration/security/performance/accessibility test suites
- [ ] Redis/background jobs, object storage, monitoring, backups, restore drills and production deployment
- [ ] Signed release bundle/APK after backend configuration and release checks
