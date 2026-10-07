from pathlib import Path

from fastapi import APIRouter, HTTPException

import pandas as pd

from app.xai.shap_explainer import (
    generate_global_explanation,
    generate_local_explanation
)


router = APIRouter(
    prefix="/xai",
    tags=["XAI"]
)


@router.get("/global")
def get_global_explanation(
    processed_filename: str
):
    try:
        project_root = Path(__file__).resolve().parents[3]

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

        dataframe = pd.read_csv(processed_file)

        target_column = "default payment next month"

        if target_column not in dataframe.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Target column '{target_column}' not found."
            )

        X = dataframe.drop(
            columns=[target_column, "ID"],
            errors="ignore"
        )

        result = generate_global_explanation(X)

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get("/local")
def get_local_explanation(
    processed_filename: str,
    row_index: int
):
    try:
        project_root = Path(__file__).resolve().parents[3]

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

        dataframe = pd.read_csv(processed_file)

        target_column = "default payment next month"

        if target_column not in dataframe.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Target column '{target_column}' not found."
            )

        if row_index < 0 or row_index >= len(dataframe):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid row_index. "
                    f"Use a value between 0 and {len(dataframe) - 1}."
                )
            )

        X = dataframe.drop(
            columns=[target_column, "ID"],
            errors="ignore"
        )

        sample = X.iloc[[row_index]]

        result = generate_local_explanation(sample)

        return {
            "row_index": row_index,
            "actual_target": int(
                dataframe.iloc[row_index][target_column]
            ),
            **result
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )