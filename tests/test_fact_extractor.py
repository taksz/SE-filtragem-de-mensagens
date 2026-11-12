"""Testes do Extrator de Fatos."""

import pytest
from expert_system.fact_extractor import FactExtractor


@pytest.fixture
def extractor():
    return FactExtractor()


class TestFactExtractor:
    """Testes de extração de fatos a partir de texto."""

    def test_detects_link(self, extractor):
        report = extractor.extract("Acesse https://example.com agora")
        assert "contem_link" in report.facts

    def test_detects_shortened_link(self, extractor):
        report = extractor.extract("Clique em https://bit.ly/abc123")
        assert "contem_link_encurtado" in report.facts
        assert "contem_link" in report.facts

    def test_detects_urgency(self, extractor):
        report = extractor.extract("URGENTE: sua conta será bloqueada!")
        assert "tom_urgente" in report.facts

    def test_detects_personal_data_request(self, extractor):
        report = extractor.extract("Por favor informe sua senha e CPF")
        assert "pede_dados_pessoais" in report.facts

    def test_detects_financial_offer(self, extractor):
        report = extractor.extract("Parabéns! Você ganhou um prêmio GRÁTIS!")
        assert "oferta_financeira" in report.facts

    def test_detects_unknown_sender(self, extractor):
        report = extractor.extract("Olá", sender="spam@evil.com")
        assert "remetente_desconhecido" in report.facts

    def test_detects_known_sender(self, extractor):
        report = extractor.extract(
            "Olá",
            sender="amigo@empresa.com",
            known_senders={"amigo@empresa.com"},
        )
        assert "remetente_conhecido" in report.facts

    def test_detects_similar_domain(self, extractor):
        report = extractor.extract("Olá", sender="suporte@nubank-seguro.xyz")
        assert "dominio_similar_conhecido" in report.facts

    def test_detects_executable_attachment(self, extractor):
        report = extractor.extract("Veja o anexo", attachments=["virus.exe"])
        assert "contem_anexo_executavel" in report.facts

    def test_detects_multiple_recipients(self, extractor):
        report = extractor.extract("Oferta!", recipient_count=20)
        assert "multiplos_destinatarios" in report.facts

    def test_safe_message_facts(self, extractor):
        """Mensagem simples sem links/anexos de remetente conhecido."""
        report = extractor.extract(
            "Oi, tudo bem? Vamos almoçar amanhã?",
            sender="colega@empresa.com",
            known_senders={"colega@empresa.com"},
        )
        assert "remetente_conhecido" in report.facts
        assert "sem_links" in report.facts
        assert "sem_anexos" in report.facts

    def test_emotional_language(self, extractor):
        report = extractor.extract("Por favor me ajude, estou desesperado!")
        assert "linguagem_emocional" in report.facts

    def test_evidence_is_recorded(self, extractor):
        report = extractor.extract("Sua senha foi comprometida!")
        assert "pede_dados_pessoais" in report.facts
        assert len(report.evidence["pede_dados_pessoais"]) > 0

    def test_empty_message(self, extractor):
        report = extractor.extract("")
        assert "sem_links" in report.facts
        assert "sem_anexos" in report.facts
