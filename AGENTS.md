# AGENTS.md — AdaptiMultiRAG

## Language
- 所有思考和回答使用简体中文

## Repo structure
- `rag-backend/` — Python/FastAPI + LangGraph backend (uv, Python >=3.12)
- `rag-frontend/` — Vue 3 + Vite frontend (npm)
- 每个子项目有独立的 `CLAUDE.md`，包含完整架构和配置说明

## Essential commands

| Where | Cmd | What |
|-------|-----|------|
| Backend | `uv sync` | Install Python deps |
| Backend | `python main.py` | Start FastAPI (port 8000) |
| Backend | `uv run pytest backend/tests/` | Run all tests |
| Backend | `uv run pytest backend/tests/test_xxx.py -v` | Single test file |
| Frontend | `npm install` | Install JS deps |
| Frontend | `npm run dev` | Dev server (port 5173) |
| Root | `docker compose up -d` | Start all services |
| Root | `docker compose down -v` | ⚠️ Destroy all data volumes |

## Env setup
- **Docker**: Copy `.env.docker.example` → `.env` at repo root. Hosts use Docker service names (mysql, postgres, etc.).
- **Local dev**: Create `rag-backend/backend/.env`. No `.env.example` exists; adapt from root `.env.docker.example`.
- **Required**: `DASHSCOPE_API_KEY` (阿里云 DashScope), MySQL `DB_URL`, PostgreSQL `POSTGRES_*`, `JWT_SECRET_KEY`.

## API proxy quirk
- Frontend calls use `/api/...` prefix (e.g. `/api/auth/login`, `/api/llm/chat`).
- Vite proxy rewrites `/api` → `/` → `localhost:8000` (see `vite.config.js`).
- Backend routers: `/auth`, `/llm`, `/knowledge`, `/crawl`, `/visual`, `/rag` (no `/api` prefix).

## Collection ID
Format: `kb{library_id}_{timestamp_ms}` (e.g. `kb12_1760260169325`). Generated per knowledge base; used as Milvus collection name, RAGGraph workspace param, and visual graph route.

## RAGGraph
- **Per-knowledge-base instance** (not global singleton). `get_rag_graph_for_collection(collection_id)` in `backend/config/agent.py`.
- Models: qwen3-max-preview (chat), text-embedding-v4 (1536-dim vector, DashScope).
- Dual mode: PostgreSQL checkpoint enabled by default (`LANGGRAPH_ENABLE_CHECKPOINT=true`). `langgraph dev` auto-disables it.
- 8-node workflow: start → check_retrieval → direct_answer | expand_subquestions → classify_question_type → vector/graph retrieval → generate_answer → END.

## Database notes
- **MySQL**: Business data. Auto-creates tables on startup. Use `DatabaseFactory.create_session()` (NOT deprecated `get_session()`).
- **PostgreSQL**: LangGraph checkpoint + langmem store. Auto-created tables.
- **Milvus** (vector): Needs etcd + MinIO running. Docker compose at `rag-backend/backend/rag/storage/docker-compose.yml`.
- **Neo4j** (graph): LightRAG knowledge graph. Configured via `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`.

## Tests
All 13 files in `rag-backend/backend/tests/`. Require manual model init (not global singleton). Key: `test_raggraph_simple.py`, `test_raggraph_vector.py`, `test_raggraph_lightrag.py`, `test_auth.py`.

## Docker port map (host:container)
| Service | Port |
|---------|------|
| FastAPI | 8000 |
| MySQL | 3307:3306 |
| PostgreSQL | 5432 |
| Milvus | 19530 |
| Neo4j Bolt | 7687 |
| Redis | 6379 |
| MinIO Console | 9001 |
