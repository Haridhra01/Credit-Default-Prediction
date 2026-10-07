from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from xgboost import XGBClassifier

from app.ml.feature_selection import select_features


# ============================================================
# FINAL MODEL CONFIGURATION
# ============================================================

RANDOM_STATE = 42

TEST_SIZE = 0.20

FINAL_MODEL_NAME = "xgboost"

TARGET_COLUMN = "default payment next month"


# ============================================================
# CREATE FINAL XGBOOST MODEL
# ============================================================

def create_final_model() -> XGBClassifier:
    """
    Create the final XGBoost classification model.
    """

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        eval_metric="logloss"
    )

    return model


# ============================================================
# TRAIN FINAL MODEL
# ============================================================

def train_final_model(
    dataframe: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
    k: int | str = "all"
) -> Dict[str, Any]:
    """
    Train the final XGBoost model using:

    1. Train/test split
    2. Feature selection
    3. XGBoost training
    4. Model evaluation
    5. Model persistence
    """

    # --------------------------------------------------------
    # Step 1: Validate target column
    # --------------------------------------------------------

    if target_column not in dataframe.columns:

        raise ValueError(
            f"Target column '{target_column}' "
            "was not found in the dataset."
        )

    # --------------------------------------------------------
    # Step 2: Separate features and target
    # --------------------------------------------------------

    X = dataframe.drop(
        columns=[target_column]
    )

    y = dataframe[target_column]

    # --------------------------------------------------------
    # Step 3: Train/test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # --------------------------------------------------------
    # Step 4: Feature selection
    # --------------------------------------------------------

    (
        X_train_selected,
        X_test_selected,
        selected_features,
        feature_scores
    ) = select_features(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        k=k
    )

    # --------------------------------------------------------
    # Step 5: Create final XGBoost model
    # --------------------------------------------------------

    model = create_final_model()

    # --------------------------------------------------------
    # Step 6: Train final model
    # --------------------------------------------------------

    model.fit(
        X_train_selected,
        y_train
    )

    # --------------------------------------------------------
    # Step 7: Generate predictions
    # --------------------------------------------------------

    y_pred = model.predict(
        X_test_selected
    )

    y_probability = model.predict_proba(
        X_test_selected
    )[:, 1]

    # --------------------------------------------------------
    # Step 8: Calculate metrics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Step 9: Create trained-model directory
    # --------------------------------------------------------

    project_root = Path(__file__).resolve().parents[3]

    model_directory = (
        project_root / "trained_models"
    )

    model_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Step 10: Save model and metadata together
    # --------------------------------------------------------

    model_path = (
        model_directory /
        "explainbi_xgboost_model.joblib"
    )

    model_bundle = {
        "model": model,
        "model_name": FINAL_MODEL_NAME,
        "target_column": target_column,
        "selected_features": selected_features,
        "feature_scores": feature_scores,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE
    }

    joblib.dump(
        model_bundle,
        model_path
    )

    # --------------------------------------------------------
    # Step 11: Return training results
    # --------------------------------------------------------

    return {
        "model_name": FINAL_MODEL_NAME,
        "target_column": target_column,
        "original_feature_count": X.shape[1],
        "selected_feature_count": len(selected_features),
        "selected_features": selected_features,
        "training_rows": X_train.shape[0],
        "testing_rows": X_test.shape[0],
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "model_path": str(model_path),
        "feature_scores": feature_scores
    }


# ============================================================
# LOAD SAVED MODEL
# ============================================================

def load_final_model() -> Dict[str, Any]:
    """
    Load the saved ExplainBI XGBoost model bundle.
    """

    project_root = Path(__file__).resolve().parents[3]

    model_path = (
        project_root /
        "trained_models" /
        "explainbi_xgboost_model.joblib"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            "The final ExplainBI model has not been trained yet."
        )

    return joblib.load(
        model_path
    )