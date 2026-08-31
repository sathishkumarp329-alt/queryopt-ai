<<<<<<< HEAD
# QueryOpt AI — Agentic SQL Query Analysis & Optimization Assistant

> Agentic Workflows Track

QueryOpt AI uses a **pipeline of 6 specialized AI agents** to analyze SQL queries, identify performance and correctness problems, generate optimized SQL, verify correctness, and produce evidence-based reports.

---

## 🏗️ Architecture

```
User Input (SQL + Schema)
        │
        ▼
  Agent Orchestrator
        │
  ┌─────┴───────────────────┐
  ▼                         ▼
SQL Analysis Agent    Performance Agent
  (parse + classify)   (EXPLAIN + timing)
        │                   │
        └────────┬──────────┘
                 ▼
         Index Agent
      (schema + coverage)
                 │
                 ▼
       Optimization Agent
        (LLM + rule-based)
                 │
                 ▼
       Verification Agent
    (equivalence + benchmarks)
                 │
                 ▼
        Report Agent
     (score + final report)
                 │
                 ▼
          Dashboard
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Google Gemini API key for LLM-powered optimizations

### 1. Clone & Install

```bash
git clone <repository>
cd queryopt-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env and optionally add your GEMINI_API_KEY
```

### 3. Initialize the Demo Database

```bash
python database/init_db.py
```

Expected output:
```
Initializing database at: database/demo.db
✓ Schema created
✓ Seed data loaded
  customers: 500 rows
  products:  200 rows
  orders:    2000 rows
  order_items: 5000 rows
  employees: 300 rows
  departments: 10 rows
  suppliers: 20 rows
Database initialized successfully!
```

### 4. Start the Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

---

## 📊 Running the Evaluation

```bash
# Run full evaluation suite (both baseline and agentic)
python evaluation/run_evaluation.py

# Calculate and display metrics
python evaluation/calculate_metrics.py
```

---

## 🧪 Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires running backend + demo DB)
pytest tests/integration/ -v

# All tests
pytest tests/ -v
```

---

## 🤖 Agent Details

| Agent | Purpose | Tools Used |
|-------|---------|-----------|
| SQL Analysis Agent | Parse SQL structure, detect obvious issues | sqlglot |
| Performance Agent | Analyze query plan, measure execution time | EXPLAIN QUERY PLAN, sqlite3 |
| Index Agent | Recommend indexes based on schema + query | schema_tool, explain_tool |
| Optimization Agent | Generate optimized SQL | Gemini API / rule-based fallback |
| Verification Agent | Verify correctness and performance improvement | query_executor, explain_tool |
| Report Agent | Score and compile final report | All agent outputs |

---

## 🔒 Security

- **Read-only mode**: Only `SELECT` and `EXPLAIN` queries are allowed on the demo database
- **Destructive SQL rejected**: `DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `UPDATE`, `INSERT` are blocked
- **No credential exposure**: All secrets via environment variables only
- **Parameterized queries**: App metadata DB uses SQLAlchemy with parameterized queries

---

## 🗂️ Project Structure

```
queryopt-ai/
├── backend/
│   ├── agents/          # 6 specialized agents
│   ├── tools/           # SQL parser, EXPLAIN tool, schema tool, executor
│   ├── orchestrator/    # Agent pipeline coordinator
│   ├── api/             # FastAPI route handlers
│   ├── models/          # Pydantic schemas + SQLAlchemy ORM
│   └── main.py          # FastAPI app entry point
├── baseline/            # Rule-based baseline (no LLM)
├── database/            # Schema, seed data, init script
├── evaluation/          # Test cases, evaluation runner, metrics
├── frontend/            # React + TypeScript + Tailwind
├── tests/               # Unit and integration tests
├── trajectories/        # Saved agent trajectory logs
├── reports/             # Exported analysis reports
└── docs/                # Additional documentation
```

---

## 🎯 Agentic Workflow vs Baseline

The baseline uses 15+ deterministic rules without any LLM. The agentic system adds:

| Capability | Baseline | QueryOpt AI |
|-----------|---------|-------------|
| SQL parsing | ✓ | ✓ |
| Rule-based detection | ✓ | ✓ |
| EXPLAIN analysis | Basic | Deep |
| Schema-aware recommendations | Partial | Full |
| LLM-generated optimization | ✗ | ✓ |
| Result equivalence verification | ✗ | ✓ |
| Performance benchmarking | ✗ | ✓ |
| Agent trajectory logging | ✗ | ✓ |
| Evidence-based confidence | ✗ | ✓ |

---

## 📋 Evaluation Test Cases

20 test cases covering:
1. SELECT * detection
2. Missing WHERE clause
3. Missing index on WHERE column
4. Inefficient JOIN (missing index on join key)
5. Function on indexed column (non-sargable)
6. Correlated subquery
7. Unnecessary ORDER BY without LIMIT
8. Redundant subquery
9. Poor aggregation
10. Large table scan
11. Multiple joins
12. Composite index opportunity
13. Already-optimal query (no false positives)
14. Query where optimization should NOT be applied
15. Complex multi-issue query
16. LIKE with leading wildcard
17. NOT IN vs NOT EXISTS
18. OR vs IN rewrite
19. Cartesian product detection
20. Unnecessary DISTINCT

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|---------|---------|-------------|
| `GEMINI_API_KEY` | No | — | Enables LLM optimization. App works without it (rule-based fallback). |
| `DEMO_DB_PATH` | No | `database/demo.db` | Path to SQLite demo database |
| `APP_DB_PATH` | No | `database/app.db` | Path to app metadata database |
| `MAX_QUERY_ROWS` | No | `1000` | Max rows returned per query |
| `QUERY_TIMEOUT_SECONDS` | No | `10` | Query execution timeout |

---

## 📄 License

MIT — Built for Agentic Workflows Hackathon.
=======
# queryopt-ai
Agentic SQL Query Analysis &amp; Optimization Assistant
>>>>>>> 118f2cd8cb141261ec2fb78272601b96dcf00b20
