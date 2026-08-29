import pytest
from backend.tools.sql_parser import parse_sql
from backend.tools.schema_tool import get_schema
from baseline.rule_engine import run_rules
from backend.config import settings

def test_rule_select_star_detected():
    parsed = parse_sql("SELECT * FROM customers;")
    schema = get_schema(settings.DEMO_DB_PATH)
    findings = run_rules(parsed, schema)
    rule_ids = [f.rule_id for f in findings]
    assert "R001" in rule_ids

def test_rule_cartesian_join_detected():
    parsed = parse_sql("SELECT c.first_name, o.order_id FROM customers c, orders o;")
    schema = get_schema(settings.DEMO_DB_PATH)
    findings = run_rules(parsed, schema)
    rule_ids = [f.rule_id for f in findings]
    assert "R009" in rule_ids

def test_rule_leading_wildcard_detected():
    parsed = parse_sql("SELECT customer_id FROM customers WHERE email LIKE '%@gmail.com';")
    schema = get_schema(settings.DEMO_DB_PATH)
    findings = run_rules(parsed, schema)
    rule_ids = [f.rule_id for f in findings]
    assert "R007" in rule_ids
