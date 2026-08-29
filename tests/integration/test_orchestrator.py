import pytest
from backend.orchestrator.orchestrator import AgentOrchestrator

def test_orchestrator_pipeline_execution():
    orchestrator = AgentOrchestrator()
    sql = "SELECT * FROM orders WHERE customer_id = 25;"
    result = orchestrator.run(sql)

    assert "final_report" in result
    assert "trajectory" in result
    report = result["final_report"]

    assert 0 <= report["sql_score"] <= 100
    assert 0 <= report["performance_score"] <= 100
    assert report["optimization_potential"] in ["HIGH", "MEDIUM", "LOW", "NONE"]
    assert "findings" in report
    assert "optimization" in report
    assert "verification" in report
    
    # Check that all agents logged into trajectory
    agent_names = {t["agent_name"] for t in result["trajectory"]}
    assert "SQL Analysis Agent" in agent_names
    assert "Performance Agent" in agent_names
    assert "Index Recommendation Agent" in agent_names
    assert "Optimization Agent" in agent_names
    assert "Verification Agent" in agent_names
    assert "Final Report Agent" in agent_names
