from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import HTTPException
from sklearn.preprocessing import StandardScaler


# ============================================================
# DETERMINE PROBLEM TYPE
# ============================================================

def determine_problem_type(
    target_series: pd.Series
) -> str:
    """
    Determine whether the target represents
    a classification or regression problem.
    """

    clean_target = target_series.dropna()

    if clean_target.empty:

        raise HTTPException(
            status_code=400,
            detail="Target column contains no usable values."
        )

    unique_values = clean_target.nunique()

    # --------------------------------------------------------
    # Categorical / Boolean target
    # --------------------------------------------------------

    if (
        pd.api.types.is_object_dtype(clean_target)
        or pd.api.types.is_categorical_dtype(clean_target)
        or pd.api.types.is_bool_dtype(clean_target)
    ):

        return "classification"

    # --------------------------------------------------------
    # Numerical target
    # --------------------------------------------------------

    if pd.api.types.is_numeric_dtype(clean_target):

        if unique_values <= 10:

            return "classification"

        return "regression"

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return "classification"


# ============================================================
# ANALYZE PREPROCESSING
# ============================================================

def analyze_preprocessing(
    file_path: Path,
    target_column: str,
    header_row: Optional[int] = None
) -> dict:
    """
    Analyze preprocessing requirements of a dataset.

    This function does NOT modify the dataset.

    It only analyzes:
    - Dataset dimensions
    - Target column
    - Problem type
    - Numerical features
    - Categorical features
    - Missing values
    - Duplicate rows
    - Target information
    - Scaling requirement
    - Encoding requirement
    """

    # --------------------------------------------------------
    # Step 1: Read dataset
    # --------------------------------------------------------

    from app.services.dataset_service import read_dataset

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
    # Step 4: Validate target
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
    # Step 5: Separate feature dataframe
    # --------------------------------------------------------

    feature_dataframe = dataframe.drop(
        columns=[target_column]
    )

    # --------------------------------------------------------
    # Step 6: Detect numerical features
    # --------------------------------------------------------

    numerical_features = [
        str(column)
        for column in feature_dataframe.select_dtypes(
            include="number"
        ).columns
    ]

    # --------------------------------------------------------
    # Step 7: Detect categorical features
    # --------------------------------------------------------

    categorical_features = [
        str(column)
        for column in feature_dataframe.select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        ).columns
    ]

    # --------------------------------------------------------
    # Step 8: Determine problem type
    # --------------------------------------------------------

    problem_type = determine_problem_type(
        target_series
    )

    # --------------------------------------------------------
    # Step 9: Missing values
    # --------------------------------------------------------

    missing_values = int(
        dataframe.isna()
        .sum()
        .sum()
    )

    # --------------------------------------------------------
    # Step 10: Duplicate rows
    # --------------------------------------------------------

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    # --------------------------------------------------------
    # Step 11: Target missing values
    # --------------------------------------------------------

    target_missing_values = int(
        target_series.isna().sum()
    )

    # --------------------------------------------------------
    # Step 12: Target unique values
    # --------------------------------------------------------

    target_unique_values = int(
        target_series.nunique(
            dropna=True
        )
    )

    # --------------------------------------------------------
    # Step 13: Target classes
    # --------------------------------------------------------

    target_classes = None

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

    # --------------------------------------------------------
    # Step 14: Determine scaling requirement
    # --------------------------------------------------------

    scaling_required = (
        len(numerical_features) > 0
    )

    # --------------------------------------------------------
    # Step 15: Determine encoding requirement
    # --------------------------------------------------------

    encoding_required = (
        len(categorical_features) > 0
    )

    # --------------------------------------------------------
    # Step 16: Return preprocessing analysis
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
            int(feature_dataframe.shape[1]),

        "numerical_features":
            numerical_features,

        "categorical_features":
            categorical_features,

        "missing_values":
            missing_values,

        "duplicate_rows":
            duplicate_rows,

        "target_missing_values":
            target_missing_values,

        "target_unique_values":
            target_unique_values,

        "target_classes":
            target_classes,

        "scaling_required":
            scaling_required,

        "encoding_required":
            encoding_required
    }


# ============================================================
# APPLY ACTUAL DATASET PREPROCESSING
# ============================================================

