"""Payment delay predictor — classifies invoices as on-time, late, or very late.

Uses Random Forest trained on user's payment history.
Features: client past behavior, invoice amount, day of month, project type, days to due.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

from app.config import ML_MODELS_DIR, MIN_TRAINING_SAMPLES
from app.data.database import Database


class PaymentPredictor:
    """Predicts whether an invoice will be paid on-time, late, or very late."""

    LABELS = ["on_time", "late", "very_late"]  # 0-7 days, 7-30, 30+

    def __init__(self, db: Database):
        self.db = db
        self.model_path = ML_MODELS_DIR / "payment_predictor.pkl"
        self.type_encoder_path = ML_MODELS_DIR / "payment_type_encoder.pkl"
        self.label_encoder_path = ML_MODELS_DIR / "payment_label_encoder.pkl"
        self._model: RandomForestClassifier | None = None
        self._type_encoder: LabelEncoder | None = None
        self._label_encoder: LabelEncoder | None = None
        self._load_model()

    def _load_model(self) -> None:
        if self.model_path.exists():
            self._model = joblib.load(self.model_path)
            self._type_encoder = joblib.load(self.type_encoder_path)
            if self.label_encoder_path.exists():
                self._label_encoder = joblib.load(self.label_encoder_path)

    def _save_model(self) -> None:
        joblib.dump(self._model, self.model_path)
        joblib.dump(self._type_encoder, self.type_encoder_path)
        joblib.dump(self._label_encoder, self.label_encoder_path)

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def _load_training_data(self) -> pd.DataFrame | None:
        """Load paid invoices with payment timing data."""
        rows = self.db.execute("""
            SELECT i.amount, i.due_date, i.date_issued, i.total,
                   p.type as project_type,
                   pay.payment_date
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            JOIN payments pay ON pay.invoice_id = i.id
            WHERE i.status = 'Paid'
        """)
        if len(rows) < MIN_TRAINING_SAMPLES:
            return None

        data = []
        for row in rows:
            data.append({
                "amount": row["total"],
                "project_type": row["project_type"] or "General",
                "due_date": row["due_date"],
                "date_issued": row["date_issued"],
                "payment_date": row["payment_date"],
            })
        return pd.DataFrame(data)

    def train(self) -> bool:
        """Train on historical payment data. Returns True if successful."""
        df = self._load_training_data()
        if df is None:
            return False

        # Feature engineering
        df["days_to_due"] = (pd.to_datetime(df["due_date"]) - pd.to_datetime(df["date_issued"])).dt.days
        df["delay_days"] = (pd.to_datetime(df["payment_date"]) - pd.to_datetime(df["due_date"])).dt.days

        # Label: on_time (<=0), late (1-30), very_late (30+)
        df["label"] = df["delay_days"].apply(
            lambda d: "on_time" if d <= 0 else ("late" if d <= 30 else "very_late")
        )

        self._type_encoder = LabelEncoder()
        df["type_enc"] = self._type_encoder.fit_transform(df["project_type"])

        X = df[["amount", "days_to_due", "type_enc"]].values
        self._label_encoder = LabelEncoder()
        y = self._label_encoder.fit_transform(df["label"])

        self._model = RandomForestClassifier(n_estimators=50, random_state=42)
        self._model.fit(X, y)
        self._save_model()
        return True

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, amount: float, days_to_due: int, project_type: str) -> dict[str, Any]:
        """Predict payment timing for a new invoice."""
        if not self.is_trained:
            if not self.train():
                return {"prediction": "unknown", "confidence": 0, "message": "Not enough data to predict."}

        try:
            type_enc = self._type_encoder.transform([project_type])[0]
        except (ValueError, AttributeError):
            type_enc = 0

        X = np.array([[amount, days_to_due, type_enc]])
        proba = self._model.predict_proba(X)[0]
        idx = np.argmax(proba)

        # Map model class indices back to label strings via the trained encoder
        if self._label_encoder is not None:
            labels = list(self._label_encoder.classes_)
        else:
            labels = self.LABELS

        return {
            "prediction": labels[idx],
            "confidence": round(float(proba[idx]) * 100, 1),
            "probabilities": {label: round(float(p) * 100, 1) for label, p in zip(labels, proba)},
        }
