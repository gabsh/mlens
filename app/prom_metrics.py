"""
Custom Prometheus business metrics.

Cardinality rule: every label value must come from a finite, known set
(a validated model_name, a label name, an error category) — never raw
user-supplied text. Requests with an unvalidated model_name collapse to
the constant "invalid" label instead of the raw (attacker-controlled) string.
"""
from prometheus_client import Counter, Gauge, Histogram

models_loaded = Gauge(
    "mlens_models_loaded",
    "Number of trained models currently loaded in memory",
)

predictions_total = Counter(
    "mlens_predictions_total",
    "Total predictions served",
    ["model_name", "label"],
)

prediction_errors_total = Counter(
    "mlens_prediction_errors_total",
    "Total prediction errors",
    ["model_name", "error_type"],
)

explain_duration_seconds = Histogram(
    "mlens_explain_duration_seconds",
    "LIME explanation duration in seconds",
    ["model_name"],
)

explain_errors_total = Counter(
    "mlens_explain_errors_total",
    "Total explain errors",
    ["model_name", "error_type"],
)
