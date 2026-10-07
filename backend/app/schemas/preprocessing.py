from typing import List, Optional

from pydantic import BaseModel


# ============================================================
# DATASET PREPROCESSING ANALYSIS REQUEST
# ============================================================

class DatasetPreprocessRequest(BaseModel):
    filename: str
    target_column: str
    header_row: Optional[int] = None


# ============================================================
# DATASET PREPROCESSING ANALYSIS RESPONSE
# ============================================================

class DatasetPreprocessResponse(BaseModel):
    filename: str
    target_column: str
    problem_type: str
    total_rows: int
    total_columns: int
    feature_count: int
    numerical_features: List[str]
    categorical_features: List[str]
    missing_values: int
    duplicate_rows: int
    target_missing_values: int
    target_unique_values: int
    target_classes: Optional[List[str]] = None
    scaling_required: bool
    encoding_required: bool


# ============================================================
# ACTUAL DATASET PREPROCESSING REQUEST
# ============================================================

class DatasetPreprocessApplyRequest(BaseModel):
    filename: str
    target_column: str
    header_row: Optional[int] = None


# ============================================================
# ACTUAL DATASET PREPROCESSING RESPONSE
# ============================================================

class DatasetPreprocessApplyResponse(BaseModel):
    filename: str
    processed_filename: str
    target_column: str
    problem_type: str

    original_rows: int
    processed_rows: int

    original_feature_count: int
    processed_feature_count: int

    numerical_features: List[str]
    categorical_features: List[str]

    missing_values_before: int
    missing_values_after: int

    duplicate_rows_removed: int
    target_missing_rows_removed: int

    scaling_applied: bool
    encoding_applied: bool

    processed_columns: List[str]

    message: str