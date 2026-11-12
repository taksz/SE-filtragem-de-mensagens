# 🛡️ Sistema Especialista para Filtragem de Mensagens Indesejadas

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=flat&logo=scikitlearn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/github/license/taksz/sistema-especialista-filtragem-mensagens?style=flat" alt="Licença MIT" />
</p>

**Autor:** Arthur Magalhães

Sistema especialista híbrido (simbólico + aprendizado de máquina) para classificação de mensagens como **phishing**, **spam** ou **seguro**.

Desenvolvido como trabalho acadêmico para demonstrar os conceitos de Inteligência Artificial aplicados à segurança da informação.

---

## 📐 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    MENSAGEM DE ENTRADA                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │    EXTRATOR DE FATOS    │  Regex + heurísticas
         │   (fact_extractor.py)   │  → conjunto de fatos
         └────────┬────────────────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌───────────────┐   ┌────────────────┐
│   SISTEMA     │   │   MÓDULO DE    │
│  SIMBÓLICO    │   │  APRENDIZADO   │
│               │   │  DE MÁQUINA    │
│ • Base de     │   │               │
│   Conhecim.   │   │ • TF-IDF      │
│   (3 regras)  │   │ • Regressão   │
│ • Motor de    │   │   Logística   │
│   Inferência  │   │ • Top features│
│   (forward    │   │               │
│    chaining)  │   │               │
└───────┬───────┘   └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  ▼
     ┌────────────────────────┐
     │    SISTEMA HÍBRIDO     │  Média ponderada
     │  (hybrid_system.py)    │  (60% regras + 40% ML)
     └────────────┬───────────┘
                  │
                  ▼
     ┌────────────────────────┐
     │  MÓDULO DE EXPLICAÇÃO  │  Relatório completo:
     │   (explain())          │  fatos, regras, ML, veredito
     └────────────────────────┘
