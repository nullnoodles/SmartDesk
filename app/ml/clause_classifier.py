"""Contract clause classifier using sentence-transformers + logistic regression.

WOW Feature: Upload a contract PDF → extract text → classify each clause
into risk categories using real NLP embeddings.

Categories: ip_transfer, payment_terms, termination, liability, revisions, safe
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import joblib

from app.config import ML_MODELS_DIR, CLAUSE_MODEL_NAME


class ClauseClassifier:
    """Classifies contract clauses into risk categories using embeddings."""

    CATEGORIES = ["ip_transfer", "payment_terms", "termination", "liability", "revisions", "safe"]

    def __init__(self):
        self.model_path = ML_MODELS_DIR / "clause_classifier.pkl"
        self.encoder_path = ML_MODELS_DIR / "clause_encoder.pkl"
        self._embedder = None
        self._classifier: LogisticRegression | None = None
        self._encoder: LabelEncoder | None = None
        self._load_model()

    # ------------------------------------------------------------------
    # Lazy-load the sentence transformer (heavy, ~80MB)
    # ------------------------------------------------------------------

    @property
    def embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(CLAUSE_MODEL_NAME)
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers is not available. "
                    "NLP clause classification requires: pip install sentence-transformers"
                )
        return self._embedder

    @property
    def embedder_available(self) -> bool:
        """Check if sentence-transformers can be imported."""
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    # ------------------------------------------------------------------
    # Model persistence
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        if self.model_path.exists() and self.encoder_path.exists():
            self._classifier = joblib.load(self.model_path)
            self._encoder = joblib.load(self.encoder_path)

    def _save_model(self) -> None:
        joblib.dump(self._classifier, self.model_path)
        joblib.dump(self._encoder, self.encoder_path)

    @property
    def is_trained(self) -> bool:
        return self._classifier is not None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, texts: list[str], labels: list[str]) -> float:
        """
        Train the classifier on labeled clause examples.
        Returns accuracy on training data (for display).
        """
        self._encoder = LabelEncoder()
        y = self._encoder.fit_transform(labels)

        X = self.embedder.encode(texts, show_progress_bar=False)

        self._classifier = LogisticRegression(max_iter=1000, random_state=42)
        self._classifier.fit(X, y)

        accuracy = self._classifier.score(X, y)
        self._save_model()
        return accuracy

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def classify_clause(self, text: str) -> dict[str, Any]:
        """Classify a single clause. Returns category + confidence."""
        if not self.is_trained:
            return {"category": "unknown", "confidence": 0, "text": text}

        if not self.embedder_available:
            return {"category": "unknown", "confidence": 0, "text": text}

        try:
            embedding = self.embedder.encode([text], show_progress_bar=False)
            proba = self._classifier.predict_proba(embedding)[0]
            idx = np.argmax(proba)
            category = self._encoder.inverse_transform([idx])[0]

            return {
                "category": category,
                "confidence": round(float(proba[idx]) * 100, 1),
                "text": text,
            }
        except Exception:
            return {"category": "unknown", "confidence": 0, "text": text}

    def classify_contract(self, full_text: str) -> list[dict[str, Any]]:
        """Split contract into clauses and classify each one."""
        clauses = self._split_into_clauses(full_text)
        return [self.classify_clause(clause) for clause in clauses if clause.strip()]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_into_clauses(text: str) -> list[str]:
        """Split contract text into individual clauses/sentences."""
        # Split on numbered items, bullet points, or sentence boundaries
        parts = re.split(r'(?:\d+[\.\)]\s)|(?:\n\s*[-•]\s)|(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if len(p.strip()) > 20]