def apply_preprocessing(
    file_path: Path,
    target_column: str,
    header_row: Optional[int] = None
) -> dict:
    """
    Perform actual preprocessing of an uploaded dataset.

    The original uploaded dataset is never overwritten.

    Processing steps:
    1. Read dataset.
    2. Validate target column.
    3. Remove duplicate rows.
    4. Remove rows with missing target values.
    5. Handle missing numerical feature values using median.
    6. Handle missing categorical feature values using mode.
    7. Encode categorical features using one-hot encoding.
    8. Scale numerical features using StandardScaler.
    9. Reattach the target column.
    10. Save the processed dataset as a separate CSV file.
    """

    # --------------------------------------------------------
    # Step 1: Read dataset
    # --------------------------------------------------------

    from app.services.dataset_service import read_dataset

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
    # Step 3: Validate target data
    # --------------------------------------------------------

    target_series = dataframe[
        target_column
    ]

    if target_series.dropna().empty:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Target column '{target_column}' "
                "contains no usable values."
            )
        )

    # --------------------------------------------------------
    # Step 4: Determine problem type
    # --------------------------------------------------------

    problem_type = determine_problem_type(
        target_series
    )

    # --------------------------------------------------------
    # Step 5: Store original dataset information
    # --------------------------------------------------------

    original_rows = int(
        dataframe.shape[0]
    )

    original_feature_dataframe = dataframe.drop(
        columns=[target_column]
    )

    original_feature_count = int(
        original_feature_dataframe.shape[1]
    )

    # --------------------------------------------------------
    # Step 6: Count missing values before processing
    # --------------------------------------------------------

    missing_values_before = int(
        dataframe.isna()
        .sum()
        .sum()
    )

    # --------------------------------------------------------
    # Step 7: Remove duplicate rows
    # --------------------------------------------------------

    duplicate_rows_removed = int(
        dataframe.duplicated().sum()
    )

    dataframe = dataframe.drop_duplicates().copy()

    # --------------------------------------------------------
    # Step 8: Remove rows where target is missing
    # --------------------------------------------------------

    target_missing_rows_removed = int(
        dataframe[target_column].isna().sum()
    )

    dataframe = dataframe.dropna(
        subset=[target_column]
    ).copy()

    # --------------------------------------------------------
    # Step 9: Separate features and target
    # --------------------------------------------------------

    features = dataframe.drop(
        columns=[target_column]
    ).copy()

    target = dataframe[
        target_column
    ].copy()

    # --------------------------------------------------------
    # Step 10: Detect numerical features
    # --------------------------------------------------------

    numerical_features = [
        str(column)
        for column in features.select_dtypes(
            include="number"
        ).columns
    ]

    # --------------------------------------------------------
    # Step 11: Detect categorical features
    # --------------------------------------------------------

    categorical_features = [
        str(column)
        for column in features.select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        ).columns
    ]

    # --------------------------------------------------------
    # Step 12: Handle missing numerical values
    # --------------------------------------------------------

    for column in numerical_features:

        if features[column].isna().any():

            median_value = features[column].median()

            if pd.isna(median_value):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Numerical column '{column}' "
                        "does not contain a usable value "
                        "for median imputation."
                    )
                )

            features[column] = features[column].fillna(
                median_value
            )

    # --------------------------------------------------------
    # Step 13: Handle missing categorical values
    # --------------------------------------------------------

    for column in categorical_features:

        if features[column].isna().any():

            mode_values = features[column].mode(
                dropna=True
            )

            if mode_values.empty:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Categorical column '{column}' "
                        "does not contain a usable value "
                        "for mode imputation."
                    )
                )

            features[column] = features[column].fillna(
                mode_values.iloc[0]
            )

    # --------------------------------------------------------
    # Step 14: Encode categorical features
    # --------------------------------------------------------

    encoding_applied = (
        len(categorical_features) > 0
    )

    if encoding_applied:

        features = pd.get_dummies(
            features,
            columns=categorical_features,
            drop_first=False,
            dtype=int
        )

    # --------------------------------------------------------
    # Step 15: Scale numerical features
    # --------------------------------------------------------

    scaling_applied = (
        len(numerical_features) > 0
    )

    if scaling_applied:

        scaler = StandardScaler()

        features[numerical_features] = (
            scaler.fit_transform(
                features[numerical_features]
            )
        )

    # --------------------------------------------------------
    # Step 16: Reattach target column
    # --------------------------------------------------------

    processed_dataframe = features.copy()

    processed_dataframe[
        target_column
    ] = target.values

    # --------------------------------------------------------
    # Step 17: Check for remaining missing values
    # --------------------------------------------------------

    missing_values_after = int(
        processed_dataframe.isna()
        .sum()
        .sum()
    )

    if missing_values_after > 0:

        raise HTTPException(
            status_code=500,
            detail=(
                "Preprocessing completed but "
                "missing values remain in the "
                "processed dataset."
            )
        )

    # --------------------------------------------------------
    # Step 18: Create processed directory
    # --------------------------------------------------------

    project_root = file_path.parent.parent.parent

    processed_directory = (
        project_root / "processed"
    )

    processed_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Step 19: Create processed filename
    # --------------------------------------------------------

    processed_filename = (
        f"{file_path.stem.replace(' ', '_')}"
        "_processed.csv"
    )

    processed_file_path = (
        processed_directory /
        processed_filename
    )

    # --------------------------------------------------------
    # Step 20: Save processed dataset
    # --------------------------------------------------------

    processed_dataframe.to_csv(
        processed_file_path,
        index=False
    )

    # --------------------------------------------------------
    # Step 21: Return preprocessing information
    # --------------------------------------------------------

    return {

        "filename":
            file_path.name,

        "processed_filename":
            processed_filename,

        "target_column":
            target_column,

        "problem_type":
            problem_type,

        "original_rows":
            original_rows,

        "processed_rows":
            int(
                processed_dataframe.shape[0]
            ),

        "original_feature_count":
            original_feature_count,

        "processed_feature_count":
            int(
                processed_dataframe.shape[1] - 1
            ),

        "numerical_features":
            numerical_features,

        "categorical_features":
            categorical_features,

        "missing_values_before":
            missing_values_before,

        "missing_values_after":
            missing_values_after,

        "duplicate_rows_removed":
            duplicate_rows_removed,

        "target_missing_rows_removed":
            target_missing_rows_removed,

        "scaling_applied":
            scaling_applied,

        "encoding_applied":
            encoding_applied,

        "processed_columns":
            [
                str(column)
                for column in processed_dataframe.columns
            ],

        "message":
            "Dataset preprocessing completed successfully."
    }