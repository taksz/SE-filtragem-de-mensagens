# Sistema Especialista para Filtragem de Mensagens Indesejadas

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=flat&logo=scikitlearn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/tests-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/github/license/taksz/SE-filtragem-de-mensagens?style=flat" alt="Licenca MIT" />
</p>

**Autores:** Arthur Magalhaes | Maurício Marques

Sistema especialista hibrido (simbolico + aprendizado de maquina) para classificacao de mensagens como **phishing**, **spam** ou **seguro**.

Desenvolvido como trabalho academico para demonstrar os conceitos de Inteligencia Artificial aplicados a seguranca da informacao.

---

## Arquitetura do Sistema

```
+-------------------------------------------------------------+
|                    MENSAGEM DE ENTRADA                       |
+----------------------------+--------------------------------+
                             |
                             v
              +--------------------------+
              |    EXTRATOR DE FATOS     |  Regex + heuristicas
              |   (fact_extractor.py)    |  -> conjunto de fatos
              +------------+-------------+
                           |
                 +---------+----------+
                 v                    v
        +----------------+   +-----------------+
        |    SISTEMA     |   |   MODULO DE     |
        |   SIMBOLICO    |   |  APRENDIZADO    |
        |                |   |  DE MAQUINA     |
        | - Base de      |   |                 |
        |   Conhecim.    |   | - TF-IDF        |
        |   (3 regras)   |   | - Regressao     |
        | - Motor de     |   |   Logistica     |
        |   Inferencia   |   | - Top features  |
        |   (forward     |   |                 |
        |    chaining)   |   |                 |
        +-------+--------+   +--------+--------+
                |                      |
                +----------+-----------+
                           v
              +--------------------------+
              |    SISTEMA HIBRIDO       |  Media ponderada
              |  (hybrid_system.py)      |  (60% regras + 40% ML)
              +------------+-------------+
                           |
                           v
              +--------------------------+
              |  MODULO DE EXPLICACAO    |  Relatorio completo:
              |   (explain())            |  fatos, regras, ML, veredito
              +--------------------------+
```

---

## Conceitos Teoricos

### Sistema Especialista

Um **sistema especialista** e um programa que emula o raciocinio de um especialista humano em um dominio especifico. Seus componentes fundamentais sao:

- **Base de Conhecimento:** O sistema classifica mensagens como phishing, spam ou seguro, para ajudar quem recebe mensagens (usuário final ou administrador de segurança) a não cair em golpes que roubam senhas e dados. Ele une regras da equipe (peso de 60%) a um modelo de ML, TF-IDF com regressão logística (peso de 40%), e gera um relatório que explica a decisão.

Fatos de entrada: o texto da mensagem, o remetente, os remetentes conhecidos, o número de destinatários e os anexos. O extrator transforma isso em fatos como link, link encurtado, pedido de dados pessoais, tom urgente, remetente desconhecido e anexos.
- **Motor de Inferencia:** algoritmo que aplica as regras aos fatos para derivar conclusoes. Usamos **encadeamento progressivo (forward chaining)**: partimos dos fatos e derivamos novas conclusoes iterativamente.
Motor de inferência

O motor usa encadeamento progressivo: parte dos fatos, dispara as regras satisfeitas, adiciona as conclusões e repete até nenhuma regra nova disparar. No caso do projeto:

Fatos iniciais: contem_link, pede_dados_pessoais e tom_urgente (mais link encurtado e remetente desconhecido, que reforçam a suspeita).
R1 dispara, porque as três condições estão presentes, e conclui phishing com certeza de 95%.
O ML também prevê phishing, com 87% de confiança. Como regras e ML concordam, a certeza combinada sobe e chega a cerca de 97%.
R2 dispara, pois a conclusão “phishing com alta certeza e concordância” agora é um fato. O resultado é alerta e quarentena reversível.
Nenhuma outra regra dispara, então o motor termina (ponto fixo) e o explain() mostra os fatos, as regras acionadas, a predição do ML e o veredito.
- **Memoria de Trabalho:** conjunto de fatos conhecidos sobre a mensagem sendo analisada.

### Fator de Certeza (Modelo MYCIN)

Cada regra possui um **fator de certeza (CF)** entre 0 e 1 que indica a confianca do especialista naquela regra. Quando duas regras levam a mesma conclusao, os fatores sao combinados usando a formula do MYCIN:

```
CF_combinado = CF1 + CF2 * (1 - CF1)
```

Isso garante que evidencias independentes reforcam a conclusao sem ultrapassar 1.0.

### Encadeamento Progressivo (Forward Chaining)

O motor percorre as regras repetidamente:

