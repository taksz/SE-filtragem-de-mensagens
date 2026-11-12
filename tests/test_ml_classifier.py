"""Testes do Classificador de ML."""

import pytest
from pathlib import Path
from ml.dataset import generate_dataset
from ml.classifier import SpamClassifier


@pytest.fixture(scope="module")
def trained_classifier(tmp_path_factory):
    """Treina o classificador uma vez para todo o módulo de testes."""
    data_dir = tmp_path_factory.mktemp("data")
    dataset_path = data_dir / "test_dataset.csv"
    generate_dataset(dataset_path, n_samples=200, seed=99)

    clf = SpamClassifier()
    clf.train(dataset_path)
    return clf


class TestDatasetGeneration:
    """Testes do gerador de dataset."""

    def test_generates_csv(self, tmp_path):
        path = generate_dataset(tmp_path / "test.csv", n_samples=100)
        assert path.exists()
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 101  # header + 100 samples

    def test_balanced_classes(self, tmp_path):
        path = generate_dataset(tmp_path / "test.csv", n_samples=400)
        import csv
        with open(path) as f:
            reader = csv.DictReader(f)
            labels = [r["label"] for r in reader]
        for cls in ["phishing", "spam", "seguro", "suspeito"]:
            count = labels.count(cls)
            assert count == 100, f"Classe {cls} deveria ter 100, tem {count}"

    def test_reproducible_with_seed(self, tmp_path):
        p1 = generate_dataset(tmp_path / "a.csv", seed=42)
        p2 = generate_dataset(tmp_path / "b.csv", seed=42)
        assert p1.read_text() == p2.read_text()


class TestSpamClassifier:
    """Testes do classificador treinado."""

    def test_predict_phishing(self, trained_classifier):
        pred = trained_classifier.predict(
            "URGENTE: sua conta foi bloqueada, confirme seus dados em https://bit.ly/x"
        )
        assert pred.label in ("phishing", "suspeito")
        assert pred.confidence > 0.3

    def test_predict_spam(self, trained_classifier):
        pred = trained_classifier.predict(
            "Parabéns! Você ganhou um prêmio GRÁTIS! Promoção imperdível!"
        )
        assert pred.label in ("spam", "suspeito")
        assert pred.confidence > 0.3

    def test_predict_safe(self, trained_classifier):
        pred = trained_classifier.predict(
            "Oi, tudo bem? Vamos almoçar amanhã?"
        )
        assert pred.label == "seguro"
        assert pred.confidence > 0.3

    def test_probabilities_sum_to_one(self, trained_classifier):
        pred = trained_classifier.predict("qualquer texto para teste")
        total = sum(pred.probabilities.values())
        assert abs(total - 1.0) < 0.01

    def test_top_features_not_empty_for_spam(self, trained_classifier):
        pred = trained_classifier.predict(
            "GRÁTIS desconto promoção prêmio ganhou cashback"
        )
        assert len(pred.top_features) > 0

    def test_untrained_raises_error(self):
        clf = SpamClassifier()
        with pytest.raises(RuntimeError, match="não treinado"):
            clf.predict("teste")

    def test_save_and_load(self, trained_classifier, tmp_path):
        model_path = tmp_path / "model.pkl"
        trained_classifier.save(model_path)
        assert model_path.exists()

        new_clf = SpamClassifier()
        new_clf.load(model_path)
        pred = new_clf.predict("URGENTE: confirme sua senha agora!")
        assert pred.label is not None


class TestClassifierMetrics:
    """Testes das métricas do modelo."""

    def test_accuracy_above_threshold(self, tmp_path):
        """Acurácia no conjunto de teste deve ser >= 70%."""
        dataset_path = tmp_path / "metrics_test.csv"
        generate_dataset(dataset_path, n_samples=400)
        clf = SpamClassifier()
        report = clf.train(dataset_path)
        assert report["accuracy"] >= 0.70, (
            f"Acurácia {report['accuracy']:.2%} abaixo do mínimo de 70%"
        )
