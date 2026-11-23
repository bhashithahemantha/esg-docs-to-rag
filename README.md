# esg-docs-to-rag

Scrape ESG reports → extract text from PDF/DOCX → clean → chunk → store in
Postgres + pgvector → answer questions with cited sources.

## Run it
```bash
docker compose up -d      # start Postgres + pgvector
uv sync                   # install Python libraries
uv run pytest -q          # check everything works
```

## Build log

### Step 0 – Skeleton ✅
| What | Why |
|---|---|
| `uv init --package` | Creates the project; `src/` layout so tests use the installed package |
| `uv add ...` | Installs libraries; `uv.lock` pins exact versions so it installs the same everywhere |
| `docker-compose.yml` | Runs Postgres with pgvector in a container; nothing installed on the Mac; port 5433 avoids clashes |
| `db/init.sql` | Runs once when the DB is first created; switches on pgvector |
| `config.py` | One place for the DB address; can be overridden with `DATABASE_URL` |
| `tests/test_db.py` | Automatic check that Python can reach the DB and pgvector is on |
| `ruff` | Formats code and catches mistakes |

**Gotchas I hit**
- Docker Desktop must be running first (`open -a Docker`), or you get "failed to connect to the docker API"
- `init.sql` only runs on a brand-new DB → `docker compose down` then `up -d` after changing it

**Interview line:** Reproducible (lockfile + container), and one database for both vectors and keyword search.