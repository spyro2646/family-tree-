# Architecture

FamilyRoots uses a modular monolith. The Flutter app talks to versioned FastAPI routes. The API owns authentication, authorization, and all community-scoped data. PostgreSQL is the system of record; UUIDs and composite foreign keys scope person relationships to one community.

The first implementation slice provides registration/login, community creation and listing, person creation/listing, parent-child and partnership creation, a shortest kinship path, role checks, and a cycle check. A Flutter sign-in and community/tree browsing shell calls those endpoints. The displayed member cards are not yet arranged by relationship edges; see the known limitations in the README.

Domain modules planned for the same API process: identity, communities, genealogy, collaboration, memories/media, discovery, notifications, and portability. Redis/Celery, object storage, and FCM are intentionally not wired until their configuration and credential lifecycle are defined.
