from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Query,
    HTTPException
)

from app.schemas.dataset import (
    DatasetUploadResponse,
    DatasetProfileResponse,
    DatasetPrepareRequest,
    DatasetPrepareResponse
)

from app.schemas.preprocessing import (
    DatasetPreprocessRequest,
    DatasetPreprocessResponse,
    DatasetPreprocessApplyRequest,
    DatasetPreprocessApplyResponse
)

from app.services.dataset_service import (
    validate_dataset_file,
    save_dataset,
    read_dataset,
    get_dataset_metadata,
    get_dataset_profile,
    get_uploaded_dataset_path,
    prepare_dataset
)

from app.services.preprocessing_service import (
    analyze_preprocessing,
    apply_preprocessing
)


# ============================================================
# DATASET ROUTER
# ============================================================

router = APIRouter(
    prefix="/datasets",
    tags=["Dataset Management"]
)


# ============================================================
# DATASET UPLOAD
# ============================================================

@router.post(
    "/upload",
    response_model=DatasetUploadResponse
)
def upload_dataset(
    file: UploadFile = File(...)
):
    """
    Upload, validate, save, and analyze a dataset.
    """

    # --------------------------------------------------------
    # Step 1: Validate uploaded file
    # --------------------------------------------------------

    validate_dataset_file(
        file
    )

    # --------------------------------------------------------
    # Step 2: Save uploaded file
    # --------------------------------------------------------

    file_path = save_dataset(
        file
    )

    # --------------------------------------------------------
    # Step 3: Read dataset
    # --------------------------------------------------------

    dataframe = read_dataset(
        file_path
    )

    # --------------------------------------------------------
    # Step 4: Extract dataset metadata
    # --------------------------------------------------------

    metadata = get_dataset_metadata(
        dataframe
    )

    # --------------------------------------------------------
    # Step 5: Return upload information
    # --------------------------------------------------------

    return {

        "filename":
            file.filename,

        "message":
            "Dataset uploaded successfully.",

        "rows":
            metadata["rows"],

        "columns":
            metadata["columns"],

        "column_names":
            metadata["column_names"]
    }


# ============================================================
# DATASET PROFILING
# ============================================================

@router.get(
    "/profile",
    response_model=DatasetProfileResponse
)
def profile_dataset(
    filename: str = Query(
        ...,
        description="Name of the uploaded dataset"
    ),

    header_row: int | None = Query(
        None,
        ge=0,
        description=(
            "Optional zero-based header row. "
            "If omitted, the system automatically "
            "detects the header for Excel files."
        )
    )
):
    """
    Generate a complete profile of an uploaded dataset.

    Includes:
    - Dataset preview
    - Basic dataset profile
    - Data quality analysis
    - Statistical summary
    """

    # --------------------------------------------------------
    # Step 1: Locate uploaded dataset
    # --------------------------------------------------------

    dataset_path = get_uploaded_dataset_path(
        filename
    )

    # --------------------------------------------------------
    # Step 2: Read dataset
    # --------------------------------------------------------

    dataframe = read_dataset(
        dataset_path,
        header_row=header_row
    )

    # --------------------------------------------------------
    # Step 3: Generate complete profile
    # --------------------------------------------------------

    profile = get_dataset_profile(
        dataframe
    )

    # --------------------------------------------------------
    # Step 4: Return profile
    # --------------------------------------------------------

    return profile


# ============================================================
# DATASET PREPARATION
# ============================================================

@router.post(
    "/prepare",
    response_model=DatasetPrepareResponse
)
def prepare_uploaded_dataset(
    request: DatasetPrepareRequest
):
    """
    Prepare an uploaded dataset for machine learning.

    The user provides:
    - Dataset filename
    - Target column
    - Optional header row

    The system:
    - Locates the uploaded dataset
    - Reads the dataset
    - Validates the target column
    - Separates features and target logically
    - Detects classification or regression
    - Returns preparation metadata
    """

    # --------------------------------------------------------
    # Step 1: Locate uploaded dataset
    # --------------------------------------------------------

    dataset_path = get_uploaded_dataset_path(
        request.filename
    )

    # --------------------------------------------------------
    # Step 2: Prepare dataset
    # --------------------------------------------------------

    result = prepare_dataset(
        file_path=dataset_path,
        target_column=request.target_column,
        header_row=request.header_row
    )

    # --------------------------------------------------------
    # Step 3: Return preparation information
    # --------------------------------------------------------

    return result


# ============================================================
# DATASET PREPROCESSING ANALYSIS
# ============================================================

