"""
Sistema Híbrido — combina o Sistema Especialista (simbólico) com o
classificador de ML para uma decisão final mais robusta.

Estratégia de combinação:
1. Motor de inferência processa as regras → conclusão simbólica + CF.
2. Classificador ML prediz a classe → label + confiança.
3. Resultado final: média ponderada (peso configurável) entre os dois.
   Se apenas um módulo retorna resultado, usa-se esse resultado sozinho.
4. Conduta recomendada: a partir do veredito, o sistema sugere uma ação
   (entregar, alertar, quarentena reversível ou revisão manual). O sistema
   nunca apaga mensagens automaticamente: a decisão final é humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from expert_system import KnowledgeBase, FactExtractor, InferenceEngine
from expert_system.inference_engine import InferenceResult
from ml.classifier import SpamClassifier, MLPrediction


# Condutas possíveis (nunca há exclusão automática da mensagem)
ACTION_DELIVER = "entregar"
ACTION_ALERT = "alertar_usuario"
ACTION_QUARANTINE = "alertar_e_quarentena_reversivel"
ACTION_REVIEW = "revisao_manual"

# Confiança mínima para quarentena (regras e ML precisam concordar)
QUARANTINE_THRESHOLD = 0.90
# Abaixo disso o veredito é fraco demais e vai para revisão humana
LOW_CONFIDENCE_THRESHOLD = 0.50

_RISKY_LABELS = ("phishing", "spam", "suspeito")


@dataclass
class HybridVerdict:
    """Veredito final do sistema híbrido com rastreabilidade completa."""

    # Resultado final
    classification: str
    confidence: float

    # Componentes individuais
    rule_result: InferenceResult
    ml_result: MLPrediction | None

    # Metadados de explicação
    facts_extracted: set[str]
    evidence: dict[str, list[str]]

    # Conduta recomendada (apoio à decisão, não decisão final)
    action: str = ACTION_DELIVER
    action_reason: str = ""

    def explain(self) -> str:
        """Gera relatório de explicação legível em português."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  RELATORIO DE ANALISE -- SISTEMA ESPECIALISTA HIBRIDO")
        lines.append("=" * 60)

        # 1. Fatos extraídos
        lines.append("\nFATOS EXTRAIDOS DA MENSAGEM:")
        for fact in sorted(self.facts_extracted):
            evidences = self.evidence.get(fact, [])
            ev_str = f' (evidencia: "{evidences[0]}")' if evidences else ""
            lines.append(f"   - {fact}{ev_str}")

        # 2. Regras disparadas
        lines.append("\nREGRAS DISPARADAS (encadeamento progressivo):")
        if self.rule_result.fired_rules:
            for i, firing in enumerate(self.rule_result.fired_rules, 1):
                lines.append(f"   {i}. [{firing.rule_name}] -> {firing.conclusion} "
                             f"(certeza: {firing.certainty:.0%})")
                lines.append(f"      Motivo: {firing.rule_description}")
        else:
            lines.append("   (nenhuma regra disparada)")

        # 3. Conclusão simbólica
        lines.append("\nCONCLUSAO DO SISTEMA SIMBOLICO:")
        top = self.rule_result.top_conclusion
        if top:
            lines.append(f"   Classificacao: {top[0].upper()} (certeza: {top[1]:.0%})")
        else:
            lines.append("   Nenhuma conclusao derivada pelas regras.")

        # 4. Predição ML
        lines.append("\nPREDICAO DO MODELO DE ML (TF-IDF + Regressao Logistica):")
        if self.ml_result:
            lines.append(f"   Classificacao: {self.ml_result.label.upper()} "
                         f"(confianca: {self.ml_result.confidence:.0%})")
            lines.append("   Probabilidades por classe:")
            for cls, prob in sorted(self.ml_result.probabilities.items(),
                                     key=lambda x: -x[1]):
                bar = "#" * int(prob * 20)
                lines.append(f"     {cls:>10}: {prob:.1%} {bar}")
            if self.ml_result.top_features:
                lines.append("   Palavras-chave que mais influenciaram:")
                for word, weight in self.ml_result.top_features:
                    lines.append(f"     - \"{word}\" (peso: {weight:.4f})")
        else:
            lines.append("   (modelo nao disponivel)")

        # 5. Veredito final
        lines.append("\n" + "=" * 60)
        lines.append(f"   VEREDITO FINAL: {self.classification.upper()} "
                     f"(confianca: {self.confidence:.0%})")
        lines.append("=" * 60)

        # 6. Conduta recomendada
        lines.append(f"\nCONDUTA RECOMENDADA: {self.action}")
        lines.append(f"   Motivo: {self.action_reason}")
        lines.append("   Classificacao automatica e estimativa, nao garantia. "
                     "Nenhuma mensagem e apagada automaticamente.")

        return "\n".join(lines)


