from pathlib import Path

from fastapi import APIRouter, HTTPException

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from app.ml.model_training import load_final_model


router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


@router.post("")
def make_prediction(
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

        model_bundle = load_final_model()

        model = model_bundle["model"]
        selected_features = model_bundle["selected_features"]

        X = dataframe.drop(
            columns=[target_column, "ID"],
            errors="ignore"
        )

        sample = X.iloc[[row_index]]

        missing_features = [
            feature
            for feature in selected_features
            if feature not in sample.columns
        ]

        if missing_features:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Required model features are missing.",
                    "missing_features": missing_features
                }
            )

        sample = sample[selected_features]

        prediction = model.predict(sample)[0]
        probability = model.predict_proba(sample)[0, 1]

        prediction_label = (
            "Default"
            if int(prediction) == 1
            else "No Default"
        )

        return {
            "row_index": row_index,
            "model": model_bundle["model_name"],
            "prediction": int(prediction),
            "prediction_label": prediction_label,
            "default_probability": float(probability)
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get("/performance")
def get_model_performance(
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

        model_bundle = load_final_model()

        model = model_bundle["model"]
        selected_features = model_bundle["selected_features"]

        X = dataframe.drop(
            columns=[target_column, "ID"],
            errors="ignore"
        )

        y = dataframe[target_column]

        missing_features = [
            feature
            for feature in selected_features
            if feature not in X.columns
        ]

        if missing_features:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Required model features are missing.",
                    "missing_features": missing_features
                }
            )

        X = X[selected_features]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

        y_pred = model.predict(X_test)
        y_probability = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        precision = precision_score(
            y_test,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_test,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            y_pred,
            zero_division=0
        )

        roc_auc = roc_auc_score(
            y_test,
            y_probability
        )

        return {
            "model": model_bundle["model_name"],
            "target_column": target_column,
            "training_rows": len(X_train),
            "testing_rows": len(X_test),
            "original_feature_count": len(
                dataframe.drop(
                    columns=[target_column],
                    errors="ignore"
                ).columns
            ),
            "selected_feature_count": len(selected_features),
            "selected_features": selected_features,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc)
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )