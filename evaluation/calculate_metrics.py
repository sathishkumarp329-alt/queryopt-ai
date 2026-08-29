import json
from typing import Dict, Any, List

def calculate_metrics_from_data(results: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate Precision, Recall, F1 Score, False Positive Rate, Optimization Correctness,
    and average latency from evaluation run records.
    """
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_tn = 0
    
    total_opts = 0
    correct_opts = 0
    total_time_ms = 0.0

    cases_map = {tc["id"]: tc for tc in test_cases}

    for res in results:
        tc_id = res["id"]
        tc = cases_map.get(tc_id, {})
        expected_problems = [p.lower() for p in tc.get("expected_problems", [])]
        
        detected_findings = res.get("findings", [])
        detected_titles = [f["title"].lower() for f in detected_findings]

        # Count TP, FP, FN
        matched_expected = set()
        for d in detected_titles:
            is_match = False
            for exp_p in expected_problems:
                if exp_p in d or any(w in d for w in exp_p.split()):
                    is_match = True
                    matched_expected.add(exp_p)
                    break
            if is_match:
                total_tp += 1
            else:
                # If detected an issue on an optimal query or bogus
                total_fp += 1

        for exp_p in expected_problems:
            if exp_p not in matched_expected:
                total_fn += 1

        if not expected_problems and not detected_titles:
            total_tn += 1

        # Optimization correctness
        opt = res.get("optimization", {})
        verif = res.get("verification", {})
        if opt and opt.get("optimized_sql") != opt.get("original_sql"):
            total_opts += 1
            if verif.get("is_equivalent", False) and verif.get("syntax_valid", False):
                correct_opts += 1

        total_time_ms += res.get("exec_time_ms", 0.0)

    precision = round(total_tp / max(1, total_tp + total_fp) * 100.0, 1)
    recall = round(total_tp / max(1, total_tp + total_fn) * 100.0, 1)
    f1 = round((2 * precision * recall) / max(1.0, precision + recall), 1)
    fpr = round(total_fp / max(1, total_fp + total_tn) * 100.0, 1)
    opt_correctness = round(correct_opts / max(1, total_opts) * 100.0, 1) if total_opts > 0 else 100.0
    avg_time = round(total_time_ms / max(1, len(results)), 2)

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": fpr,
        "optimization_correctness": opt_correctness,
        "avg_time_ms": avg_time,
        "total_cases": len(results),
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn
    }
