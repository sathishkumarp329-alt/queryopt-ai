import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from backend.orchestrator.orchestrator import AgentOrchestrator
from baseline.baseline_analyzer import BaselineAnalyzer
from evaluation.calculate_metrics import calculate_metrics_from_data

def run_evaluation():
    print("=" * 70)
    print("[*] QueryOpt AI Evaluation Benchmark Suite (20 Test Cases)")
    print("=" * 70)

    cases_file = ROOT_DIR / "evaluation" / "test_cases" / "cases.json"
    with open(cases_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    baseline_analyzer = BaselineAnalyzer()
    orchestrator = AgentOrchestrator()

    baseline_results = []
    agentic_results = []

    print(f"\n[1/2] Running Baseline Analyzer on {len(test_cases)} test cases...")
    for tc in test_cases:
        res = baseline_analyzer.analyze(tc["sql"])
        res["id"] = tc["id"]
        res["name"] = tc["name"]
        baseline_results.append(res)
        print(f"  [+] [{tc['id']}] {tc['name']} -> {len(res.get('findings',[]))} finding(s)")

    print(f"\n[2/2] Running QueryOpt AI (6-Agent Pipeline) on {len(test_cases)} test cases...")
    for tc in test_cases:
        out = orchestrator.run(tc["sql"])
        rep = out["final_report"]
        rep["id"] = tc["id"]
        rep["name"] = tc["name"]
        agentic_results.append(rep)
        print(f"  [+] [{tc['id']}] {tc['name']} -> Score: {rep.get('sql_score')}/100, Status: {rep.get('verification',{}).get('status')}")

    # Save raw outputs
    with open(ROOT_DIR / "evaluation" / "results_baseline.json", "w", encoding="utf-8") as f:
        json.dump(baseline_results, f, indent=2)

    with open(ROOT_DIR / "evaluation" / "results_agentic.json", "w", encoding="utf-8") as f:
        json.dump(agentic_results, f, indent=2)

    # Compute comparative metrics
    base_metrics = calculate_metrics_from_data(baseline_results, test_cases)
    agent_metrics = calculate_metrics_from_data(agentic_results, test_cases)

    print("\n" + "=" * 70)
    print("BASELINE vs QUERYOPT AI COMPARISON RESULTS")
    print("=" * 70)
    print(f"{'Metric':<30} | {'Baseline':<12} | {'QueryOpt AI':<12} | {'Improvement':<12}")
    print("-" * 70)
    print(f"{'Problem Detection Precision':<30} | {base_metrics['precision']:>10.1f}% | {agent_metrics['precision']:>10.1f}% | {agent_metrics['precision'] - base_metrics['precision']:>+10.1f}%")
    print(f"{'Problem Detection Recall':<30} | {base_metrics['recall']:>10.1f}% | {agent_metrics['recall']:>10.1f}% | {agent_metrics['recall'] - base_metrics['recall']:>+10.1f}%")
    print(f"{'F1 Score':<30} | {base_metrics['f1_score']:>10.1f}% | {agent_metrics['f1_score']:>10.1f}% | {agent_metrics['f1_score'] - base_metrics['f1_score']:>+10.1f}%")
    print(f"{'Optimization Correctness':<30} | {base_metrics['optimization_correctness']:>10.1f}% | {agent_metrics['optimization_correctness']:>10.1f}% | {agent_metrics['optimization_correctness'] - base_metrics['optimization_correctness']:>+10.1f}%")
    print(f"{'False Positive Rate':<30} | {base_metrics['false_positive_rate']:>10.1f}% | {agent_metrics['false_positive_rate']:>10.1f}% | {agent_metrics['false_positive_rate'] - base_metrics['false_positive_rate']:>+10.1f}%")
    print(f"{'Avg Query Exec Time':<30} | {base_metrics['avg_time_ms']:>10.2f}ms | {agent_metrics['avg_time_ms']:>10.2f}ms | {base_metrics['avg_time_ms'] - agent_metrics['avg_time_ms']:>+10.2f}ms")
    print("=" * 70 + "\n")

    metrics_summary = {
        "baseline": base_metrics,
        "agentic": agent_metrics,
        "improvement": {
            "precision_delta": round(agent_metrics["precision"] - base_metrics["precision"], 1),
            "recall_delta": round(agent_metrics["recall"] - base_metrics["recall"], 1),
            "f1_delta": round(agent_metrics["f1_score"] - base_metrics["f1_score"], 1),
            "correctness_delta": round(agent_metrics["optimization_correctness"] - base_metrics["optimization_correctness"], 1),
        }
    }
    with open(ROOT_DIR / "evaluation" / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    return metrics_summary

if __name__ == "__main__":
    run_evaluation()
