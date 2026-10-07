from typing import List, Tuple

import pandas as pd
from sklearn.feature_selection import (
    SelectKBest,
    mutual_info_classif
)


# ============================================================
# FEATURE SELECTION
# ============================================================

def select_features(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    k: int | str = "all"
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    List[str],
    pd.DataFrame
]:
    """
    Perform feature selection using SelectKBest
    with mutual information.

    Feature selection is fitted only on the training data
    to prevent data leakage.

    Parameters
    ----------
    X_train:
        Training feature dataframe.

    y_train:
        Training target series.

    X_test:
        Testing feature dataframe.

    k:
        Number of features to select.
        "all" keeps all available features.

    Returns
    -------
    selected_X_train:
        Training data containing selected features.

    selected_X_test:
        Testing data containing selected features.

    selected_features:
        Names of selected features.

    feature_scores:
        Feature names and their mutual-information scores.
    """

    # --------------------------------------------------------
    # Step 1: Remove identifier columns
    # --------------------------------------------------------

    identifier_columns = []

    for column in X_train.columns:

        column_name = str(column).strip().lower()

        if column_name in {
            "id",
            "customer_id",
            "customerid",
            "user_id",
            "userid"
        }:
            identifier_columns.append(column)

    if identifier_columns:

        X_train = X_train.drop(
            columns=identifier_columns
        )

        X_test = X_test.drop(
            columns=identifier_columns,
            errors="ignore"
        )

    # --------------------------------------------------------
    # Step 2: Validate feature availability
    # --------------------------------------------------------

    if X_train.shape[1] == 0:

        raise ValueError(
            "No usable features are available "
            "for feature selection."
        )

    # --------------------------------------------------------
    # Step 3: Determine valid k
    # --------------------------------------------------------

    if k != "all":

        k = int(k)

        if k <= 0:

            raise ValueError(
                "The number of selected features "
                "must be greater than zero."
            )

        k = min(
            k,
            X_train.shape[1]
        )

    # --------------------------------------------------------
    # Step 4: Create SelectKBest
    # --------------------------------------------------------

    selector = SelectKBest(
        score_func=mutual_info_classif,
        k=k
    )

    # --------------------------------------------------------
    # Step 5: Fit ONLY on training data
    # --------------------------------------------------------

    selector.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Step 6: Transform training data
    # --------------------------------------------------------

    X_train_selected = selector.transform(
        X_train
    )

    # --------------------------------------------------------
    # Step 7: Transform testing data
    # --------------------------------------------------------

    X_test_selected = selector.transform(
        X_test
    )

    # --------------------------------------------------------
    # Step 8: Get selected feature names
    # --------------------------------------------------------

    selected_features = (
        X_train.columns[
            selector.get_support()
        ]
        .tolist()
    )

    # --------------------------------------------------------
    # Step 9: Get feature scores
    # --------------------------------------------------------

    feature_scores = pd.DataFrame(
        {
            "feature": X_train.columns,
            "score": selector.scores_
        }
    )

    feature_scores = (
        feature_scores
        .sort_values(
            by="score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Step 10: Convert selected data to DataFrames
    # --------------------------------------------------------

    selected_X_train = pd.DataFrame(
        X_train_selected,
        columns=selected_features,
        index=X_train.index
    )

    selected_X_test = pd.DataFrame(
        X_test_selected,
        columns=selected_features,
        index=X_test.index
    )

    return (
        selected_X_train,
        selected_X_test,
        selected_features,
        feature_scores
    )