from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from .metadata_schema import ExperimentMetadata
from .benchmark_schema import BenchmarkSuite


class StructuralEmbedding(BaseModel):
    """
    Representation of the 8-dimensional structural embedding calculated for a dynamical system.
    """

    lyapunov_max: float = Field(..., description="Estimated maximum Lyapunov exponent")
    spectral_entropy: float = Field(
        ..., description="Entropy calculated from the power spectrum density"
    )
    dominant_frequency: float = Field(
        ..., description="Dominant frequency in the signal"
    )
    variance: float = Field(..., description="Variance of the dynamical trace")
    autocorr_decay: float = Field(
        ..., description="Time decay rate for the autocorrelation function"
    )
    kurtosis: float = Field(
        ..., description="Kurtosis metric of the signal distribution"
    )
    skewness: float = Field(
        ..., description="Skewness metric of the signal distribution"
    )
    energy: float = Field(..., description="Root-mean-square energy of the signal")


class TelemetryData(BaseModel):
    """
    Telemetry data representing pipeline resource logs and node statuses.
    """

    node_id: Optional[int] = Field(None, description="Database node identifier")
    parent_id: Optional[int] = Field(None, description="Parent node identifier")
    framework_family: str = Field(
        ..., description="Category of execution framework (e.g. NUMERICAL, SYMBOLIC)"
    )
    framework: str = Field(
        ..., description="Specific backend library utilized (e.g. scipy, sympy)"
    )
    status: str = Field(..., description="Execution status: SUCCESS, ERROR, or TIMEOUT")
    cost_metric: float = Field(..., description="Computation cost/runtime in seconds")
    redundancy_flag: int = Field(
        0, description="Flag indicating if the execution is redundant (1) or unique (0)"
    )
    redundant_to_id: Optional[int] = Field(
        None, description="Reference node ID if redundancy is detected"
    )
    semantic_notes: Optional[str] = Field(
        None, max_length=300, description="Contextual semantic metadata"
    )


class ExperimentSession(BaseModel):
    """
    Master contract schema representing an entire execution session,
    grouping metadata, telemetry data, structural embeddings, and benchmark metrics.
    """

    metadata: ExperimentMetadata = Field(..., description="Session metadata")
    telemetry: List[TelemetryData] = Field(
        default_factory=list, description="List of node telemetry logs from execution"
    )
    embeddings: Dict[str, StructuralEmbedding] = Field(
        default_factory=dict,
        description="Map of system names to their structural embeddings",
    )
    benchmarks: Optional[BenchmarkSuite] = Field(
        None, description="Benchmark performance and precision results"
    )