1. Verifica quais regras tem todas as condicoes satisfeitas pelos fatos atuais.
2. Dispara as regras satisfeitas, adicionando suas conclusoes ao conjunto de fatos.
3. Repete ate que nenhuma nova regra dispare (ponto fixo).

### Sistema Hibrido (Simbolico + ML)

O sistema combina dois paradigmas complementares:

- **Simbolico (regras):** explicavel, deterministico, baseado em conhecimento do especialista. Peso: 60%.
- **Estatistico (ML):** generaliza a partir de dados, captura padroes de vocabulario nao cobertos pelas regras. Peso: 40%.

A decisao final e a media ponderada dos dois subsistemas, com penalizacao em caso de discordancia.

### TF-IDF + Regressao Logistica

- **TF-IDF (Term Frequency-Inverse Document Frequency):** transforma texto em vetores numericos, valorizando palavras distintivas de cada classe.
- **Regressao Logistica Multinomial:** classificador linear interpretavel -- os coeficientes revelam quais palavras mais pesam em cada classe.

---

## Estrutura do Repositorio

```
SE-filtragem-de-mensagens/
|-- expert_system/              # Modulo simbolico
|   |-- __init__.py
|   |-- knowledge_base.py       # Base de conhecimento (3 regras)
|   |-- fact_extractor.py       # Extracao de fatos do texto
|   |-- inference_engine.py     # Motor de inferencia (forward chaining)
|-- ml/                         # Modulo de aprendizado de maquina
|   |-- __init__.py
|   |-- dataset.py              # Gerador de dataset sintetico
|   |-- classifier.py           # TF-IDF + Regressao Logistica
|-- tests/                      # Suite de testes (pytest)
|   |-- test_knowledge_base.py
|   |-- test_fact_extractor.py
|   |-- test_inference_engine.py
|   |-- test_ml_classifier.py
|   |-- test_hybrid_system.py
|-- data/                       # Dados gerados (nao versionados)
|-- hybrid_system.py            # Combinacao regras + ML
|-- main.py                     # CLI principal
|-- requirements.txt
|-- LICENSE
|-- README.md
```

---

## Como Executar

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/taksz/SE-filtragem-de-mensagens.git
cd SE-filtragem-de-mensagens
pip install -r requirements.txt
```

### 2. Rodar a demonstracao

```bash
python main.py --demo
```

Analisa 4 mensagens de exemplo (phishing, spam, seguro) e exibe o relatorio completo de cada uma.

### 3. Modo interativo

```bash
python main.py --interactive
```

### 4. Analisar uma mensagem especifica

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

## Testes

A suite cobre **5 modulos** com **40+ cenarios**:

| Modulo                       | Cenarios de Teste                                                         |
|------------------------------|---------------------------------------------------------------------------|
| `test_knowledge_base.py`     | Regras carregadas, unicidade, faixa de CF, condicoes                      |
| `test_fact_extractor.py`     | Deteccao de links, urgencia, dados pessoais, spoofing, anexos             |
| `test_inference_engine.py`   | Disparo de regras, combinacao MYCIN, trilha de auditoria, regras custom   |
| `test_ml_classifier.py`     | Dataset, predicao por classe, persistencia, metricas >= 70%               |
| `test_hybrid_system.py`     | Integracao end-to-end, explicacao, funcionamento sem ML                   |

---

## Exemplo de Saida

```
============================================================
  RELATORIO DE ANALISE -- SISTEMA ESPECIALISTA HIBRIDO
============================================================

FATOS EXTRAIDOS DA MENSAGEM:
   - contem_link (evidencia: "https://bit.ly/nubank-verify")
   - contem_link_encurtado (evidencia: "https://bit.ly/nubank-verify")
   - pede_dados_pessoais (evidencia: "senha")
   - remetente_desconhecido (evidencia: "seguranca@nubannk.com")
   - tom_urgente (evidencia: "urgente")

REGRAS DISPARADAS (encadeamento progressivo):
   1. [R1_phishing_classico] -> phishing (certeza: 95%)
      Motivo: Mensagem contem link, pede dados pessoais e usa tom de urgencia.

CONCLUSAO DO SISTEMA SIMBOLICO:
   Classificacao: PHISHING (certeza: 95%)

PREDICAO DO MODELO DE ML (TF-IDF + Regressao Logistica):
   Classificacao: PHISHING (confianca: 87%)
   Palavras-chave que mais influenciaram:
     - "confirme seus dados" (peso: 0.3421)
     - "bloqueada" (peso: 0.2815)

============================================================
   VEREDITO FINAL: PHISHING (confianca: 97%)
============================================================
```

---

## Licenca

MIT License -- veja [LICENSE](LICENSE).
