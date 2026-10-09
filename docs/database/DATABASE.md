# Database

PostgreSQL is the authoritative store. Migration `0001_initial` creates users, communities, memberships, invitations, persons, parent-child edges, and partnerships. IDs are UUIDs; timestamps are timezone aware. `community_id` is part of each kinship foreign key so cross-community links fail at the database layer. Person records use soft deletion and a version field for future optimistic updates. Invitations store token hashes and expire after seven days.

The API currently checks ancestry cycles in the service before inserting an edge. Concurrent writers can race this check; production hardening should serialize edge updates per community (or use a PostgreSQL recursive trigger/transaction advisory lock) before enabling high concurrency. Migration extensions for proposals, audit records, invitations, memories, media, notifications, sessions, devices, consent, exports, and deletion requests remain pending.