class HybridSystem:
    """Combina sistema especialista simbólico + ML."""

    def __init__(
        self,
        *,
        rule_weight: float = 0.6,
        ml_weight: float = 0.4,
        dataset_path: str | Path = "data/dataset.csv",
    ) -> None:
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        self.dataset_path = Path(dataset_path)

        # Componentes
        self.kb = KnowledgeBase()
        self.extractor = FactExtractor()
        self.engine = InferenceEngine(self.kb)
        self.classifier = SpamClassifier()
        self._ml_ready = False

    def train_ml(self) -> dict:
        """Treina o classificador ML e retorna métricas."""
        report = self.classifier.train(self.dataset_path)
        self._ml_ready = True
        return report

    def analyze(
        self,
        text: str,
        *,
        sender: str = "",
        known_senders: set[str] | None = None,
        recipient_count: int = 1,
        attachments: list[str] | None = None,
    ) -> HybridVerdict:
        """Analisa uma mensagem usando os dois subsistemas."""

        # 1. Extrair fatos
        report = self.extractor.extract(
            text,
            sender=sender,
            known_senders=known_senders,
            recipient_count=recipient_count,
            attachments=attachments,
        )

        # 2. Inferência simbólica
        rule_result = self.engine.infer(report.facts)

        # 3. Predição ML (se disponível)
        ml_result = None
        if self._ml_ready:
            ml_result = self.classifier.predict(text)

        # 4. Combinar resultados
        classification, confidence = self._combine(rule_result, ml_result)

        # 5. Conduta recomendada
        action, action_reason = self._decide_action(
            classification, confidence, rule_result, ml_result
        )

        return HybridVerdict(
            classification=classification,
            confidence=confidence,
            rule_result=rule_result,
            ml_result=ml_result,
            facts_extracted=report.facts,
            evidence=report.evidence,
            action=action,
            action_reason=action_reason,
        )

    def _decide_action(
        self,
        classification: str,
        confidence: float,
        rule_result: InferenceResult,
        ml_result: MLPrediction | None,
    ) -> tuple[str, str]:
        """
        Define a conduta recomendada (ação, motivo).

        - Quarentena reversível: só quando regras e ML concordam em
          phishing com alta confiança.
        - Revisão manual: regras e ML discordam, ou confiança baixa.
        - Alerta: mensagem de risco (phishing, spam, suspeito).
        - Entregar: mensagem classificada como segura.
        Nenhuma conduta apaga a mensagem.
        """
        rule_top = rule_result.top_conclusion
        agree = bool(
            rule_top and ml_result and rule_top[0] == ml_result.label
        )
        disagree = bool(
            rule_top and ml_result and rule_top[0] != ml_result.label
        )

        if classification == "indeterminado":
            return ACTION_REVIEW, "Nenhum modulo chegou a uma conclusao."

        if disagree:
            return ACTION_REVIEW, (
                "Regras e modelo de ML discordam; o administrador de "
                "seguranca deve revisar."
            )

        if (
            classification == "phishing"
            and agree
            and confidence >= QUARANTINE_THRESHOLD
        ):
            return ACTION_QUARANTINE, (
                "Regras e ML concordam em phishing com alta confianca; "
                "mensagem retida de forma reversivel (usuario pode "
                "contestar)."
            )

        if confidence < LOW_CONFIDENCE_THRESHOLD:
            return ACTION_REVIEW, "Confianca baixa; requer revisao humana."

        if classification in _RISKY_LABELS:
            return ACTION_ALERT, (
                f"Mensagem classificada como {classification}; o usuario "
                "decide, apos ler o aviso."
            )

        return ACTION_DELIVER, "Mensagem classificada como segura."

    def _combine(
        self, rule_result: InferenceResult, ml_result: MLPrediction | None
    ) -> tuple[str, float]:
        """Combina conclusões dos dois subsistemas."""

        rule_top = rule_result.top_conclusion  # (label, cf) ou None

        # Caso 1: ambos disponíveis
        if rule_top and ml_result:
            rule_label, rule_cf = rule_top
            ml_label = ml_result.label
            ml_cf = ml_result.confidence

            if rule_label == ml_label:
                # Concordam → certeza combinada alta
                combined_cf = min(1.0, rule_cf * self.rule_weight + ml_cf * self.ml_weight + 0.1)
                return rule_label, round(combined_cf, 4)
            else:
                # Discordam → prevalece o de maior certeza ponderada
                rule_score = rule_cf * self.rule_weight
                ml_score = ml_cf * self.ml_weight
                if rule_score >= ml_score:
                    return rule_label, round(rule_cf * 0.8, 4)  # penaliza por discordância
                else:
                    return ml_label, round(ml_cf * 0.8, 4)

        # Caso 2: só regras
        if rule_top:
            return rule_top[0], rule_top[1]

        # Caso 3: só ML
        if ml_result:
            return ml_result.label, ml_result.confidence

        # Caso 4: nenhum
        return "indeterminado", 0.0
