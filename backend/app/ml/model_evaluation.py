from typing import Dict, Any

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from xgboost import XGBClassifier


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Dict[str, Any]:
    """
    Train and evaluate a single classification model.
    """

    # --------------------------------------------------------
    # Step 1: Train the model
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Step 2: Generate predictions
    # --------------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Step 3: Generate probabilities
    # --------------------------------------------------------

    y_probability = model.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # Step 4: Calculate evaluation metrics
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
    # Step 5: Return results
    # --------------------------------------------------------

    return {
        "model": model.__class__.__name__,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc
    }


# ============================================================
# CANDIDATE MODELS
# ============================================================

def get_candidate_models():
    """
    Return the candidate classification algorithms
    considered for ExplainBI.
    """

    models = {

        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=42
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced"
        ),

        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss"
        )
    }

    return models


# ============================================================
# EVALUATE ALL CANDIDATES
# ============================================================

def evaluate_candidate_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> pd.DataFrame:
    """
    Evaluate all candidate models using the same
    training and testing data.
    """

    candidate_models = get_candidate_models()

    results = []

    for model_name, model in candidate_models.items():

        print(
            f"Training {model_name}..."
        )

        result = evaluate_model(
            model=model,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test
        )

        result["candidate"] = model_name

        results.append(
            result
        )

    results_dataframe = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Arrange columns
    # --------------------------------------------------------

    results_dataframe = results_dataframe[
        [
            "candidate",
            "model",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc"
        ]
    ]

    return results_dataframe