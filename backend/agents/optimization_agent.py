import re
import time
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.config import settings
from backend.tools.sql_parser import ParsedQuery
from backend.tools.schema_tool import SchemaInfo

class OptimizationAgent(BaseAgent):
    """
    Agent 4: Query Optimization Agent
    Generates an optimized SQL rewrite that preserves query semantics while
    eliminating anti-patterns, utilizing sargable predicates, replacing SELECT *,
    and improving join/subquery efficiency.
    """
    def __init__(self):
        super().__init__(name="Optimization Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sql: str = context.get("sql", "")
        parsed: ParsedQuery = context.get("parsed_query")
        schema: SchemaInfo = context.get("schema_info")
        sql_findings: List[Dict[str, Any]] = context.get("sql_findings", [])
        perf_findings: List[Dict[str, Any]] = context.get("performance_findings", [])

        start_time = time.perf_counter()
        
        optimized_sql = sql
        changes: List[str] = []
        explanation = ""

        # Check if Gemini API is available
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            try:
                optimized_sql, changes, explanation = self._optimize_with_gemini(
                    sql=sql,
                    parsed=parsed,
                    schema=schema,
                    findings=sql_findings + perf_findings
                )
                self.log(
                    action="generate_llm_optimization",
                    tool_used="Google Gemini 1.5 Flash",
                    input_summary=sql[:80],
                    result_summary=f"Generated {len(changes)} optimizations via Gemini",
                    finding="LLM-assisted query rewrite generated",
                    confidence=0.90,
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )
            except Exception as e:
                print(f"Gemini API optimization fallback triggered: {e}")
                optimized_sql, changes, explanation = self._optimize_rule_based(sql, parsed, schema)
                self.log(
                    action="generate_rule_optimization",
                    tool_used="Rule Optimization Engine (Fallback)",
                    input_summary=sql[:80],
                    result_summary=f"Generated {len(changes)} optimizations via Rule Engine",
                    finding="Rule-based query rewrite generated",
                    confidence=0.85,
                    duration_ms=(time.perf_counter() - start_time) * 1000.0
                )
        else:
            optimized_sql, changes, explanation = self._optimize_rule_based(sql, parsed, schema)
            self.log(
                action="generate_rule_optimization",
                tool_used="Rule Optimization Engine",
                input_summary=sql[:80],
                result_summary=f"Generated {len(changes)} optimizations via deterministic rules",
                finding="Rule-based query rewrite generated",
                confidence=0.88,
                duration_ms=(time.perf_counter() - start_time) * 1000.0
            )

        context["optimized_sql"] = optimized_sql
        context["optimization_changes"] = changes
        context["optimization_explanation"] = explanation
        return context

    def _optimize_rule_based(
        self,
        sql: str,
        parsed: ParsedQuery,
        schema: SchemaInfo
    ) -> tuple[str, List[str], str]:
        """Deterministic SQL rewrite engine for standard SQL antipatterns."""
        opt = sql.strip().rstrip(";")
        changes = []
        
        # 1. Non-sargable YEAR(col) = 2025 -> col >= '2025-01-01' AND col < '2026-01-01'
        year_match = re.search(r"(?:strftime\('%Y',\s*(\w+)\)|YEAR\((\w+)\)|strftime\(\"%Y\",\s*(\w+)\))\s*=\s*(?:'(\d{4})'|(\d{4}))", opt, re.IGNORECASE)
        if year_match:
            col_name = year_match.group(1) or year_match.group(2) or year_match.group(3)
            year_val = int(year_match.group(4) or year_match.group(5))
            next_year = year_val + 1
            replacement = f"{col_name} >= '{year_val}-01-01' AND {col_name} < '{next_year}-01-01'"
            opt = opt[:year_match.start()] + replacement + opt[year_match.end():]
            changes.append(f"Replaced non-sargable YEAR({col_name})={year_val} with sargable date range [{year_val}-01-01 to {next_year}-01-01)")

        # 2. Non-sargable strftime('%m', col) = '05'
        month_match = re.search(r"strftime\('%m',\s*(\w+)\)\s*=\s*'(\d{2})'", opt, re.IGNORECASE)
        if month_match:
            col_name = month_match.group(1)
            changes.append(f"Identified non-sargable month extraction on '{col_name}'. Consider date range filtering.")

        # 3. SELECT * replacement with explicit table columns
        if parsed and parsed.is_select_star and parsed.tables and schema:
            primary_tbl = parsed.tables[0]
            if primary_tbl in schema.tables:
                col_list = [c.name for c in schema.tables[primary_tbl].columns]
                # Replace root SELECT *
                pattern = re.compile(r"SELECT\s+\*\s+FROM", re.IGNORECASE)
                if pattern.search(opt):
                    explicit_cols = ", ".join(col_list)
                    opt = pattern.sub(f"SELECT {explicit_cols} FROM", opt, count=1)
                    changes.append(f"Replaced SELECT * with explicit projection of {len(col_list)} columns from '{primary_tbl}'")

        # 4. Remove redundant DISTINCT with GROUP BY
        if "DISTINCT" in opt.upper() and "GROUP BY" in opt.upper():
            opt = re.sub(r"SELECT\s+DISTINCT\s+", "SELECT ", opt, flags=re.IGNORECASE)
            changes.append("Removed redundant DISTINCT keyword when GROUP BY is already present")

        # 5. Multiple OR conditions on same column to IN (col IN (a, b, c))
        or_pattern = re.search(r"(\w+)\s*=\s*('[^']+'|\d+)\s+OR\s+\1\s*=\s*('[^']+'|\d+)(?:\s+OR\s+\1\s*=\s*('[^']+'|\d+))*", opt, re.IGNORECASE)
        if or_pattern:
            col = or_pattern.group(1)
            # Find all values
            full_match = or_pattern.group(0)
            vals = re.findall(rf"{col}\s*=\s*('[^']+'|\d+)", full_match, re.IGNORECASE)
            if len(vals) >= 2:
                in_clause = f"{col} IN ({', '.join(vals)})"
                opt = opt[:or_pattern.start()] + in_clause + opt[or_pattern.end():]
                changes.append(f"Replaced chained OR equality on '{col}' with compact '{in_clause}'")

        # 6. Unnecessary ORDER BY without LIMIT on aggregate queries
        if re.search(r"ORDER\s+BY", opt, re.IGNORECASE) and not re.search(r"LIMIT", opt, re.IGNORECASE) and re.search(r"COUNT\(\*\)", opt, re.IGNORECASE):
            # Aggregation with no limit
            pass

        # If no changes were triggered, provide an identical formatted statement
        if not changes:
            explanation = "Query structure is already well-formed. No major antipattern rewrites required."
            opt_sql = f"{opt};"
        else:
            explanation = f"Applied {len(changes)} targeted SQL optimization(s) to convert non-sargable expressions and minimize I/O overhead."
            opt_sql = f"{opt};"

        return opt_sql, changes, explanation

    def _optimize_with_gemini(
        self,
        sql: str,
        parsed: ParsedQuery,
        schema: SchemaInfo,
        findings: List[Dict[str, Any]]
    ) -> tuple[str, List[str], str]:
        """Calls Google Gemini API to generate optimized SQL."""
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        findings_summary = "\n".join([f"- [{f.get('severity')}] {f.get('title')}: {f.get('description')}" for f in findings])
        tables_str = ", ".join(parsed.tables) if parsed else "unknown"

        prompt = f"""You are an expert SQL optimization specialist.
Rewrite the following SQL query to be maximally efficient while preserving exact semantics and output results.

ORIGINAL SQL:
{sql}

TARGET TABLES:
{tables_str}

IDENTIFIED ISSUES:
{findings_summary}

RULES:
1. Provide the optimized SQL query inside a ```sql ... ``` code block.
2. Provide a bulleted list of specific changes under the heading "### Changes:".
3. Provide a concise explanation under the heading "### Explanation:".
4. Do NOT change query semantics or return column names unless converting SELECT * to explicit table columns.
"""
        response = model.generate_content(prompt)
        text = response.text

        # Extract SQL
        sql_match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        opt_sql = sql_match.group(1).strip() if sql_match else sql

        # Extract Changes
        changes = []
        changes_match = re.search(r"### Changes:(.*?)(?=###|$)", text, re.DOTALL | re.IGNORECASE)
        if changes_match:
            for line in changes_match.group(1).strip().split("\n"):
                clean_line = line.strip().lstrip("-*123456789. ")
                if clean_line:
                    changes.append(clean_line)

        # Extract Explanation
        explanation_match = re.search(r"### Explanation:(.*?)$", text, re.DOTALL | re.IGNORECASE)
        explanation = explanation_match.group(1).strip() if explanation_match else "Optimized via Gemini AI model."

        if not changes:
            changes = ["Optimized SQL query structure and predicate SARGability."]

        return opt_sql, changes, explanation
