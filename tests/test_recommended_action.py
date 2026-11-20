"""Testes da conduta recomendada (alertar / quarentena reversível / revisão)."""

from expert_system.inference_engine import InferenceResult
from hybrid_system import (
    HybridSystem,
    ACTION_ALERT,
    ACTION_DELIVER,
    ACTION_QUARANTINE,
    ACTION_REVIEW,
)
from ml.classifier import MLPrediction


def _rules(label=None, cf=0.0) -> InferenceResult:
    result = InferenceResult()
    if label:
        result.conclusions[label] = cf
    return result


def _ml(label, confidence) -> MLPrediction:
    return MLPrediction(
        label=label,
        confidence=confidence,
        probabilities={label: confidence},
        top_features=[],
    )


def _decide(classification, confidence, rules, ml):
    return HybridSystem()._decide_action(classification, confidence, rules, ml)


class TestRecommendedAction:
    """A conduta é apoio à decisão: nunca apaga a mensagem."""

    def test_quarantine_when_rules_and_ml_agree_on_phishing(self):
        action, reason = _decide(
            "phishing", 0.97, _rules("phishing", 0.95), _ml("phishing", 0.87)
        )
        assert action == ACTION_QUARANTINE
        assert "reversivel" in reason

    def test_no_quarantine_when_only_rules(self):
        """Sem concordância do ML, phishing vira alerta (não quarentena)."""
        action, _ = _decide("phishing", 0.95, _rules("phishing", 0.95), None)
        assert action == ACTION_ALERT

    def test_no_quarantine_below_threshold(self):
        action, _ = _decide(
            "phishing", 0.75, _rules("phishing", 0.7), _ml("phishing", 0.7)
        )
        assert action == ACTION_ALERT

    def test_manual_review_when_rules_and_ml_disagree(self):
        action, _ = _decide(
            "phishing", 0.76, _rules("phishing", 0.95), _ml("spam", 0.6)
        )
        assert action == ACTION_REVIEW

    def test_manual_review_on_low_confidence(self):
        action, _ = _decide("spam", 0.4, _rules(), _ml("spam", 0.4))
        assert action == ACTION_REVIEW

    def test_manual_review_when_indeterminate(self):
        action, _ = _decide("indeterminado", 0.0, _rules(), None)
        assert action == ACTION_REVIEW

    def test_alert_for_spam(self):
        action, _ = _decide(
            "spam", 0.9, _rules("spam", 0.85), _ml("spam", 0.9)
        )
        assert action == ACTION_ALERT

    def test_alert_for_suspicious(self):
        action, _ = _decide("suspeito", 0.8, _rules(), _ml("suspeito", 0.8))
        assert action == ACTION_ALERT

    def test_deliver_safe_message(self):
        action, _ = _decide(
            "seguro", 0.95, _rules("seguro", 0.9), _ml("seguro", 0.95)
        )
        assert action == ACTION_DELIVER

    def test_never_deletes_automatically(self):
        """Nenhuma conduta possível é exclusão automática."""
        actions = {ACTION_ALERT, ACTION_DELIVER, ACTION_QUARANTINE, ACTION_REVIEW}
        assert not any("apagar" in a or "excluir" in a for a in actions)


class TestActionInReport:
    """A conduta aparece no veredito e no relatório de explicação."""

    def test_verdict_has_action_without_ml(self):
        verdict = HybridSystem().analyze(
            "URGENTE: confirme seus dados em https://bit.ly/x",
            sender="evil@fake.com",
        )
        assert verdict.action == ACTION_ALERT
        assert verdict.action_reason

    def test_explain_shows_recommended_action(self):
        verdict = HybridSystem().analyze(
            "URGENTE: confirme seus dados em https://bit.ly/x",
            sender="evil@fake.com",
        )
        text = verdict.explain()
        assert "CONDUTA RECOMENDADA" in text
        assert "nao garantia" in text
