"""
Módulo de Aprendizado de Máquina — classificador TF-IDF + Regressão Logística.

Complementa o sistema simbólico com aprendizado estatístico a partir de dados.
"""

from ml.dataset import generate_dataset
from ml.classifier import SpamClassifier

__all__ = ["generate_dataset", "SpamClassifier"]
