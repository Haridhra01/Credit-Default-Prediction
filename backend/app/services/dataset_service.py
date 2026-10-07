import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import UploadFile, HTTPException


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SUPPORTED DATASET FORMATS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xls",
    ".xlsx"
}


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_dataset_file(
    file: UploadFile
):
    """
    Validate whether the uploaded file is a supported
    dataset format.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    file_extension = Path(
        file.filename
    ).suffix.lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Only CSV, XLS, and XLSX files are supported."
            )
        )


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(
    file: UploadFile
) -> Path:
    """
    Save the uploaded dataset inside the uploads directory.

    Returns:
        Path: Location of the saved dataset.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    safe_filename = Path(
        file.filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save dataset: {str(error)}"
            )
        )

    return file_path


# ============================================================
# GET UPLOADED DATASET PATH
# ============================================================

def get_uploaded_dataset_path(
    filename: str
) -> Path:
    """
    Get the path of an uploaded dataset safely.
    """

    safe_filename = Path(
        filename
    ).name

    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    return file_path


# ============================================================
# HEADER DETECTION
# ============================================================

def detect_header_row(
    file_path: Path
) -> int:
    """
    Detect the most likely header row for an Excel dataset.

    The first few rows are inspected without assigning
    a header.

    Returns:
        int: Zero-based index of the detected header row.
    """

    try:

        preview = pd.read_excel(
            file_path,
            header=None,
            nrows=10
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unable to inspect Excel header: {str(error)}"
            )
        )

    if preview.empty:

        return 0

    best_row = 0
    best_score = -1

    for row_index in range(
        len(preview)
    ):

        row = preview.iloc[
            row_index
        ]

        non_empty_values = row.dropna()

        if len(non_empty_values) == 0:

            continue

        values = [
            str(value).strip()
            for value in non_empty_values
        ]

        text_values = 0

        for value in values:

            if not value:
                continue

            try:

                float(value)

            except ValueError:

                text_values += 1

        unique_values = len(
            set(values)
        )

        score = (
            (text_values * 3)
            + len(non_empty_values)
            + unique_values
        )

        if score > best_score:

            best_score = score
            best_row = row_index

    return best_row


# ============================================================
# READ DATASET
# ============================================================

def read_dataset(
    file_path: Path,
    header_row: Optional[int] = None
) -> pd.DataFrame:
    """
    Read a dataset based on its file format.

    Supported:
    - CSV
    - XLS
    - XLSX

    Args:
        file_path:
            Path of the dataset.

        header_row:
            Optional zero-based header row.

            If provided, that row is used.

            If omitted:
            - CSV uses the first row.
            - Excel uses automatic header detection.
    """

    try:

        file_extension = file_path.suffix.lower()

        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        if file_extension == ".csv":

            if header_row is not None:

                dataframe = pd.read_csv(
                    file_path,
                    header=header_row
                )

            else:

                dataframe = pd.read_csv(
                    file_path
                )

        # ----------------------------------------------------
        # EXCEL
        # ----------------------------------------------------

        elif file_extension in {
            ".xls",
            ".xlsx"
        }:

            if header_row is not None:

                dataframe = pd.read_excel(
                    file_path,
                    header=header_row
                )

            else:

                detected_header_row = (
                    detect_header_row(
                        file_path
                    )
                )

                dataframe = pd.read_excel(
                    file_path,
                    header=detected_header_row
                )

        # ----------------------------------------------------
        # UNSUPPORTED FORMAT
        # ----------------------------------------------------

        else:

            raise HTTPException(
                status_code=400,
                detail="Unsupported dataset format."
            )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unable to read dataset: {str(error)}"
            )
        )

    return dataframe


# ============================================================
# BASIC DATASET METADATA
# ============================================================

def get_dataset_metadata(
    dataframe: pd.DataFrame
) -> dict:
    """
    Extract basic metadata from the dataset.
    """

    return {

        "rows": int(
            dataframe.shape[0]
        ),

        "columns": int(
            dataframe.shape[1]
        ),

        "column_names": [
            str(column)
            for column in dataframe.columns
        ]
    }


# ============================================================
# DATASET PREVIEW
# ============================================================

def get_dataset_preview(
    dataframe: pd.DataFrame,
    rows: int = 5
) -> list:
    """
    Return the first few rows of the dataset.
    """

    preview_dataframe = dataframe.head(
        rows
    )

    preview_dataframe = (
        preview_dataframe
        .astype(object)
        .where(
            pd.notna(
                preview_dataframe
            ),
            None
        )
    )

    return preview_dataframe.to_dict(
        orient="records"
    )


# ============================================================
# COLUMN INFORMATION
# ============================================================

def get_column_information(
    dataframe: pd.DataFrame
) -> list:
    """
    Get information about every dataset column.
    """

    column_information = []

    for column in dataframe.columns:

        column_information.append(
            {
                "name": str(column),

                "data_type": str(
                    dataframe[column].dtype
                )
            }
        )

    return column_information


# ============================================================
# DATA QUALITY ANALYSIS
# ============================================================

def get_data_quality(
    dataframe: pd.DataFrame
) -> dict:
    """
    Analyze basic data quality.

    Checks:
    - Missing values per column
    - Total missing values
    - Duplicate rows
    """

    missing_values = {}

    for column in dataframe.columns:

        missing_values[
            str(column)
        ] = int(
            dataframe[column].isna().sum()
        )

    total_missing_values = int(
        dataframe.isna()
        .sum()
        .sum()
    )

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    return {

        "missing_values":
            missing_values,

        "total_missing_values":
            total_missing_values,

        "duplicate_rows":
            duplicate_rows
    }


