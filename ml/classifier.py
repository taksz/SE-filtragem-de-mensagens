"""
Classificador de ML — TF-IDF + Regressão Logística.

Escolha do modelo:
- Regressão Logística é interpretável (coeficientes por feature).
- TF-IDF captura padrões de vocabulário típicos de spam/phishing.
- Treinamento em < 1 segundo, sem GPU.
"""

from __future__ import annotations

import csv
import pickle
from pathlib import Path
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


@dataclass
class MLPrediction:
    """Resultado de uma predição do classificador."""

    label: str
    confidence: float
    probabilities: dict[str, float]
    top_features: list[tuple[str, float]]  # (palavra, peso)


class SpamClassifier:
    """Pipeline TF-IDF → Regressão Logística para classificação de mensagens."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            strip_accents="unicode",
            lowercase=True,
        )
        self.model = LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            random_state=42,
        )
        self._is_trained = False

    # ------------------------------------------------------------------
    # Treinamento
    # ------------------------------------------------------------------

    def train(self, dataset_path: str | Path) -> dict:
        """
        Treina o modelo a partir de um CSV com colunas (text, label).

        Retorna métricas de avaliação no conjunto de teste (30%).
        """
        texts, labels = self._load_csv(dataset_path)

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.3, random_state=42, stratify=labels,
        )

        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.model.fit(X_train_vec, y_train)
        self._is_trained = True

        y_pred = self.model.predict(X_test_vec)
        report = classification_report(y_test, y_pred, output_dict=True)
        return report

    # ------------------------------------------------------------------
    # Predição
    # ------------------------------------------------------------------

    def predict(self, text: str) -> MLPrediction:
        """Classifica uma mensagem e retorna predição com explicação."""
        if not self._is_trained:
            raise RuntimeError("Modelo não treinado. Chame train() primeiro.")

        vec = self.vectorizer.transform([text])
        proba = self.model.predict_proba(vec)[0]
        classes = self.model.classes_
        idx = int(np.argmax(proba))

        probabilities = {c: round(float(p), 4) for c, p in zip(classes, proba)}

        # Top features que mais contribuíram para a classe predita
        top_features = self._get_top_features(vec, idx, n=5)

        return MLPrediction(
            label=classes[idx],
            confidence=round(float(proba[idx]), 4),
            probabilities=probabilities,
            top_features=top_features,
        )

    # ------------------------------------------------------------------
    # Explicabilidade do ML
    # ------------------------------------------------------------------

    def _get_top_features(
        self, vec, class_idx: int, n: int = 5
    ) -> list[tuple[str, float]]:
        """Retorna as N features com maior peso para a classe predita."""
        feature_names = self.vectorizer.get_feature_names_out()
        coefs = self.model.coef_[class_idx]

        # Multiplicar coeficientes pelo valor TF-IDF da amostra
        arr = vec.toarray().flatten()
        contributions = arr * coefs
        top_idx = np.argsort(contributions)[-n:][::-1]

        return [
            (feature_names[i], round(float(contributions[i]), 4))
            for i in top_idx
            if contributions[i] > 0
        ]

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def save(self, path: str | Path = "data/model.pkl") -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "model": self.model}, f)

    def load(self, path: str | Path = "data/model.pkl") -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)  # noqa: S301
        self.vectorizer = data["vectorizer"]
        self.model = data["model"]
        self._is_trained = True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_csv(path: str | Path) -> tuple[list[str], list[str]]:
        texts, labels = [], []
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row["text"])
                labels.append(row["label"])
        return texts, labels
