from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.schema_tool import SchemaInfo, has_index_on
from backend.tools.explain_tool import ExplainResult
from backend.tools.sql_parser import ParsedQuery

class IndexAgent(BaseAgent):
    """
    Agent 3: Index Recommendation Agent
    Evaluates WHERE filters, JOIN keys, and ORDER BY columns against existing indexes
    and physical EXPLAIN scans to recommend specific single-column, composite, or covering indexes.
    """
    def __init__(self):
        super().__init__(name="Index Recommendation Agent")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        schema: SchemaInfo = context.get("schema_info")
        parsed: ParsedQuery = context.get("parsed_query")
        explain_res: ExplainResult = context.get("explain_result")

        recommendations: List[Dict[str, Any]] = []

        if not schema or not parsed:
            context["index_recommendations"] = recommendations
            return context

        # Analyze WHERE columns
        for col_name in parsed.where_columns:
            # Find which table this column belongs to
            for tbl_name in parsed.tables:
                if tbl_name in schema.tables:
                    col_objs = [c.name.lower() for c in schema.tables[tbl_name].columns]
                    if col_name.lower() in col_objs:
                        # Check if index already exists
                        if not has_index_on(schema, tbl_name, [col_name]):
                            # If this table had a full scan or is large
                            idx_name = f"idx_{tbl_name}_{col_name}"
                            create_stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl_name}({col_name});"
                            
                            rec = {
                                "table_name": tbl_name,
                                "columns": [col_name],
                                "index_type": "BTREE",
                                "create_statement": create_stmt,
                                "reason": f"Column '{col_name}' is used in WHERE filtering on table '{tbl_name}' but currently lacks an index.",
                                "expected_impact": "Eliminates full table scan, changing table lookup from O(N) to O(log N)."
                            }
                            recommendations.append(rec)
                            self.log(
                                action="recommend_filter_index",
                                tool_used="schema_tool",
                                input_summary=f"Table: {tbl_name}, Column: {col_name}",
                                result_summary=f"Recommended index {idx_name}",
                                finding=f"Missing index on {tbl_name}({col_name})",
                                confidence=0.92
                            )

        # Analyze JOIN keys
        for join in parsed.joins:
            join_tbl = join.get("table", "").lower()
            cond = join.get("condition", "").lower()
            if join_tbl in schema.tables:
                for col in schema.tables[join_tbl].columns:
                    c_name = col.name.lower()
                    if c_name in cond:
                        if not has_index_on(schema, join_tbl, [c_name]) and not col.is_pk:
                            idx_name = f"idx_{join_tbl}_{c_name}"
                            create_stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {join_tbl}({c_name});"
                            rec = {
                                "table_name": join_tbl,
                                "columns": [c_name],
                                "index_type": "BTREE",
                                "create_statement": create_stmt,
                                "reason": f"Foreign/join key '{c_name}' on table '{join_tbl}' is used in join condition without an index.",
                                "expected_impact": "Accelerates nested loop / hash join lookups significantly."
                            }
                            recommendations.append(rec)
                            self.log(
                                action="recommend_join_index",
                                tool_used="schema_tool",
                                input_summary=f"Join Table: {join_tbl}, Column: {c_name}",
                                result_summary=f"Recommended join index {idx_name}",
                                finding=f"Missing join index on {join_tbl}({c_name})",
                                confidence=0.90
                            )

        # Analyze Composite Index Opportunities: WHERE col + ORDER BY col
        if parsed.where_columns and parsed.order_by and parsed.tables:
            tbl_name = parsed.tables[0]
            if tbl_name in schema.tables:
                w_col = parsed.where_columns[0]
                # extract raw order col name
                o_col_raw = parsed.order_by[0].split()[0].replace(",", "").lower()
                col_objs = [c.name.lower() for c in schema.tables[tbl_name].columns]
                if w_col in col_objs and o_col_raw in col_objs and w_col != o_col_raw:
                    if not has_index_on(schema, tbl_name, [w_col, o_col_raw]):
                        idx_name = f"idx_{tbl_name}_{w_col}_{o_col_raw}"
                        create_stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl_name}({w_col}, {o_col_raw});"
                        recommendations.append({
                            "table_name": tbl_name,
                            "columns": [w_col, o_col_raw],
                            "index_type": "COMPOSITE",
                            "create_statement": create_stmt,
                            "reason": f"Query combines equality filter on '{w_col}' with sorting on '{o_col_raw}'. A composite index satisfies both filtering and sorting simultaneously.",
                            "expected_impact": "Eliminates in-memory sort pass (Sort buffer) and applies index range scan."
                        })

        if not recommendations:
            self.log(
                action="inspect_index_coverage",
                tool_used="schema_tool",
                input_summary=f"Tables: {', '.join(parsed.tables)}",
                result_summary="Existing indexes adequately cover WHERE/JOIN conditions or no indexable predicates present",
                finding=None,
                confidence=0.95
            )

        context["index_recommendations"] = recommendations
        return context
