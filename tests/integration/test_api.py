import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_validate_safe_query():
    response = client.post("/api/query/validate", json={"sql": "SELECT * FROM customers;"})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["is_destructive"] is False

def test_validate_destructive_query():
    response = client.post("/api/query/validate", json={"sql": "DROP TABLE customers;"})
    assert response.status_code == 200
    assert response.json()["is_destructive"] is True
    assert response.json()["valid"] is False

def test_explain_endpoint():
    response = client.post("/api/query/explain", json={"sql": "SELECT * FROM orders WHERE customer_id = 10;"})
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "has_full_table_scan" in data

def test_execute_endpoint():
    response = client.post("/api/query/execute", json={"sql": "SELECT customer_id, first_name FROM customers LIMIT 5;", "max_rows": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["row_count"] == 5
    assert len(data["rows"]) == 5

def test_analyze_full_pipeline():
    response = client.post("/api/analyze", json={
        "sql": "SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024';",
        "database_type": "sqlite",
        "schema_name": "demo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "report" in data
    report = data["report"]
    assert "sql_score" in report
    assert "findings" in report
    assert "trajectory" in report
    assert len(report["trajectory"]) >= 5
