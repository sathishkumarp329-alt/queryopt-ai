import time
from typing import Dict, Any, List
from backend.agents.sql_analysis_agent import SQLAnalysisAgent
from backend.agents.performance_agent import PerformanceAgent
from backend.agents.index_agent import IndexAgent
from backend.agents.optimization_agent import OptimizationAgent
from backend.agents.verification_agent import VerificationAgent
from backend.agents.report_agent import ReportAgent
from backend.tools.schema_tool import get_schema
from backend.config import settings

class AgentOrchestrator:
    """
    Coordinates the multi-agent pipeline:
    SQL Analysis -> Performance -> Index -> Optimization -> Verification -> Final Report
    """
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DEMO_DB_PATH

    def run(self, sql: str, database_type: str = "sqlite", schema_name: str = "demo") -> Dict[str, Any]:
        pipeline_start = time.perf_counter()

        # Instantiate agents fresh for each run
        sql_agent = SQLAnalysisAgent()
        perf_agent = PerformanceAgent()
        index_agent = IndexAgent()
        opt_agent = OptimizationAgent()
        verif_agent = VerificationAgent()
        report_agent = ReportAgent()

        agents = [
            sql_agent,
            perf_agent,
            index_agent,
            opt_agent,
            verif_agent,
            report_agent,
        ]

        # Initial context
        schema_info = get_schema(self.db_path)
        context: Dict[str, Any] = {
            "sql": sql,
            "database_type": database_type,
            "schema_name": schema_name,
            "db_path": self.db_path,
            "schema_info": schema_info,
        }

        # Run pipeline
        for agent in agents:
            try:
                context = agent.run(context)
            except Exception as e:
                print(f"Error in {agent.name}: {e}")
                agent.log(
                    action="error_recovery",
                    result_summary=f"Agent exception: {str(e)}",
                    finding=f"Failure in {agent.name}",
                    confidence=0.0
                )

        # Merge trajectories from all agents
        all_trajectories: List[Dict[str, Any]] = []
        for agent in agents:
            for entry in agent.trajectory:
                all_trajectories.append({
                    "agent_name": entry.agent_name,
                    "action": entry.action,
                    "tool_used": entry.tool_used,
                    "input_summary": entry.input_summary,
                    "result_summary": entry.result_summary,
                    "finding": entry.finding,
                    "confidence": entry.confidence,
                    "duration_ms": entry.duration_ms,
                    "timestamp": entry.timestamp,
                })

        duration_total = round(time.perf_counter() - pipeline_start, 3)

        final_report = context.get("final_report", {})
        final_report["trajectory"] = all_trajectories
        final_report["total_pipeline_duration_seconds"] = duration_total

        return {
            "final_report": final_report,
            "trajectory": all_trajectories,
            "duration_seconds": duration_total,
        }
