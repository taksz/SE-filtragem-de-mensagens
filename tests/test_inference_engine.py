"""Testes do Motor de Inferência."""

import pytest
from expert_system.knowledge_base import KnowledgeBase, Rule
from expert_system.inference_engine import InferenceEngine


@pytest.fixture
def engine():
    return InferenceEngine(KnowledgeBase())


class TestInferenceEngine:
    """Testes do encadeamento progressivo."""

    def test_phishing_detection(self, engine):
        """Fatos de phishing clássico devem disparar R1."""
        facts = {"contem_link", "pede_dados_pessoais", "tom_urgente"}
        result = engine.infer(facts)
        assert "phishing" in result.conclusions
        assert result.conclusions["phishing"] >= 0.90

    def test_spam_detection(self, engine):
        """Fatos de spam promocional devem disparar R2."""
        facts = {"contem_link", "oferta_financeira", "remetente_desconhecido"}
        result = engine.infer(facts)
        assert "spam" in result.conclusions

    def test_safe_message(self, engine):
        """Remetente conhecido + sem links + sem anexos → seguro."""
        facts = {"remetente_conhecido", "sem_links", "sem_anexos"}
        result = engine.infer(facts)
        assert "seguro" in result.conclusions

    def test_no_rules_fire_on_empty_facts(self, engine):
        result = engine.infer(set())
        assert len(result.fired_rules) == 0
        assert result.top_conclusion is None

    def test_trace_is_recorded(self, engine):
        """Deve registrar trilha de auditoria."""
        facts = {"contem_link", "pede_dados_pessoais", "tom_urgente"}
        result = engine.infer(facts)
        trace = result.get_trace()
        assert len(trace) > 0
        assert "regra" in trace[0]
        assert "conclusao" in trace[0]

    def test_multiple_rules_combine_certainty(self):
        """Se duas regras concluem a mesma coisa, CF deve ser combinado (MYCIN)."""
        kb = KnowledgeBase()
        kb.add_rule(Rule(
            name="extra_phishing",
            conditions=frozenset(["dominio_similar_conhecido", "pede_dados_pessoais"]),
            conclusion="phishing",
            certainty=0.90,
        ))
        engine = InferenceEngine(kb)
        facts = {
            "contem_link", "pede_dados_pessoais", "tom_urgente",  # R1 → phishing
            "dominio_similar_conhecido",  # extra → phishing
        }
        result = engine.infer(facts)
        assert "phishing" in result.conclusions
        # CF combinado deve ser > que qualquer CF individual
        assert result.conclusions["phishing"] > 0.95

    def test_max_iterations_prevents_infinite_loop(self):
        """Motor deve parar mesmo com regras cíclicas (improvável, mas seguro)."""
        kb = KnowledgeBase()
        engine = InferenceEngine(kb)
        result = engine.infer({"contem_link"}, max_iterations=2)
        assert result.iterations <= 2

    def test_custom_rule_fires(self):
        """Regra adicionada pelo usuário deve funcionar."""
        kb = KnowledgeBase()
        kb.add_rule(Rule(
            name="custom_test",
            conditions=frozenset(["fato_x", "fato_y"]),
            conclusion="conclusao_custom",
            certainty=0.8,
        ))
        engine = InferenceEngine(kb)
        result = engine.infer({"fato_x", "fato_y"})
        assert "conclusao_custom" in result.conclusions

    def test_top_conclusion_returns_highest(self, engine):
        """top_conclusion deve retornar a de maior certeza."""
        facts = {
            "contem_link", "pede_dados_pessoais", "tom_urgente",
        }
        result = engine.infer(facts)
        top = result.top_conclusion
        assert top is not None
        label, cf = top
        for other_cf in result.conclusions.values():
            assert cf >= other_cf
