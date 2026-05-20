from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Union

class ExperimentMetadata(BaseModel):
    """
    Contract for experiment metadata.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: Union[int, str] = Field(..., description="Unique identifier for the experiment session")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of the experiment execution")
    modelo: str = Field(..., description="Name of the model utilized in the experiment")
    version: str = Field(..., alias="versión", description="Version of the pipeline/model used")
    noise_level: float = Field(0.0, alias="noiseLevel", description="Noise level injection")
    seed: Optional[int] = Field(None, description="Random seed used for reproducibility")

