3 Critical issues:
1. Zero Alembic migrations (schema relies entirely on create_all())
2. datetime.utcnow() deprecated in 34 places (Python 3.12+)
3. Dev ports are misconfigured — Vite runs on :5174 proxying to :8001, but CORS allows :5173 and docs say :5173/:8000
6 High issues: No pagination on any endpoint, zero application logging, missing root .gitignore, broken niche filter scoring, config file divergence, and Alembic missing the learning model import.
8 Medium issues include dead code (events module), missing DB indexes, no password policy, Postgres-only SQL in audit services, and stale documentation.
9 Low issues cover frontend gaps (no 404 route, full page reloads, unused chart components) and minor validation gaps.