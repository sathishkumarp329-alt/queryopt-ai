# QueryOpt AI — Hackathon 5-Minute Presentation & Demo Guide

## ⏱️ 5-Minute Presentation Script

### 0:00 – 0:30 · The Problem
> "Database performance degradation in production is rarely caused by database engine bugs — it's almost always caused by inefficient SQL queries written by developers: non-sargable functions, missing composite indexes, wildcard SELECTs, and unintentional full table scans. Standard AI chatbots often hallucinate SQL rewrites that silently change query semantics or don't actually improve database performance."

### 0:30 – 1:00 · The Baseline vs Agentic Solution
> "Traditional linters and rule-based analyzers only catch superficial regex patterns without physical database execution evidence. We built **QueryOpt AI**: a 6-agent system that pairs structural AST analysis with actual physical EXPLAIN query plans, automated index recommendations, LLM rewrites, and a strict verification safety gate that tests output equivalence before recommending any change."

### 1:00 – 3:00 · Live QueryOpt AI Demonstration
1. **Enter Query**: Select Preset #1:
   ```sql
   SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024';
   ```
2. **Click Analyze Query**: Watch the orchestrator coordinate all 6 agents in real-time.
3. **Show Scores & Findings**:
   - SQL Quality Score: ~47/100
   - Detected non-sargable `strftime('%Y', order_date)` forcing full table scan across 2,000 orders.
   - Detected `SELECT *` projection antipattern.
4. **Show Side-by-Side Diff**:
   - Original: `strftime('%Y', order_date) = '2024'`
   - Optimized: `order_date >= '2024-01-01' AND order_date < '2025-01-01'` (Sargable date range).
5. **Show Physical Query Plan & Verification Badge**:
   - Verification Agent tested output equivalence and confirmed physical index search utilization.
6. **Show Multi-Agent Trajectory**: Step-by-step transparency audit trail.

### 3:00 – 4:00 · Empirical Evaluation & Benchmark
1. Navigate to the **Evaluation** tab.
2. Review the comparative table measured across 20 diverse test cases:
   - **Problem Detection Recall**: Jumped from **61.1%** (Baseline) to **90.5%** (QueryOpt AI) — a **+29.4%** improvement.
   - **F1 Score**: Improved by **+12.3%**.
   - **False Positive Rate**: Reduced across test suites.

### 4:00 – 4:30 · Safety & The Verification Gate
> "Notice the Optimization Correctness metric: QueryOpt AI flagged 2 candidate rewrites that produced subtle row count differences and rejected them. A simple LLM would have returned those broken queries to the developer. Our Verification Agent prevented production bugs."

### 4:30 – 5:00 · Hot Take & Conclusion
> **Hot Take**: *"LLM-generated SQL optimization is never an optimization until verified by query-plan evidence and result-equivalence tests. Generative AI needs deterministic database verifiers to be safe in enterprise environments."*

---

## 🎯 Sample Queries for Demo

| # | Name | Query SQL | Key Insight to Highlight |
|---|------|-----------|--------------------------|
| 1 | Non-Sargable Function | `SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024';` | Converts to index range scan `[2024-01-01, 2025-01-01)` |
| 2 | Cartesian Product | `SELECT customers.first_name, orders.order_id FROM customers, orders;` | Flags critical M x N combinatorial explosion |
| 3 | Unindexed Filter | `SELECT order_id, total_amount FROM orders WHERE shipping_city = 'Chicago';` | Recommends `CREATE INDEX idx_orders_shipping_city` |
| 4 | Optimal Query | `SELECT o.order_id, o.order_date, c.first_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.customer_id = 42;` | Score 100/100, zero false positives |
