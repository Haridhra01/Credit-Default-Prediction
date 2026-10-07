from typing import Dict, Any

import pandas as pd
import shap
import xgboost as xgb

from app.ml.model_training import load_final_model


# ============================================================
# LOAD FINAL MODEL
# ============================================================

def get_model_bundle() -> Dict[str, Any]:
    """
    Load the saved ExplainBI model bundle.
    """

    return load_final_model()


# ============================================================
# CREATE SHAP EXPLAINER
# ============================================================

def create_shap_explainer():
    """
    Return the saved model bundle.

    XGBoost 3.2.0 uses a vector-valued base_score format
    that is not handled correctly by SHAP 0.49.1
    TreeExplainer.

    Therefore, ExplainBI uses XGBoost's native
    prediction-contribution mechanism.
    """

    return get_model_bundle()


# ============================================================
# GLOBAL SHAP EXPLANATION
# ============================================================

def generate_global_explanation(
    X: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate global SHAP feature importance.

    Mean absolute SHAP value represents the average
    magnitude of each feature's contribution.
    """

    model_bundle = create_shap_explainer()

    selected_features = model_bundle[
        "selected_features"
    ]

    model = model_bundle[
        "model"
    ]

    # --------------------------------------------------------
    # Keep only features used by the model
    # --------------------------------------------------------

    X_selected = X[
        selected_features
    ].copy()

    # --------------------------------------------------------
    # Convert DataFrame to XGBoost DMatrix
    # --------------------------------------------------------

    data_matrix = xgb.DMatrix(
        X_selected,
        feature_names=selected_features
    )

    # --------------------------------------------------------
    # Generate SHAP values
    # --------------------------------------------------------

    shap_values_with_bias = (
        model.get_booster().predict(
            data_matrix,
            pred_contribs=True
        )
    )

    # Last column contains the bias/base contribution
    shap_values = shap_values_with_bias[
        :, :-1
    ]

    # --------------------------------------------------------
    # Calculate mean absolute SHAP value
    # --------------------------------------------------------

    mean_absolute_shap = (
        pd.DataFrame(
            abs(shap_values),
            columns=selected_features
        )
        .mean()
        .sort_values(
            ascending=False
        )
    )

    # --------------------------------------------------------
    # Convert to response-friendly format
    # --------------------------------------------------------

    feature_importance = []

    for feature, importance in mean_absolute_shap.items():

        feature_importance.append(
            {
                "feature": feature,
                "mean_absolute_shap": float(
                    importance
                )
            }
        )

    return {
        "model": model_bundle["model_name"],
        "feature_count": len(
            selected_features
        ),
        "feature_importance": feature_importance
    }


# ============================================================
# LOCAL SHAP EXPLANATION
# ============================================================

def generate_local_explanation(
    input_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate a SHAP explanation for one prediction.
    """

    model_bundle = create_shap_explainer()

    model = model_bundle[
        "model"
    ]

    selected_features = model_bundle[
        "selected_features"
    ]

    # --------------------------------------------------------
    # Keep only model features
    # --------------------------------------------------------

    X_selected = input_data[
        selected_features
    ].copy()

    # --------------------------------------------------------
    # Generate prediction
    # --------------------------------------------------------

    prediction = model.predict(
        X_selected
    )[0]

    probability = model.predict_proba(
        X_selected
    )[0, 1]

    # --------------------------------------------------------
    # Convert to XGBoost DMatrix
    # --------------------------------------------------------

    data_matrix = xgb.DMatrix(
        X_selected,
        feature_names=selected_features
    )

    # --------------------------------------------------------
    # Generate SHAP values
    # --------------------------------------------------------

    shap_values_with_bias = (
        model.get_booster().predict(
            data_matrix,
            pred_contribs=True
        )
    )

    shap_values = shap_values_with_bias[
        :, :-1
    ]

    row_shap_values = shap_values[0]

    # --------------------------------------------------------
    # Create contribution list
    # --------------------------------------------------------

    contributions = []

    for feature, shap_value, feature_value in zip(
        selected_features,
        row_shap_values,
        X_selected.iloc[0].values
    ):

        contributions.append(
            {
                "feature": feature,
                "value": float(
                    feature_value
                ),
                "shap_value": float(
                    shap_value
                ),
                "direction": (
                    "increases"
                    if shap_value > 0
                    else "decreases"
                )
            }
        )

    # --------------------------------------------------------
    # Sort by absolute contribution
    # --------------------------------------------------------

    contributions.sort(
        key=lambda item: abs(
            item["shap_value"]
        ),
        reverse=True
    )

    return {
        "model": model_bundle["model_name"],
        "prediction": int(
            prediction
        ),
        "default_probability": float(
            probability
        ),
        "contributions": contributions
    }