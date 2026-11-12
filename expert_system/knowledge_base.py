"""
Base de Conhecimento — regras IF-THEN com fator de certeza (0-1).

Cada regra mapeia um conjunto de fatos (condições) a uma conclusão e
carrega um fator de certeza (CF) que indica a confiança do especialista.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Rule:
    """Regra de produção no formato IF condições THEN conclusão (CF)."""

    name: str
    conditions: frozenset[str]
    conclusion: str
    certainty: float  # 0.0 – 1.0
    description: str = ""

    def evaluate(self, facts: set[str]) -> bool:
        """Retorna True se TODAS as condições estão presentes nos fatos."""
        return self.conditions.issubset(facts)


class KnowledgeBase:
    """Armazena regras e fatos do domínio de filtragem de spam/phishing."""

    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self._load_default_rules()

    # ------------------------------------------------------------------
    # Regras do especialista (3 regras lógicas)
    # ------------------------------------------------------------------

    def _load_default_rules(self) -> None:
        """Carrega as regras padrão do especialista em segurança."""

        # --- Regra 1: Phishing clássico ---
        self.add_rule(Rule(
            name="R1_phishing_classico",
            conditions=frozenset([
                "contem_link",
                "pede_dados_pessoais",
                "tom_urgente",
            ]),
            conclusion="phishing",
            certainty=0.95,
            description=(
                "Mensagem contém link, pede dados pessoais e usa tom de "
                "urgência → forte indicativo de phishing."
            ),
        ))

        # --- Regra 2: Spam promocional ---
        self.add_rule(Rule(
            name="R2_spam_promocional",
            conditions=frozenset([
                "contem_link",
                "oferta_financeira",
                "remetente_desconhecido",
            ]),
            conclusion="spam",
            certainty=0.85,
            description=(
                "Mensagem de remetente desconhecido com link e oferta "
                "financeira → provável spam promocional."
            ),
        ))

        # --- Regra 3: Mensagem segura (contra-exemplo) ---
        self.add_rule(Rule(
            name="R3_mensagem_segura",
            conditions=frozenset([
                "remetente_conhecido",
                "sem_links",
                "sem_anexos",
            ]),
            conclusion="seguro",
            certainty=0.90,
            description=(
                "Remetente conhecido, sem links e sem anexos → mensagem "
                "muito provavelmente segura."
            ),
        ))

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def get_rules(self) -> list[Rule]:
        return list(self.rules)

    def get_rule_by_name(self, name: str) -> Rule | None:
        for r in self.rules:
            if r.name == name:
                return r
        return None