@router.post(
    "/preprocess",
    response_model=DatasetPreprocessResponse
)
def preprocess_uploaded_dataset(
    request: DatasetPreprocessRequest
):
    """
    Analyze preprocessing requirements of
    an uploaded dataset.

    The system:
    - Locates the uploaded dataset
    - Reads the uploaded dataset
    - Validates the target column
    - Detects numerical features
    - Detects categorical features
    - Checks missing values
    - Checks duplicate rows
    - Determines scaling requirement
    - Determines encoding requirement

    This endpoint does NOT modify the dataset.
    """

    # --------------------------------------------------------
    # Step 1: Locate uploaded dataset
    # --------------------------------------------------------

    dataset_path = get_uploaded_dataset_path(
        request.filename
    )

    # --------------------------------------------------------
    # Step 2: Analyze preprocessing requirements
    # --------------------------------------------------------

    result = analyze_preprocessing(
        file_path=dataset_path,
        target_column=request.target_column,
        header_row=request.header_row
    )

    # --------------------------------------------------------
    # Step 3: Return preprocessing information
    # --------------------------------------------------------

    return result


# ============================================================
# APPLY ACTUAL DATASET PREPROCESSING
# ============================================================

@router.post(
    "/preprocess/apply",
    response_model=DatasetPreprocessApplyResponse
)
def apply_dataset_preprocessing(
    request: DatasetPreprocessApplyRequest
):
    """
    Perform actual preprocessing on an uploaded dataset.

    The system:
    - Locates the uploaded dataset
    - Reads the dataset
    - Validates the target column
    - Removes duplicate rows
    - Removes rows with missing target values
    - Handles missing feature values
    - Encodes categorical features when required
    - Scales numerical features when required
    - Keeps the target column unchanged
    - Saves the processed dataset separately

    The original uploaded dataset is never overwritten.
    """

    # --------------------------------------------------------
    # Step 1: Locate uploaded dataset
    # --------------------------------------------------------

    dataset_path = get_uploaded_dataset_path(
        request.filename
    )

    # --------------------------------------------------------
    # Step 2: Apply actual preprocessing
    # --------------------------------------------------------

    result = apply_preprocessing(
        file_path=dataset_path,
        target_column=request.target_column,
        header_row=request.header_row
    )

    # --------------------------------------------------------
    # Step 3: Return preprocessing result
    # --------------------------------------------------------

    return result


# ============================================================
# GET PROCESSED DATASET ROWS
# ============================================================

@router.get(
    "/rows"
)
def get_dataset_rows(
    processed_filename: str = Query(
        ...,
        description="Name of the processed CSV dataset"
    ),

    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of rows to return"
    ),

    offset: int = Query(
        0,
        ge=0,
        description="Number of rows to skip"
    )
):
    """
    Return rows from a processed dataset.

    This endpoint is mainly used by the frontend
    to display and select customers for prediction.

    The dataset is not modified.
    """

    # --------------------------------------------------------
    # Step 1: Locate project root
    # --------------------------------------------------------

    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]

    # --------------------------------------------------------
    # Step 2: Locate processed dataset
    # --------------------------------------------------------

    processed_file = (
        project_root /
        "processed" /
        processed_filename
    )

    if not processed_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Processed dataset not found."
        )

    # --------------------------------------------------------
    # Step 3: Read processed dataset
    # --------------------------------------------------------

    try:
        dataframe = read_dataset(
            processed_file
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read processed dataset: {str(exc)}"
        )

    # --------------------------------------------------------
    # Step 4: Calculate requested range
    # --------------------------------------------------------

    total_rows = len(dataframe)

    if offset >= total_rows and total_rows > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid offset. "
                f"Use a value between 0 and {total_rows - 1}."
            )
        )

    end_index = min(
        offset + limit,
        total_rows
    )

    selected_dataframe = dataframe.iloc[
        offset:end_index
    ].copy()

    # --------------------------------------------------------
    # Step 5: Add row index
    # --------------------------------------------------------

    selected_dataframe.insert(
        0,
        "row_index",
        range(
            offset,
            end_index
        )
    )

    # --------------------------------------------------------
    # Step 6: Convert values to JSON-compatible format
    # --------------------------------------------------------

    selected_dataframe = selected_dataframe.astype(
        object
    ).where(
        selected_dataframe.notna(),
        None
    )

    rows = selected_dataframe.to_dict(
        orient="records"
    )

    # --------------------------------------------------------
    # Step 7: Return dataset rows
    # --------------------------------------------------------

    return {
        "processed_filename": processed_filename,
        "total_rows": total_rows,
        "offset": offset,
        "limit": limit,
        "returned_rows": len(rows),
        "rows": rows
    }