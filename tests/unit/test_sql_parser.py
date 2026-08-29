import pytest
from backend.tools.sql_parser import parse_sql, is_destructive, extract_table_aliases

def test_parse_simple_select():
    sql = "SELECT customer_id, first_name FROM customers WHERE city = 'New York';"
    parsed = parse_sql(sql)
    assert parsed.parse_error is None
    assert parsed.query_type == "SELECT"
    assert "customers" in parsed.tables
    assert "customer_id" in parsed.columns
    assert "city" in parsed.where_columns
    assert not parsed.is_select_star

def test_parse_select_star():
    sql = "SELECT * FROM orders;"
    parsed = parse_sql(sql)
    assert parsed.is_select_star
    assert "orders" in parsed.tables

def test_parse_joins():
    sql = "SELECT o.order_id, c.first_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id;"
    parsed = parse_sql(sql)
    assert len(parsed.joins) == 1
    assert parsed.joins[0]["table"] == "customers"
    assert "orders" in parsed.tables

def test_is_destructive():
    assert is_destructive("DROP TABLE customers;")
    assert is_destructive("DELETE FROM orders WHERE order_id = 1;")
    assert is_destructive("TRUNCATE TABLE products;")
    assert is_destructive("ALTER TABLE customers ADD COLUMN age INT;")
    assert is_destructive("UPDATE employees SET salary = 100000;")
    assert not is_destructive("SELECT * FROM customers;")
    assert not is_destructive("EXPLAIN QUERY PLAN SELECT * FROM orders;")

def test_detect_functions_on_columns():
    sql = "SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024';"
    parsed = parse_sql(sql)
    assert len(parsed.has_functions_on_columns) > 0
    assert parsed.has_functions_on_columns[0]["column"] == "order_date"

def test_detect_leading_wildcards():
    sql = "SELECT * FROM customers WHERE email LIKE '%@gmail.com';"
    parsed = parse_sql(sql)
    assert len(parsed.has_leading_wildcard_like) > 0
    assert parsed.has_leading_wildcard_like[0]["column"] == "email"
