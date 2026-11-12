"""
Gerador de Dataset Sintético para treinamento e teste do classificador.

Em um cenário real, usaríamos dados de e-mails rotulados (ex.: SpamAssassin
Public Corpus). Aqui geramos amostras realistas em português para manter o
repositório autocontido — sem dependência de download externo.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Templates de mensagens (português brasileiro)
# ---------------------------------------------------------------------------

_PHISHING_TEMPLATES = [
    "URGENTE: Sua conta foi bloqueada. Acesse https://bit.ly/seguranca-{id} e confirme seus dados para evitar o cancelamento.",
    "Prezado cliente, detectamos uma atividade suspeita. Atualize seu cadastro imediatamente: https://tinyurl.com/banco-{id}",
    "Seu cartão foi clonado! Informe seus dados bancários em https://bit.ly/cartao-{id} para proteção imediata.",
    "Atenção: seu CPF está irregular na Receita Federal. Regularize agora: https://is.gd/receita-{id}. Prazo final hoje!",
    "Aviso do Banco: confirme sua senha e token em https://cutt.ly/banco-{id} para não ter sua conta suspensa.",
    "Seu pacote dos Correios foi retido. Pague a taxa de R$3,50 em https://bit.ly/correios-{id} para liberar.",
    "Netflix: sua assinatura expira hoje. Atualize seu cartão em https://tinyurl.com/netflix-{id} imediatamente.",
    "Nubank: detectamos compra de R$4.999. Se não reconhece, informe seus dados aqui: https://bit.ly/nubank-{id}",
]

_SPAM_TEMPLATES = [
    "PROMOÇÃO IMPERDÍVEL! Ganhe um iPhone GRÁTIS! Acesse https://oferta-{id}.com e cadastre-se agora!",
    "Parabéns, você foi sorteado! Resgate seu prêmio de R$10.000 em https://premio-{id}.com",
    "Ganhe dinheiro fácil trabalhando de casa! Lucre R$5.000/mês. Saiba mais: https://rendaextra-{id}.com",
    "DESCONTO de 90% em todos os produtos! Só hoje! https://megaoferta-{id}.com — não perca!",
    "Invista em Bitcoin e tenha rendimento garantido de 30% ao mês! https://crypto-{id}.com",
    "Cashback de R$500 no Pix! Cadastre-se grátis: https://pixcashback-{id}.com",
    "Renda extra garantida! Ganhe R$200 por dia respondendo pesquisas: https://pesquisa-{id}.com",
    "Oferta relâmpago: curso completo de inglês GRATUITO por tempo limitado! https://curso-{id}.com",
]

_SAFE_TEMPLATES = [
    "Oi, tudo bem? Vamos almoçar amanhã no restaurante da esquina?",
    "Segue em anexo o relatório trimestral conforme solicitado na reunião de ontem.",
    "Bom dia! Confirmo presença na reunião de sexta-feira às 14h.",
    "Obrigado pelo envio. Vou revisar o documento e retorno até amanhã.",
    "Oi! Vi sua mensagem. Podemos conversar depois do expediente?",
    "Prezado Arthur, segue a ata da reunião de planejamento. Abraços.",
    "Lembrete: entrega do projeto dia 15. Precisa de ajuda com algo?",
    "Feliz aniversário! Tudo de bom pra você! Abraços da equipe.",
    "A apresentação ficou ótima. Parabéns pelo trabalho!",
    "Oi, cheguei bem. O voo atrasou um pouco mas está tudo certo.",
    "Segue o link do repositório do projeto: https://github.com/equipe/projeto",
    "Bom dia, a reunião de hoje foi adiada para as 16h. Pode confirmar?",
]

_SUSPICIOUS_TEMPLATES = [
    "AJUDA URGENTE: Preciso que me transfira R$500 agora, é vida ou morte! https://bit.ly/ajuda-{id}",
    "Por favor me ajude, estou desesperado. Acesse este link e veja: https://tinyurl.com/socorro-{id}",
    "Não sei o que fazer! Clique aqui para entender: https://cutt.ly/info-{id}. É urgente!",
    "Socorro! Minha conta foi hackeada. Preciso que acesse https://bit.ly/recover-{id} e siga as instruções.",
]


def generate_dataset(
    output_path: str | Path = "data/dataset.csv",
    n_samples: int = 400,
    seed: int = 42,
) -> Path:
    """
    Gera dataset CSV com colunas: text, label.

    Labels: phishing, spam, seguro, suspeito.
    Distribuição aproximada: 25% cada classe (balanceado).
    """
    rng = random.Random(seed)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    samples: list[tuple[str, str]] = []
    per_class = n_samples // 4

    for _ in range(per_class):
        t = rng.choice(_PHISHING_TEMPLATES).format(id=rng.randint(1000, 9999))
        samples.append((t, "phishing"))

    for _ in range(per_class):
        t = rng.choice(_SPAM_TEMPLATES).format(id=rng.randint(1000, 9999))
        samples.append((t, "spam"))

    for _ in range(per_class):
        t = rng.choice(_SAFE_TEMPLATES)
        samples.append((t, "seguro"))

    for _ in range(n_samples - 3 * per_class):
        t = rng.choice(_SUSPICIOUS_TEMPLATES).format(id=rng.randint(1000, 9999))
        samples.append((t, "suspeito"))

    rng.shuffle(samples)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(samples)

    return path
