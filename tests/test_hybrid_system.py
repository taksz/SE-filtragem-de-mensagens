"""Testes do Sistema Híbrido (integração completa)."""

import pytest
from pathlib import Path
from ml.dataset import generate_dataset
from hybrid_system import HybridSystem


@pytest.fixture(scope="module")
def system(tmp_path_factory):
    """Sistema híbrido treinado."""
    data_dir = tmp_path_factory.mktemp("data")
    dataset_path = data_dir / "test_dataset.csv"
    generate_dataset(dataset_path, n_samples=400)
    sys = HybridSystem(dataset_path=dataset_path)
    sys.train_ml()
    return sys


class TestHybridSystem:
    """Testes de integração end-to-end."""

    def test_phishing_classification(self, system):
        verdict = system.analyze(
            "URGENTE: Sua conta foi bloqueada. Confirme sua senha em https://bit.ly/x",
            sender="seguranca@bancoo.com",
        )
        assert verdict.classification in ("phishing", "suspeito")
        assert verdict.confidence > 0.5

    def test_spam_classification(self, system):
        verdict = system.analyze(
            "Parabéns! Você foi sorteado! Prêmio GRÁTIS em https://premio.com",
            sender="promo@spam.com",
            recipient_count=50,
        )
        assert verdict.classification == "spam"

    def test_safe_classification(self, system):
        verdict = system.analyze(
            "Oi, tudo bem? Confirmo presença na reunião de amanhã.",
            sender="colega@empresa.com",
            known_senders={"colega@empresa.com"},
        )
        assert verdict.classification == "seguro"

    def test_explain_returns_string(self, system):
        verdict = system.analyze("Teste de explicação")
        explanation = verdict.explain()
        assert isinstance(explanation, str)
        assert "RELATÓRIO" in explanation
        assert "VEREDITO FINAL" in explanation

    def test_facts_are_recorded(self, system):
        verdict = system.analyze(
            "Acesse https://bit.ly/teste urgente",
            sender="x@y.com",
        )
        assert "contem_link" in verdict.facts_extracted
        assert "contem_link_encurtado" in verdict.facts_extracted

    def test_rule_trace_available(self, system):
        verdict = system.analyze(
            "URGENTE: confirme sua senha em https://example.com",
            sender="fake@phishing.com",
        )
        trace = verdict.rule_result.get_trace()
        assert len(trace) > 0

    def test_ml_prediction_available(self, system):
        verdict = system.analyze("Promoção imperdível GRÁTIS!")
        assert verdict.ml_result is not None
        assert verdict.ml_result.label is not None

    def test_without_ml(self):
        """Sistema deve funcionar apenas com regras (ML não treinado)."""
        sys = HybridSystem()
        verdict = sys.analyze(
            "URGENTE: confirme seus dados em https://bit.ly/x",
            sender="evil@fake.com",
        )
        assert verdict.ml_result is None
        assert verdict.classification != "indeterminado"
