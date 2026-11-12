"""
Motor de Inferência — encadeamento progressivo (forward chaining).

Itera sobre as regras até que nenhuma nova conclusão possa ser derivada.
Cada disparo é registrado para rastreabilidade completa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from expert_system.knowledge_base import KnowledgeBase, Rule


@dataclass
class RuleFiring:
    """Registro de uma regra disparada."""

    rule_name: str
    rule_description: str
    matched_conditions: frozenset[str]
    conclusion: str
    certainty: float


@dataclass
class InferenceResult:
    """Resultado completo de uma sessão de inferência."""

    conclusions: dict[str, float] = field(default_factory=dict)
    fired_rules: list[RuleFiring] = field(default_factory=list)
    iterations: int = 0

    @property
    def top_conclusion(self) -> tuple[str, float] | None:
        """Retorna (conclusão, certeza) com maior fator de certeza."""
        if not self.conclusions:
            return None
        best = max(self.conclusions, key=self.conclusions.get)  # type: ignore[arg-type]
        return best, self.conclusions[best]

    def get_trace(self) -> list[dict]:
        """Trilha de auditoria legível para cada regra disparada."""
        return [
            {
                "regra": f.rule_name,
                "descricao": f.rule_description,
                "condicoes": sorted(f.matched_conditions),
                "conclusao": f.conclusion,
                "certeza": f.certainty,
            }
            for f in self.fired_rules
        ]


class InferenceEngine:
    """Motor de inferência com encadeamento progressivo."""

    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def infer(self, facts: set[str], *, max_iterations: int = 20) -> InferenceResult:
        """
        Executa encadeamento progressivo (forward chaining).

        1. Para cada regra, verifica se as condições estão nos fatos.
        2. Se sim e a conclusão ainda não existe, dispara a regra,
           adiciona a conclusão aos fatos e registra o disparo.
        3. Repete até estabilizar ou atingir max_iterations.

        Para conclusões atingidas por mais de uma regra, o fator de
        certeza é combinado: CF_combinado = 1 - ∏(1 - CF_i), conforme
        modelo MYCIN simplificado.
        """
        result = InferenceResult()
        working_facts = set(facts)
        fired_names: set[str] = set()

        for iteration in range(1, max_iterations + 1):
            result.iterations = iteration
            new_firing = False

            for rule in self.kb.get_rules():
                if rule.name in fired_names:
                    continue
                if rule.evaluate(working_facts):
                    # Registrar disparo
                    firing = RuleFiring(
                        rule_name=rule.name,
                        rule_description=rule.description,
                        matched_conditions=rule.conditions,
                        conclusion=rule.conclusion,
                        certainty=rule.certainty,
                    )
                    result.fired_rules.append(firing)
                    fired_names.add(rule.name)

                    # Combinar certeza (modelo MYCIN simplificado)
                    if rule.conclusion in result.conclusions:
                        old = result.conclusions[rule.conclusion]
                        combined = old + rule.certainty * (1 - old)
                        result.conclusions[rule.conclusion] = round(combined, 4)
                    else:
                        result.conclusions[rule.conclusion] = rule.certainty

                    # Adicionar conclusão como novo fato
                    working_facts.add(rule.conclusion)
                    new_firing = True

            if not new_firing:
                break

        return result
