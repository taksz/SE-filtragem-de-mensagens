"""
Extrator de Fatos — analisa o texto bruto de uma mensagem e devolve
o conjunto de fatos simbólicos que alimentam o motor de inferência.

Cada método ``_check_*`` é um micro-detector baseado em heurísticas
simples (regex, listas de palavras-chave). Em produção, esses
detectores poderiam ser substituídos por modelos de NLP mais robustos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Listas de palavras-chave (português + inglês misturado, como é comum em
# golpes brasileiros)
# ---------------------------------------------------------------------------

_PALAVRAS_URGENCIA = [
    "urgente", "imediato", "imediatamente", "agora mesmo", "última chance",
    "expira hoje", "prazo final", "não perca", "atenção", "cuidado",
    "bloqueado", "suspensa", "cancelamento", "sua conta será",
    "urgent", "immediately", "act now", "deadline",
]

_PALAVRAS_DADOS_PESSOAIS = [
    "senha", "cpf", "cartão", "número do cartão", "dados bancários",
    "código de segurança", "cvv", "token", "confirme seus dados",
    "atualize seu cadastro", "password", "credit card", "social security",
    "informe seus dados", "confirmar identidade",
]

_PALAVRAS_OFERTA = [
    "grátis", "gratuito", "promoção", "desconto", "prêmio", "sorteado",
    "ganhou", "parabéns", "cashback", "pix", "free", "winner", "prize",
    "oferta imperdível", "lucre", "rendimento garantido", "ganhe dinheiro",
    "renda extra", "investimento", "bitcoin",
]

_PALAVRAS_EMOCIONAL = [
    "por favor me ajude", "estou precisando", "é vida ou morte",
    "pelo amor de deus", "socorro", "desesperado", "implorando",
    "help me", "please help", "chorando", "não sei o que fazer",
]

_DOMINIOS_ENCURTADOS = [
    "bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "rebrand.ly", "shorturl.at", "cutt.ly",
]

_DOMINIOS_CONHECIDOS = [
    "banco", "bradesco", "itau", "nubank", "caixa", "bb.com",
    "santander", "mercadolivre", "amazon", "paypal", "netflix",
    "gov.br", "receita", "correios", "sedex",
]

_EXTENSOES_EXECUTAVEIS = [
    ".exe", ".bat", ".cmd", ".scr", ".msi", ".vbs", ".js",
    ".ps1", ".jar", ".apk", ".dmg",
]


@dataclass
class ExtractionReport:
    """Resultado da extração: fatos e evidências textuais."""

    facts: set[str] = field(default_factory=set)
    evidence: dict[str, list[str]] = field(default_factory=dict)

    def add(self, fact: str, snippet: str = "") -> None:
        self.facts.add(fact)
        self.evidence.setdefault(fact, [])
        if snippet:
            self.evidence[fact].append(snippet)


class FactExtractor:
    """Extrai fatos simbólicos de uma mensagem de texto."""

    def extract(
        self,
        text: str,
        *,
        sender: str = "",
        known_senders: set[str] | None = None,
        recipient_count: int = 1,
        attachments: list[str] | None = None,
    ) -> ExtractionReport:
        """
        Parâmetros
        ----------
        text : corpo da mensagem.
        sender : endereço do remetente.
        known_senders : conjunto de remetentes confiáveis (whitelist).
        recipient_count : quantidade de destinatários.
        attachments : nomes de arquivos anexados.
        """
        known_senders = known_senders or set()
        attachments = attachments or []
        report = ExtractionReport()
        lower = text.lower()

        self._check_links(lower, report)
        self._check_urgencia(lower, report)
        self._check_dados_pessoais(lower, report)
        self._check_oferta(lower, report)
        self._check_emocional(lower, report)
        self._check_remetente(sender, known_senders, report)
        self._check_dominio_similar(sender, report)
        self._check_destinatarios(recipient_count, report)
        self._check_anexos(attachments, report)
        self._check_sem_links(lower, report)
        self._check_sem_anexos(attachments, report)

        return report

    # ------------------------------------------------------------------
    # Detectores individuais
    # ------------------------------------------------------------------

    @staticmethod
    def _check_links(text: str, report: ExtractionReport) -> None:
        urls = re.findall(r"https?://\S+", text)
        if urls:
            report.add("contem_link", urls[0])
            for url in urls:
                for enc in _DOMINIOS_ENCURTADOS:
                    if enc in url:
                        report.add("contem_link_encurtado", url)
                        return

    @staticmethod
    def _check_urgencia(text: str, report: ExtractionReport) -> None:
        for p in _PALAVRAS_URGENCIA:
            if p in text:
                report.add("tom_urgente", p)
                return

    @staticmethod
    def _check_dados_pessoais(text: str, report: ExtractionReport) -> None:
        for p in _PALAVRAS_DADOS_PESSOAIS:
            if p in text:
                report.add("pede_dados_pessoais", p)
                return

    @staticmethod
    def _check_oferta(text: str, report: ExtractionReport) -> None:
        for p in _PALAVRAS_OFERTA:
            if p in text:
                report.add("oferta_financeira", p)
                return

    @staticmethod
    def _check_emocional(text: str, report: ExtractionReport) -> None:
        for p in _PALAVRAS_EMOCIONAL:
            if p in text:
                report.add("linguagem_emocional", p)
                return

    @staticmethod
    def _check_remetente(
        sender: str, known: set[str], report: ExtractionReport
    ) -> None:
        if not sender:
            report.add("remetente_desconhecido", "(sem remetente)")
            return
        if sender.lower() in {s.lower() for s in known}:
            report.add("remetente_conhecido", sender)
        else:
            report.add("remetente_desconhecido", sender)

    @staticmethod
    def _check_dominio_similar(sender: str, report: ExtractionReport) -> None:
        s = sender.lower()
        for marca in _DOMINIOS_CONHECIDOS:
            if marca in s and not s.endswith(f"@{marca}.com.br") and not s.endswith(f"@{marca}.com"):
                report.add("dominio_similar_conhecido", sender)
                return

    @staticmethod
    def _check_destinatarios(count: int, report: ExtractionReport) -> None:
        if count > 5:
            report.add("multiplos_destinatarios", f"{count} destinatários")

    @staticmethod
    def _check_anexos(attachments: list[str], report: ExtractionReport) -> None:
        for a in attachments:
            for ext in _EXTENSOES_EXECUTAVEIS:
                if a.lower().endswith(ext):
                    report.add("contem_anexo_executavel", a)
                    return

    @staticmethod
    def _check_sem_links(text: str, report: ExtractionReport) -> None:
        if not re.search(r"https?://\S+", text):
            report.add("sem_links")

    @staticmethod
    def _check_sem_anexos(attachments: list[str], report: ExtractionReport) -> None:
        if not attachments:
            report.add("sem_anexos")
