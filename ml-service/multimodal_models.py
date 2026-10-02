import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class MultimodalFusionModel(BaseEstimator, ClassifierMixin):
    """
    Calibrated Multimodal Classifier combining Gradient Boosting and Regularized Linear Models.
    Ensures well-calibrated probabilities for downstream confidence filtering.
    """

    def __init__(self, model_type: str = "hist_gbm", calibrate: bool = True):
        self.model_type = model_type
        self.calibrate = calibrate
        self.pipeline = None

    def _build_base_model(self):
        if self.model_type == "hist_gbm":
            base = HistGradientBoostingClassifier(
                max_iter=300,
                learning_rate=0.03,
                max_leaf_nodes=20,
                min_samples_leaf=20,
                l2_regularization=2.0,
                random_state=42
            )
            return base

        elif self.model_type == "gbm":
            base = GradientBoostingClassifier(
                n_estimators=250,
                learning_rate=0.03,
                max_depth=3,
                min_samples_leaf=15,
                subsample=0.85,
                random_state=42
            )
            return base

        elif self.model_type == "rf":
            base = RandomForestClassifier(
                n_estimators=300,
                max_depth=6,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
            return base

        elif self.model_type == "logistic":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(C=0.1, max_iter=2000, random_state=42))
            ])

        elif self.model_type == "ensemble":
            clf1 = Pipeline([
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(C=0.1, max_iter=1000, random_state=42))
            ])
            clf2 = HistGradientBoostingClassifier(
                max_iter=150,
                learning_rate=0.04,
                max_leaf_nodes=15,
                min_samples_leaf=15,
                l2_regularization=1.5,
                random_state=42
            )
            return VotingClassifier(
                estimators=[("lr", clf1), ("hgb", clf2)],
                voting="soft"
            )

        raise ValueError(f"Unknown model_type: {self.model_type}")

    def fit(self, X, y):
        base_estimator = self._build_base_model()
        if self.calibrate and len(y) >= 60 and len(np.unique(y)) > 1:
            # Calibrate probabilities for sharp confidence thresholds
            try:
                self.pipeline = CalibratedClassifierCV(
                    estimator=base_estimator,
                    method="sigmoid",
                    cv=2
                )
                self.pipeline.fit(X, y)
                self.classes_ = self.pipeline.classes_
                return self
            except Exception:
                pass

        self.pipeline = base_estimator
        self.pipeline.fit(X, y)
        self.classes_ = getattr(self.pipeline, "classes_", np.unique(y))
        return self

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)


class RegimeAwareMixtureModel(BaseEstimator, ClassifierMixin):
    """
    Regime-switching expert model:
    Maintains specialized sub-models for distinct market regimes:
    - Bull Market Expert
    - Bear / High-Volatility Expert
    - Sideways / Transition Expert
    """

    def __init__(self, regime_feature_idx: int = 0):
        self.regime_feature_idx = regime_feature_idx
        self.bull_model = MultimodalFusionModel(model_type="hist_gbm", calibrate=True)
        self.bear_model = MultimodalFusionModel(model_type="hist_gbm", calibrate=True)
        self.global_model = MultimodalFusionModel(model_type="ensemble", calibrate=True)

    def fit(self, X, y, regime_labels: np.ndarray = None):
        if regime_labels is None:
            # Extract from feature if provided
            regime_labels = X[:, self.regime_feature_idx]

        self.global_model.fit(X, y)
        self.classes_ = self.global_model.classes_

        bull_mask = regime_labels == 1
        bear_mask = regime_labels == -1

        if np.sum(bull_mask) >= 60 and len(np.unique(y[bull_mask])) == len(self.classes_):
            self.bull_model.fit(X[bull_mask], y[bull_mask])
        else:
            self.bull_model = self.global_model

        if np.sum(bear_mask) >= 60 and len(np.unique(y[bear_mask])) == len(self.classes_):
            self.bear_model.fit(X[bear_mask], y[bear_mask])
        else:
            self.bear_model = self.global_model

        return self

    def predict_proba(self, X, regime_labels: np.ndarray = None):
        if regime_labels is None:
            regime_labels = X[:, self.regime_feature_idx]

        n = len(X)
        n_classes = len(self.classes_)
        probs = np.zeros((n, n_classes), dtype=np.float64)

        bull_mask = regime_labels == 1
        bear_mask = regime_labels == -1
        other_mask = ~(bull_mask | bear_mask)

        if np.any(bull_mask):
            probs[bull_mask] = self.bull_model.predict_proba(X[bull_mask])
        if np.any(bear_mask):
            probs[bear_mask] = self.bear_model.predict_proba(X[bear_mask])
        if np.any(other_mask):
            probs[other_mask] = self.global_model.predict_proba(X[other_mask])

        return probs

    def predict(self, X, regime_labels: np.ndarray = None):
        probs = self.predict_proba(X, regime_labels)
        return self.classes_[np.argmax(probs, axis=1)]
