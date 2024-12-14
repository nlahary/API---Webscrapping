from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MaxFeaturesEnum(str, Enum):
    """Enum for max_features options."""
    auto = "auto"
    sqrt = "sqrt"
    log2 = "log2"


class CriterionEnum(str, Enum):
    """Enum for criterion options."""
    gini = "gini"
    entropy = "entropy"


class Parameters(BaseModel):
    """Document model."""
    n_estimators: Optional[int] = Field(
        description="Number of trees in the forest. Must be between 1 and 1000.",
        ge=1,
        le=1000
    )
    max_depth: Optional[int] = Field(
        description="Maximum depth of the tree. Leave as None for unlimited depth.",
        ge=1
    )
    min_samples_split: Optional[int] = Field(
        description="Minimum number of samples required to split an internal node.",
        ge=2
    )
    min_samples_leaf: Optional[int] = Field(
        description="Minimum number of samples required to be at a leaf node.",
        ge=1
    )
    max_features: Optional[MaxFeaturesEnum] = Field(
        description="The number of features to consider when looking for the best split."
    )
    max_leaf_nodes: Optional[int] = Field(
        description="Maximum number of leaf nodes in the tree. Leave as None for unlimited.",
        ge=1
    )
    criterion: Optional[CriterionEnum] = Field(
        description="The function to measure the quality of a split."
    )

    def to_dict(self) -> dict:
        """Convert to a dictionary. Only include set values."""
        return self.dict(exclude_unset=True)

    class Config:
        schema_extra = {
            "example": {
                "n_estimators": 100,
                "max_depth": 1,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "max_features": "auto",
                "max_leaf_nodes": 10,
                "criterion": "gini"
            }
        }
