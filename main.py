#!/usr/bin/env python3
"""
CLI principal do Sistema Especialista para Filtragem de Mensagens.

Modos de uso:
    python main.py --demo           # Roda demonstração com mensagens de exemplo
    python main.py --interactive     # Modo interativo (digita mensagens)
    python main.py --train           # Só treina o modelo ML e mostra métricas
    python main.py --analyze "texto" # Analisa uma mensagem específica
"""

from __future__ import annotations

import argparse
import sys
import json

from ml.dataset import generate_dataset
from hybrid_system import HybridSystem


def run_demo(system: HybridSystem) -> None:
    """Demonstração com mensagens representativas de cada categoria."""
    print("\n" + "=" * 60)
    print("   DEMONSTRACAO DO SISTEMA ESPECIALISTA HIBRIDO")
    print("=" * 60)

    test_messages = [
        {
            "text": (
                "URGENTE: Sua conta Nubank foi bloqueada por atividade suspeita. "
                "Confirme seus dados e senha em https://bit.ly/nubank-verify para "
                "evitar o cancelamento imediato da sua conta."
            ),
            "sender": "seguranca@nubannk.com",  # typo intencional: spoofing
            "description": "Phishing clássico (spoofing Nubank + urgência + link encurtado)",
        },
        {
            "text": (
                "Parabéns! Você foi sorteado para ganhar um iPhone 15 GRÁTIS! "
                "Acesse https://mega-premio.com e cadastre-se para resgatar. "
                "Oferta por tempo limitado! Não perca!"
            ),
            "sender": "promo@desconhecido.xyz",
            "recipient_count": 50,
            "description": "Spam promocional (oferta + muitos destinatários)",
        },
        {
            "text": (
                "Oi Arthur, tudo bem? Segue em anexo o relatório da reunião "
                "de ontem. Qualquer dúvida me avisa. Abraços!"
            ),
            "sender": "maria@empresa.com.br",
            "known_senders": {"maria@empresa.com.br"},
            "description": "Mensagem legítima (remetente conhecido, sem links)",
        },
        {
            "text": (
                "Bom dia, confirmo presença na reunião de amanhã às 14h. "
                "Qualquer mudança me avisa. Abraços!"
            ),
            "sender": "joao@empresa.com.br",
            "known_senders": {"joao@empresa.com.br"},
            "description": "Mensagem segura (remetente conhecido, sem links, sem anexos)",
        },
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'-' * 60}")
        print(f"  MENSAGEM {i}: {msg['description']}")
        print(f"{'-' * 60}")
        print(f"Texto: \"{msg['text'][:100]}...\"")
        print(f"Remetente: {msg.get('sender', '(vazio)')}")

        verdict = system.analyze(
            msg["text"],
            sender=msg.get("sender", ""),
            known_senders=msg.get("known_senders"),
            recipient_count=msg.get("recipient_count", 1),
            attachments=msg.get("attachments"),
        )

        print(verdict.explain())


def run_interactive(system: HybridSystem) -> None:
    """Modo interativo: o usuário digita mensagens para análise."""
    print("\nModo interativo -- digite uma mensagem para analisar (ou 'sair'):\n")

    while True:
        try:
            text = input(">> Mensagem: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if text.lower() in ("sair", "exit", "quit", "q"):
            print("Encerrando.")
            break

        if not text:
            continue

        sender = input(">> Remetente (Enter para vazio): ").strip()
        verdict = system.analyze(text, sender=sender)
        print(verdict.explain())


def run_train(system: HybridSystem) -> None:
    """Treina o modelo e exibe métricas."""
    print("\n[*] Gerando dataset...")
    generate_dataset()
    print("[*] Treinando modelo ML...")
    metrics = system.train_ml()

    print("\nMETRICAS DE AVALIACAO (conjunto de teste -- 30%):\n")
    for cls in ["phishing", "spam", "seguro"]:
        if cls in metrics:
            m = metrics[cls]
            print(f"  {cls:>10}: precision={m['precision']:.2f}  "
                  f"recall={m['recall']:.2f}  f1={m['f1-score']:.2f}")
    acc = metrics.get("accuracy", 0)
    print(f"\n  {'Acuracia':>10}: {acc:.2%}")


def run_analyze(system: HybridSystem, text: str) -> None:
    """Analisa uma mensagem passada por argumento."""
    verdict = system.analyze(text)
    print(verdict.explain())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistema Especialista para Filtragem de Mensagens Indesejadas"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Modo demonstração")
    group.add_argument("--interactive", action="store_true", help="Modo interativo")
    group.add_argument("--train", action="store_true", help="Treinar modelo ML")
    group.add_argument("--analyze", type=str, help="Analisar uma mensagem")

    args = parser.parse_args()

    # Gerar dataset e treinar ML por padrão
    print("[*] Inicializando sistema...")
    generate_dataset()

    system = HybridSystem()
    print("[*] Treinando classificador ML...")
    system.train_ml()
    print("[+] Sistema pronto!\n")

    if args.train:
        run_train(system)
    elif args.interactive:
        run_interactive(system)
    elif args.analyze:
        run_analyze(system, args.analyze)
    else:
        # Default: demo
        run_demo(system)


if __name__ == "__main__":
    main()
