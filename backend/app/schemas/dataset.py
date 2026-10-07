from typing import Dict, List, Optional

from pydantic import BaseModel


# ============================================================
# DATASET UPLOAD RESPONSE
# ============================================================

class DatasetUploadResponse(BaseModel):
    """
    Response returned after successfully uploading
    and analyzing a dataset.
    """

    filename: str
    message: str
    rows: int
    columns: int
    column_names: List[str]


# ============================================================
# COLUMN INFORMATION
# ============================================================

class ColumnInformation(BaseModel):
    """
    Information about an individual dataset column.
    """

    name: str
    data_type: str


# ============================================================
# BASIC DATASET PROFILE
# ============================================================

class DatasetBasicProfile(BaseModel):
    """
    Basic structural information about the dataset.
    """

    total_rows: int
    total_columns: int
    column_names: List[str]
    columns: List[ColumnInformation]


# ============================================================
# DATA QUALITY PROFILE
# ============================================================

class DataQualityProfile(BaseModel):
    """
    Basic data quality information.
    """

    missing_values: Dict[str, int]
    total_missing_values: int
    duplicate_rows: int


# ============================================================
# STATISTICAL COLUMN SUMMARY
# ============================================================

class StatisticalColumnSummary(BaseModel):
    """
    Statistical information for one numerical column.
    """

    count: int

    mean: Optional[float]

    standard_deviation: Optional[float]

    minimum: Optional[float]

    percentile_25: Optional[float]

    median: Optional[float]

    percentile_75: Optional[float]

    maximum: Optional[float]


# ============================================================
# COMPLETE DATASET PROFILE RESPONSE
# ============================================================

class DatasetProfileResponse(BaseModel):
    """
    Complete response returned by the dataset profiling API.
    """

    preview: List[Dict[str, object]]

    basic_profile: DatasetBasicProfile

    data_quality: DataQualityProfile

    statistical_summary: Dict[
        str,
        StatisticalColumnSummary
    ]


# ============================================================
# DATASET PREPARATION REQUEST
# ============================================================

class DatasetPrepareRequest(BaseModel):
    """
    Request used to prepare an uploaded dataset
    for machine learning.
    """

    filename: str

    target_column: str

    header_row: Optional[int] = None


# ============================================================
# DATASET PREPARATION RESPONSE
# ============================================================

class DatasetPrepareResponse(BaseModel):
    """
    Response returned after preparing a dataset
    for machine learning.
    """

    filename: str

    target_column: str

    problem_type: str

    total_rows: int

    total_columns: int

    feature_count: int

    feature_columns: List[str]

    target_data_type: str

    target_unique_values: int

    target_classes: List[str]