# ============================================================
# SAFE FLOAT CONVERSION
# ============================================================

def _safe_float(
    value
):
    """
    Convert a numerical value into a JSON-compatible
    Python float.

    Returns None for NaN or infinite values.
    """

    if pd.isna(value):

        return None

    return float(value)


# ============================================================
# STATISTICAL SUMMARY
# ============================================================

def get_statistical_summary(
    dataframe: pd.DataFrame
) -> dict:
    """
    Generate statistical information for numerical columns.

    Statistics:
    - Count
    - Mean
    - Standard deviation
    - Minimum
    - 25th percentile
    - Median
    - 75th percentile
    - Maximum
    """

    numerical_dataframe = (
        dataframe.select_dtypes(
            include="number"
        )
    )

    summary = {}

    for column in numerical_dataframe.columns:

        series = numerical_dataframe[
            column
        ]

        summary[
            str(column)
        ] = {

            "count": int(
                series.count()
            ),

            "mean": _safe_float(
                series.mean()
            ),

            "standard_deviation": _safe_float(
                series.std()
            ),

            "minimum": _safe_float(
                series.min()
            ),

            "percentile_25": _safe_float(
                series.quantile(0.25)
            ),

            "median": _safe_float(
                series.median()
            ),

            "percentile_75": _safe_float(
                series.quantile(0.75)
            ),

            "maximum": _safe_float(
                series.max()
            )
        }

    return summary


# ============================================================
# COMPLETE DATASET PROFILE
# ============================================================

def get_dataset_profile(
    dataframe: pd.DataFrame
) -> dict:
    """
    Generate a complete profile of the dataset.

    Includes:
    - Dataset preview
    - Basic profile
    - Data quality analysis
    - Statistical summary
    """

    metadata = get_dataset_metadata(
        dataframe
    )

    return {

        "preview": get_dataset_preview(
            dataframe
        ),

        "basic_profile": {

            "total_rows":
                metadata["rows"],

            "total_columns":
                metadata["columns"],

            "column_names":
                metadata["column_names"],

            "columns":
                get_column_information(
                    dataframe
                )
        },

        "data_quality":
            get_data_quality(
                dataframe
            ),

        "statistical_summary":
            get_statistical_summary(
                dataframe
            )
    }


# ============================================================
# DATASET PREPARATION
# ============================================================

def prepare_dataset(
    file_path: Path,
    target_column: str,
    header_row: Optional[int] = None
) -> dict:
    """
    Prepare an uploaded dataset for machine learning.

    Steps:
    1. Read the dataset.
    2. Validate the target column.
    3. Separate features and target logically.
    4. Detect classification or regression.
    5. Return preparation metadata.

    Note:
        This function does not train an ML model.
        It only prepares and analyzes the dataset structure.
    """

    # --------------------------------------------------------
    # Step 1: Read dataset
    # --------------------------------------------------------

    dataframe = read_dataset(
        file_path,
        header_row=header_row
    )

    # --------------------------------------------------------
    # Step 2: Validate target column
    # --------------------------------------------------------

    if not target_column:
        raise HTTPException(
            status_code=400,
            detail="Target column cannot be empty."
        )

    target_column = target_column.strip()

    if target_column not in dataframe.columns:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Target column '{target_column}' "
                "was not found in the dataset."
            )
        )

    # --------------------------------------------------------
    # Step 3: Get target series
    # --------------------------------------------------------

    target_series = dataframe[
        target_column
    ]

    # --------------------------------------------------------
    # Step 4: Validate target values
    # --------------------------------------------------------

    if target_series.dropna().empty:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Target column '{target_column}' "
                "contains no usable values."
            )
        )

    # --------------------------------------------------------
    # Step 5: Separate feature columns
    # --------------------------------------------------------

    feature_columns = [
        str(column)
        for column in dataframe.columns
        if str(column) != target_column
    ]

    # --------------------------------------------------------
    # Step 6: Determine target information
    # --------------------------------------------------------

    target_data_type = str(
        target_series.dtype
    )

    target_unique_values = int(
        target_series.nunique(
            dropna=True
        )
    )

    # --------------------------------------------------------
    # Step 7: Detect problem type
    # --------------------------------------------------------
    #
    # Classification:
    # - object
    # - category
    # - bool
    # - numeric target with small number of unique values
    #
    # Regression:
    # - continuous numerical target
    # --------------------------------------------------------

    if (
        pd.api.types.is_object_dtype(
            target_series
        )
        or pd.api.types.is_categorical_dtype(
            target_series
        )
        or pd.api.types.is_bool_dtype(
            target_series
        )
    ):

        problem_type = "classification"

    elif target_unique_values <= 10:

        problem_type = "classification"

    else:

        problem_type = "regression"

    # --------------------------------------------------------
    # Step 8: Get target classes
    # --------------------------------------------------------

    if problem_type == "classification":

        unique_targets = (
            target_series
            .dropna()
            .unique()
            .tolist()
        )

        target_classes = [
            str(value)
            for value in unique_targets
        ]

    else:

        target_classes = []

    # --------------------------------------------------------
    # Step 9: Return preparation information
    # --------------------------------------------------------

    return {

        "filename":
            file_path.name,

        "target_column":
            target_column,

        "problem_type":
            problem_type,

        "total_rows":
            int(dataframe.shape[0]),

        "total_columns":
            int(dataframe.shape[1]),

        "feature_count":
            len(feature_columns),

        "feature_columns":
            feature_columns,

        "target_data_type":
            target_data_type,

        "target_unique_values":
            target_unique_values,

        "target_classes":
            target_classes
    }