from pydantic import BaseModel, Field
from typing import Optional, Dict


class PerformanceMetrics(BaseModel):
    """
    Performance metrics capturing execution cost and resources.
    """

    runtime_seconds: float = Field(
        ..., description="Execution/runtime duration in seconds"
    )
    peak_ram_mb: Optional[float] = Field(
        None, description="Peak RAM usage in megabytes"
    )
    cpu_usage_pct: Optional[float] = Field(
        None, description="Average CPU usage percentage"
    )


class PrecisionMetrics(BaseModel):
    """
    Accuracy and precision metrics for performance evaluation.
    """

    accuracy: float = Field(..., description="Overall accuracy score (0.0 to 1.0)")
    precision: Optional[float] = Field(None, description="Precision score")
    recall: Optional[float] = Field(None, description="Recall score")
    f1_score: Optional[float] = Field(None, description="F1 score")
    loss: Optional[float] = Field(None, description="Loss metric value")


class ModelBenchmarkResult(BaseModel):
    """
    Result metrics for individual models evaluated in benchmark suites.
    """

    accuracy: float = Field(..., description="Model accuracy")
    time_seconds: float = Field(..., description="Model execution runtime in seconds")


class BenchmarkSuite(BaseModel):
    """
    Aggregated benchmark suite containing SOTA comparison results.
    """

    performance: Optional[PerformanceMetrics] = None
    precision: Optional[PrecisionMetrics] = None
    comparisons: Optional[Dict[str, ModelBenchmarkResult]] = Field(
        None,
        description="Dictionary mapping SOTA models (e.g. ROCKET, DTW) to their benchmark results",
    )
