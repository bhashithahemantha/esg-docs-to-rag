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

### Step 1 – Polite scraper 🚧

**What a scraper is:** a program that visits websites and collects files (ESG report PDFs) so I don't download them by hand.

**Analogy:** visiting someone's house.
- `robots.txt` = the sign on the front door saying which rooms bots may enter
- Being polite = read the sign first, only go where allowed, don't knock too often
- No sign (404) = every room is open

| What | Why |
|---|---|
| `USER_AGENT` | My bot's name badge + email, so site owners can contact me instead of blocking me |
| `fetch_robots(url)` | Goes to the front door and reads `site.com/robots.txt` |
| `robots_allows(text, url)` | Reads the sign and answers yes/no for one page; no internet needed, so easy to test |
| `tests/test_scraper.py` | Checks allowed page, blocked page, and "no sign = allowed" |

**Pieces:**
1. robots.txt check ✅
2. Slow down + retry
3. Find PDF links on a page
4. Download, fingerprint, log
5. Run on real ESG reports

**Interview line:** My scraper obeys robots.txt and identifies itself, so it doesn't get blocked or break site rules.