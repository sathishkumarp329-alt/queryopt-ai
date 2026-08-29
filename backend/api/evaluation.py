import json
from pathlib import Path
from fastapi import APIRouter
from backend.models.schemas import BaselineVsAgenticComparison, EvaluationMetricsModel
from evaluation.run_evaluation import run_evaluation as execute_eval_pipeline

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

@router.get("")
def get_evaluation_metrics():
    """Retrieve existing baseline vs agentic evaluation benchmark results."""
    metrics_file = ROOT_DIR / "evaluation" / "metrics.json"
    cases_file = ROOT_DIR / "evaluation" / "test_cases" / "cases.json"
    
    if not metrics_file.exists():
        # Run evaluation if not yet generated
        execute_eval_pipeline()

    with open(metrics_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_cases = []
    if cases_file.exists():
        with open(cases_file, "r", encoding="utf-8") as f:
            test_cases = json.load(f)

    data["cases"] = test_cases
    return data

@router.post("/run")
def trigger_evaluation_run():
    """Run full evaluation suite and calculate real metrics across all test cases."""
    metrics = execute_eval_pipeline()
    return {"status": "completed", "metrics": metrics}
