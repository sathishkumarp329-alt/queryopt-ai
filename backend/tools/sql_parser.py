import sqlglot
from sqlglot import exp
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ParsedQuery:
    raw_sql: str
    query_type: str = "SELECT"  # SELECT, INSERT, UPDATE, DELETE, etc.
    tables: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)  # selected columns
    joins: List[Dict[str, Any]] = field(default_factory=list)  # [{type, table, condition}]
    where_conditions: List[str] = field(default_factory=list)
    where_columns: List[str] = field(default_factory=list)
    group_by: List[str] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    having: List[str] = field(default_factory=list)
    subqueries: int = 0
    aggregations: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    is_select_star: bool = False
    has_functions_on_columns: List[Dict[str, str]] = field(default_factory=list)  # [{func, column}]
    has_distinct: bool = False
    has_leading_wildcard_like: List[Dict[str, str]] = field(default_factory=list)
    ctes: List[str] = field(default_factory=list)
    parse_error: Optional[str] = None

def is_destructive(sql: str) -> bool:
    """Return True if SQL contains destructive/data modification operations."""
    cleaned = sql.strip().upper()
    destructive_keywords = [
        "DROP ", "DELETE ", "TRUNCATE ", "ALTER ", "UPDATE ", "INSERT ", "REPLACE ",
        "CREATE ", "GRANT ", "REVOKE ", "ATTACH ", "DETACH ", "VACUUM "
    ]
    for kw in destructive_keywords:
        if cleaned.startswith(kw) or f"\n{kw}" in cleaned or f";{kw}" in cleaned or f"; {kw}" in cleaned:
            return True
    
    try:
        parsed_expressions = sqlglot.parse(sql)
        for parsed in parsed_expressions:
            if parsed is None:
                continue
            if not isinstance(parsed, exp.Select):
                if not ("EXPLAIN" in sql.upper()):
                    return True
    except Exception:
        pass
    return False

def parse_sql(sql: str, dialect: str = "sqlite") -> ParsedQuery:
    """Parse SQL string and extract structural AST information."""
    result = ParsedQuery(raw_sql=sql)
    
    if not sql or not sql.strip():
        result.parse_error = "Empty SQL query"
        return result

    try:
        expressions = sqlglot.parse(sql, read=dialect)
        if not expressions or expressions[0] is None:
            result.parse_error = "Could not parse SQL expression"
            return result
        
        parsed = expressions[0]
    except Exception as e:
        result.parse_error = f"Syntax error: {str(e)}"
        return result

    # Determine Query Type
    if isinstance(parsed, exp.Select):
        result.query_type = "SELECT"
    elif isinstance(parsed, exp.Insert):
        result.query_type = "INSERT"
    elif isinstance(parsed, exp.Update):
        result.query_type = "UPDATE"
    elif isinstance(parsed, exp.Delete):
        result.query_type = "DELETE"
    elif hasattr(exp, "Explain") and isinstance(parsed, exp.Explain):
        result.query_type = "EXPLAIN"
    elif "EXPLAIN" in sql.strip().upper()[:10]:
        result.query_type = "EXPLAIN"
    else:
        result.query_type = type(parsed).__name__.upper()

    # Tables
    for table in parsed.find_all(exp.Table):
        t_name = table.name.lower()
        if t_name and t_name not in result.tables:
            result.tables.append(t_name)

    # Columns selected
    if isinstance(parsed, exp.Select):
        if parsed.args.get("distinct"):
            result.has_distinct = True

        for select_expr in parsed.selects:
            if isinstance(select_expr, exp.Star):
                result.is_select_star = True
                result.columns.append("*")
            elif isinstance(select_expr, exp.Column):
                result.columns.append(select_expr.name)
            elif isinstance(select_expr, exp.Alias):
                result.columns.append(select_expr.alias)
            else:
                result.columns.append(select_expr.sql())

    # Joins
    for join in parsed.find_all(exp.Join):
        join_table = join.this.name if hasattr(join.this, "name") else str(join.this)
        join_kind = join.kind if hasattr(join, "kind") and join.kind else "INNER"
        join_on = join.args.get("on")
        cond_sql = join_on.sql() if join_on else "None"
        result.joins.append({
            "type": join_kind.upper(),
            "table": join_table.lower(),
            "condition": cond_sql
        })

    # WHERE conditions and column extractions
    where_node = parsed.args.get("where")
    if where_node:
        result.where_conditions.append(where_node.this.sql())
        for col in where_node.find_all(exp.Column):
            c_name = col.name.lower()
            if c_name not in result.where_columns:
                result.where_columns.append(c_name)

        # Detect functions on columns in WHERE clause (e.g. YEAR(date_col), UPPER(name))
        for func in where_node.find_all(exp.Func):
            func_name = type(func).__name__.upper()
            if hasattr(func, "name") and func.name:
                func_name = func.name.upper()
            for col in func.find_all(exp.Column):
                result.has_functions_on_columns.append({
                    "function": func_name,
                    "column": col.name.lower(),
                    "expression": func.sql()
                })

        # Detect LIKE with leading wildcard: LIKE '%abc' or LIKE '%abc%'
        for like in where_node.find_all(exp.Like):
            right = like.args.get("expression") or like.args.get("this")
            left = like.this
            like_pattern = right.sql() if right else ""
            if like_pattern.startswith("'%") or like_pattern.startswith('"%'):
                result.has_leading_wildcard_like.append({
                    "column": left.sql() if left else "unknown",
                    "pattern": like_pattern
                })

    # GROUP BY
    group = parsed.args.get("group")
    if group:
        for expr in group.expressions:
            result.group_by.append(expr.sql())

    # ORDER BY
    order = parsed.args.get("order")
    if order:
        for ordered in order.expressions:
            result.order_by.append(ordered.sql())

    # HAVING
    having = parsed.args.get("having")
    if having:
        result.having.append(having.sql())

    # LIMIT
    limit = parsed.args.get("limit")
    if limit and hasattr(limit, "expression"):
        try:
            result.limit = int(limit.expression.sql())
        except Exception:
            result.limit = None

    # Subqueries
    subqueries = list(parsed.find_all(exp.Subquery))
    # Exclude the root select if counted
    result.subqueries = len(subqueries)

    # Aggregations
    for agg in parsed.find_all((exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
        agg_name = type(agg).__name__.upper()
        result.aggregations.append(f"{agg_name}({agg.this.sql() if hasattr(agg, 'this') and agg.this else '*'})")

    return result

def extract_table_aliases(sql: str, dialect: str = "sqlite") -> Dict[str, str]:
    """Return map of alias -> real table name."""
    aliases = {}
    try:
        parsed = sqlglot.parse_one(sql, read=dialect)
        for table in parsed.find_all(exp.Table):
            t_name = table.name.lower()
            if table.alias:
                aliases[table.alias.lower()] = t_name
            else:
                aliases[t_name] = t_name
    except Exception:
        pass
    return aliases
