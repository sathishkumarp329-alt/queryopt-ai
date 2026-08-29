import time
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.tools.sql_parser import parse_sql
from backend.tools.query_executor import check_result_equivalence, execute_and_time
from backend.tools.explain_tool import run_explain, compare_plans
from backend.tools.schema_tool import SchemaInfo

class VerificationAgent(BaseAgent):
    """
    Agent 5: Verification Agent
    Verifies that the proposed optimized SQL:
    1. Has valid SQL syntax
    2. References valid schema objects
    3. Produces semantically equivalent result sets on sample data
    4. Delivers measurable performance / execution plan improvements
    Rejects or flags any unverified optimizations.
    """
    def __init__(self):
        super().__init__(name="Verification Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        original_sql: str = context.get("sql", "")
        optimized_sql: str = context.get("optimized_sql", "")
        db_path: str = context.get("db_path", "")
        schema: SchemaInfo = context.get("schema_info")
        orig_time_ms: float = context.get("exec_time_ms", 0.0)

        # Default verification struct
        verif = {
            "syntax_valid": True,
            "tables_valid": True,
            "is_equivalent": False,
            "equivalence_explanation": "",
            "original_time_ms": orig_time_ms,
            "optimized_time_ms": 0.0,
            "improvement_pct": 0.0,
            "status": "UNCERTAIN",  # VERIFIED, UNCERTAIN, FAILED
            "confidence": 0.5
        }

        # 1. Syntax Check
        start = time.perf_counter()
        parsed_opt = parse_sql(optimized_sql)
        syntax_valid = (parsed_opt.parse_error is None)
        verif["syntax_valid"] = syntax_valid

        self.log(
            action="verify_syntax",
            tool_used="sqlglot",
            input_summary=optimized_sql[:80],
            result_summary="Syntax valid" if syntax_valid else f"Syntax error: {parsed_opt.parse_error}",
            finding=None if syntax_valid else "Optimized SQL has syntax error",
            confidence=1.0 if syntax_valid else 0.0,
            duration_ms=(time.perf_counter() - start) * 1000.0
        )

        if not syntax_valid:
            verif["status"] = "FAILED"
            verif["confidence"] = 0.0
            verif["equivalence_explanation"] = f"Syntax validation failed: {parsed_opt.parse_error}"
            context["verification_result"] = verif
            return context

        # 2. Schema Object Validation
        if schema:
            for tbl in parsed_opt.tables:
                if tbl not in schema.tables:
                    verif["tables_valid"] = False
                    verif["status"] = "FAILED"
                    verif["confidence"] = 0.0
                    verif["equivalence_explanation"] = f"Referenced table '{tbl}' does not exist in schema."
                    context["verification_result"] = verif
                    return context

        # 3. Equivalence Verification on Sample Execution
        start = time.perf_counter()
        is_equiv, equiv_msg = check_result_equivalence(
            original_sql,
            optimized_sql,
            db_path,
            sample_size=100
        )
        verif["is_equivalent"] = is_equiv
        verif["equivalence_explanation"] = equiv_msg

        self.log(
            action="verify_result_equivalence",
            tool_used="query_executor",
            input_summary="Comparing original vs optimized result rows",
            result_summary=equiv_msg,
            finding="Semantics preserved" if is_equiv else "Semantic divergence detected",
            confidence=0.95 if is_equiv else 0.1,
            duration_ms=(time.perf_counter() - start) * 1000.0
        )

        # 4. Performance Benchmarking on Optimized Query
        _, opt_time_ms = execute_and_time(optimized_sql, db_path, runs=2)
        verif["optimized_time_ms"] = opt_time_ms

        # Calculate improvement %
        if orig_time_ms > 0:
            imp = round(((orig_time_ms - opt_time_ms) / orig_time_ms) * 100.0, 1)
            verif["improvement_pct"] = max(imp, 0.0) if is_equiv else 0.0
        else:
            verif["improvement_pct"] = 0.0

        # 5. EXPLAIN Plan Verification
        opt_explain = run_explain(optimized_sql, db_path)
        orig_explain = context.get("explain_result")
        if orig_explain:
            plan_diff = compare_plans(orig_explain, opt_explain)
            verif["plan_diff"] = plan_diff

        # 6. Final Status Assignment
        if is_equiv and syntax_valid:
            verif["status"] = "VERIFIED"
            verif["confidence"] = 0.95
        elif not is_equiv:
            verif["status"] = "FAILED"
            verif["confidence"] = 0.10
        else:
            verif["status"] = "UNCERTAIN"
            verif["confidence"] = 0.50

        context["verification_result"] = verif
        return context
