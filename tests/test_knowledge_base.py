"""Testes da Base de Conhecimento."""

import pytest
from expert_system.knowledge_base import KnowledgeBase, Rule


class TestRule:
    """Testes da classe Rule."""

    def test_evaluate_all_conditions_met(self):
        rule = Rule(
            name="test",
            conditions=frozenset(["a", "b"]),
            conclusion="c",
            certainty=0.9,
        )
        assert rule.evaluate({"a", "b", "x"}) is True

    def test_evaluate_missing_condition(self):
        rule = Rule(
            name="test",
            conditions=frozenset(["a", "b"]),
            conclusion="c",
            certainty=0.9,
        )
        assert rule.evaluate({"a", "x"}) is False

    def test_evaluate_empty_facts(self):
        rule = Rule(
            name="test",
            conditions=frozenset(["a"]),
            conclusion="c",
            certainty=0.9,
        )
        assert rule.evaluate(set()) is False


class TestKnowledgeBase:
    """Testes da Base de Conhecimento."""

    def test_default_rules_loaded(self):
        kb = KnowledgeBase()
        assert len(kb.get_rules()) >= 3, "Deve ter no mínimo 3 regras"

    def test_rule_names_unique(self):
        kb = KnowledgeBase()
        names = [r.name for r in kb.get_rules()]
        assert len(names) == len(set(names)), "Nomes de regras devem ser únicos"

    def test_add_custom_rule(self):
        kb = KnowledgeBase()
        n_before = len(kb.get_rules())
        kb.add_rule(Rule(
            name="custom",
            conditions=frozenset(["x"]),
            conclusion="y",
            certainty=0.5,
        ))
        assert len(kb.get_rules()) == n_before + 1

    def test_get_rule_by_name(self):
        kb = KnowledgeBase()
        rule = kb.get_rule_by_name("R1_phishing_classico")
        assert rule is not None
        assert rule.conclusion == "phishing"

    def test_get_rule_by_name_not_found(self):
        kb = KnowledgeBase()
        assert kb.get_rule_by_name("inexistente") is None

    def test_certainty_range(self):
        kb = KnowledgeBase()
        for rule in kb.get_rules():
            assert 0.0 <= rule.certainty <= 1.0, (
                f"Certeza de {rule.name} fora do intervalo [0, 1]"
            )

    def test_phishing_rule_conditions(self):
        """Regra de phishing clássico exige link + dados + urgência."""
        kb = KnowledgeBase()
        r = kb.get_rule_by_name("R1_phishing_classico")
        assert r is not None
        assert "contem_link" in r.conditions
        assert "pede_dados_pessoais" in r.conditions
        assert "tom_urgente" in r.conditions
