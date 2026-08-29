import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ColumnInfo:
    name: str
    type: str
    notnull: bool
    default: Optional[str]
    is_pk: bool

@dataclass
class IndexInfo:
    name: str
    table: str
    columns: List[str] = field(default_factory=list)
    is_unique: bool = False

@dataclass
class TableInfo:
    name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    indexes: List[IndexInfo] = field(default_factory=list)
    row_count: int = 0

@dataclass
class SchemaInfo:
    tables: Dict[str, TableInfo] = field(default_factory=dict)
    database_path: str = ""

def get_schema(db_path: str, tables_filter: Optional[List[str]] = None) -> SchemaInfo:
    """Extract full schema structure from SQLite database."""
    schema = SchemaInfo(database_path=db_path)

    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        all_tables = [row[0] for row in cursor.fetchall()]

        for tbl in all_tables:
            tbl_lower = tbl.lower()
            if tables_filter and tbl_lower not in [t.lower() for t in tables_filter]:
                continue

            # Row count
            cursor.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            row_count = cursor.fetchone()[0]

            # Columns
            cursor.execute(f"PRAGMA table_info(`{tbl}`)")
            cols_data = cursor.fetchall()
            columns = []
            for col in cols_data:
                # (cid, name, type, notnull, dflt_value, pk)
                columns.append(ColumnInfo(
                    name=col[1],
                    type=col[2] or "TEXT",
                    notnull=bool(col[3]),
                    default=col[4],
                    is_pk=bool(col[5])
                ))

            # Indexes
            cursor.execute(f"PRAGMA index_list(`{tbl}`)")
            idx_list = cursor.fetchall()
            indexes = []
            for idx in idx_list:
                # (seq, name, unique, origin, partial)
                idx_name = idx[1]
                is_unique = bool(idx[2])
                cursor.execute(f"PRAGMA index_info(`{idx_name}`)")
                idx_cols_data = cursor.fetchall()
                idx_cols = [c[2] for c in idx_cols_data]
                indexes.append(IndexInfo(
                    name=idx_name,
                    table=tbl_lower,
                    columns=[c.lower() for c in idx_cols],
                    is_unique=is_unique
                ))

            schema.tables[tbl_lower] = TableInfo(
                name=tbl_lower,
                columns=columns,
                indexes=indexes,
                row_count=row_count
            )

        conn.close()
    except Exception as e:
        print(f"Error fetching schema: {e}")

    return schema

def has_index_on(schema: SchemaInfo, table: str, columns: List[str]) -> bool:
    """Check if an index covering the given columns exists on the table."""
    tbl_lower = table.lower()
    if tbl_lower not in schema.tables:
        return False
    
    req_cols = [c.lower() for c in columns]
    for idx in schema.tables[tbl_lower].indexes:
        # Check if requested column is the leading column of the index
        if idx.columns and idx.columns[0] == req_cols[0]:
            if len(req_cols) == 1:
                return True
            if idx.columns[:len(req_cols)] == req_cols:
                return True
    return False

def get_schema_ddl(db_path: str) -> str:
    """Return all CREATE TABLE statements as a DDL string."""
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'index') AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%'")
        statements = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ";\n\n".join(statements) + ";"
    except Exception as e:
        return f"-- Failed to read DDL: {e}"
