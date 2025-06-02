import json
import sys

diff = json.load(sys.stdin)


def check_metric(metric_name, path="outputs/metrics/decision_tree_metrics.json"):
    try:
        return diff[path]["data"][metric_name]["diff"]
    except KeyError:
        print(f"Metric {metric_name} not found.")


metrics = ["accuracy", "macro_avg_f1"]

# Fail if any of these regress
for m in metrics:
    diff_value = check_metric(m)
    if diff_value is not None and diff_value < 0:
        print(f"❌ Regression detected in {m}: diff = {diff_value}")
        sys.exit(1)

print("✅ All quality gates passed.")