```

---

## 🧠 Conceitos Teóricos

### Sistema Especialista
Um **sistema especialista** é um programa que emula o raciocínio de um especialista humano em um domínio específico. Seus componentes fundamentais são:

- **Base de Conhecimento:** conjunto de regras IF-THEN que codificam o conhecimento do especialista. Neste projeto, são 3 regras que capturam padrões de phishing, spam e mensagens legítimas.
- **Motor de Inferência:** algoritmo que aplica as regras aos fatos para derivar conclusões. Usamos **encadeamento progressivo (forward chaining)**: partimos dos fatos e derivamos novas conclusões iterativamente.
- **Memória de Trabalho:** conjunto de fatos conhecidos sobre a mensagem sendo analisada.

### Fator de Certeza (Modelo MYCIN)
Cada regra possui um **fator de certeza (CF)** entre 0 e 1 que indica a confiança do especialista naquela regra. Quando duas regras levam à mesma conclusão, os fatores são combinados usando a fórmula do MYCIN:

```
CF_combinado = CF₁ + CF₂ × (1 - CF₁)
```

Isso garante que evidências independentes reforçam a conclusão sem ultrapassar 1.0.

### Encadeamento Progressivo (Forward Chaining)
O motor percorre as regras repetidamente:
1. Verifica quais regras têm todas as condições satisfeitas pelos fatos atuais.
2. Dispara as regras satisfeitas, adicionando suas conclusões ao conjunto de fatos.
3. Repete até que nenhuma nova regra dispare (ponto fixo).

### Sistema Híbrido (Simbólico + ML)
O sistema combina dois paradigmas complementares:
- **Simbólico (regras):** explicável, determinístico, baseado em conhecimento do especialista. Peso: 60%.
- **Estatístico (ML):** generaliza a partir de dados, captura padrões de vocabulário não cobertos pelas regras. Peso: 40%.

A decisão final é a média ponderada dos dois subsistemas, com penalização em caso de discordância.

### TF-IDF + Regressão Logística
- **TF-IDF (Term Frequency–Inverse Document Frequency):** transforma texto em vetores numéricos, valorizando palavras distintivas de cada classe.
- **Regressão Logística Multinomial:** classificador linear interpretável — os coeficientes revelam quais palavras mais pesam em cada classe.

---

## 📁 Estrutura do Repositório

```
sistema-especialista-filtragem-mensagens/
├── expert_system/              # Módulo simbólico
│   ├── __init__.py
│   ├── knowledge_base.py       # Base de conhecimento (3 regras)
│   ├── fact_extractor.py       # Extração de fatos do texto
│   └── inference_engine.py     # Motor de inferência (forward chaining)
├── ml/                         # Módulo de aprendizado de máquina
│   ├── __init__.py
│   ├── dataset.py              # Gerador de dataset sintético
│   └── classifier.py           # TF-IDF + Regressão Logística
├── tests/                      # Suíte de testes (pytest)
│   ├── test_knowledge_base.py
│   ├── test_fact_extractor.py
│   ├── test_inference_engine.py
│   ├── test_ml_classifier.py
│   └── test_hybrid_system.py
├── data/                       # Dados gerados (não versionados)
├── hybrid_system.py            # Combinação regras + ML
├── main.py                     # CLI principal
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Como Executar

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/taksz/sistema-especialista-filtragem-mensagens.git
cd sistema-especialista-filtragem-mensagens
pip install -r requirements.txt
```

### 2. Rodar a demonstração

```bash
python main.py --demo
```

Analisa 4 mensagens de exemplo (phishing, spam, seguro) e exibe o relatório completo de cada uma.

### 3. Modo interativo

```bash
python main.py --interactive
```

### 4. Analisar uma mensagem específica

```bash
python main.py --analyze "URGENTE: confirme sua senha em https://bit.ly/seguro"
```

### 5. Treinar e avaliar o modelo ML

```bash
python main.py --train
```

### 6. Rodar os testes

```bash
pytest tests/ -v
```

---

## 🧪 Testes

A suíte cobre **5 módulos** com **40+ cenários**:

| Módulo | Cenários de Teste |
|--------|------------------|
| `test_knowledge_base.py` | Regras carregadas, unicidade, faixa de CF, condições |
| `test_fact_extractor.py` | Detecção de links, urgência, dados pessoais, spoofing, anexos |
| `test_inference_engine.py` | Disparo de regras, combinação MYCIN, trilha de auditoria, regras custom |
| `test_ml_classifier.py` | Dataset, predição por classe, persistência, métricas ≥ 70% |
| `test_hybrid_system.py` | Integração end-to-end, explicação, funcionamento sem ML |

---

## 📊 Exemplo de Saída

```
============================================================
  RELATÓRIO DE ANÁLISE — SISTEMA ESPECIALISTA HÍBRIDO
============================================================

📋 FATOS EXTRAÍDOS DA MENSAGEM:
   • contem_link (evidência: "https://bit.ly/nubank-verify")
   • contem_link_encurtado (evidência: "https://bit.ly/nubank-verify")
   • pede_dados_pessoais (evidência: "senha")
   • remetente_desconhecido (evidência: "seguranca@nubannk.com")
   • tom_urgente (evidência: "urgente")

⚙️  REGRAS DISPARADAS (encadeamento progressivo):
   1. [R1_phishing_classico] → phishing (certeza: 95%)
      Motivo: Mensagem contém link, pede dados pessoais e usa tom de urgência.

🔎 CONCLUSÃO DO SISTEMA SIMBÓLICO:
   Classificação: PHISHING (certeza: 95%)

🤖 PREDIÇÃO DO MODELO DE ML (TF-IDF + Regressão Logística):
   Classificação: PHISHING (confiança: 87%)
   Palavras-chave que mais influenciaram:
     • "confirme seus dados" (peso: 0.3421)
     • "bloqueada" (peso: 0.2815)

============================================================
  🚨 VEREDITO FINAL: PHISHING (confiança: 97%)
============================================================
```

---

## 📝 Licença

MIT License — veja [LICENSE](LICENSE).
