# Ética e Impactos da IA — Análise do Sistema Especialista de Filtragem de Mensagens

## 1. Leitura e vídeo

**Artigo.** A questão de integridade acadêmica é declarar o uso de IA de forma específica e verdadeira: para que a ferramenta serviu, o que foi aproveitado e como o resultado foi conferido. A equipe continua responsável pelo conteúdo. A IA não pode aparecer como autora nem ser citada como fonte sem verificação.

**Vídeo.** Ponto de partida: um trecho sobre responsabilidade institucional por sistemas automatizados, que se liga ao dilema do projeto (quem responde quando o filtro erra).

## 2. Análise ética do projeto

**Apresentação.** O projeto é um sistema especialista híbrido que classifica mensagens como phishing, spam ou seguro, desenvolvido por Arthur Magalhães e Maurício Marques. O problema é que golpes por mensagem enganam pessoas e levam ao roubo de senhas e dados. Quem usa o sistema é quem recebe mensagens (usuário final ou administrador de segurança). Podem ser afetados pelas saídas o destinatário, o remetente legítimo classificado por engano e as organizações imitadas pelos golpes.

**Onde a IA participa.**

- **Regras da equipe (peso 60%):** um extrator de fatos (links, link encurtado, pedido de dados pessoais, tom urgente, remetente desconhecido, anexos) alimenta regras IF-THEN com fator de certeza (modelo MYCIN) e encadeamento progressivo. Exemplo: a regra R1 (link + dados pessoais + urgência → phishing, 95%).
- **Modelo de ML (peso 40%):** TF-IDF com regressão logística, que prevê a classe pelo vocabulário do texto.
- **Combinação:** se regras e ML concordam, soma-se 0,1 à certeza; se discordam, prevalece o maior escore ponderado, com penalização de 20%.

| Aspecto | Situação concreta | Quem é afetado | Medida da equipe |
| --- | --- | --- | --- |
| Privacidade e dados | O sistema lê texto completo, remetente e anexos, que podem conter dados pessoais ou sigilosos. O dataset de treino é sintético e não versionado, o que evita expor pessoas reais. | Destinatários e remetentes | Não armazenar mensagens analisadas, mostrar só trechos-evidência no relatório e manter dados reais fora do repositório. Se treinar com mensagens reais, anonimizar antes. |
| Viés e equidade | A regra "tom urgente + dados pessoais + link" pode marcar como phishing um aviso legítimo de banco, escola ou hospital. "Remetente desconhecido" penaliza contatos novos. Um dataset sintético pode não representar gírias e regionalismos. | Quem escreve de modo informal ou com urgência real; remetentes novos | Criar casos de teste pareados (mesmo conteúdo, tom ou remetente diferente) e medir falsos positivos por tipo de mensagem. Diversificar o dataset. |
| Transparência | O `explain()` já mostra fatos extraídos com evidência, regras disparadas, probabilidades do ML e palavras de maior peso. A certeza combinada (ex.: 97%) pode parecer mais precisa do que é, pois pesos 60/40 e bônus de 0,1 não foram calibrados. | Quem recebe o veredito | Rotular a saída como classificação automática, explicar o motivo em linguagem simples e informar que a confiança é uma estimativa. |
| Supervisão e responsabilidade | Um e-mail legítimo de fornecedor é classificado como phishing e fica retido. | Remetente e destinatário | Não apagar automaticamente: apenas marcar ou pôr em quarentena. Oferecer botão "não é phishing" e definir um responsável (administrador de segurança) por revisar contestações e ajustar as regras. |
| Impacto social | Beneficia quem evita golpes, sobretudo pessoas com menos familiaridade digital. Se tratado como definitivo, um falso negativo gera falsa segurança e um falso positivo bloqueia comunicação importante. | Usuários vulneráveis a golpes; remetentes legítimos bloqueados | Apresentar o resultado como apoio à decisão, nunca como garantia, e manter a orientação de verificar o remetente por outro canal. |

## 3. Debate em sala e reflexão individual

**Dilema.** Quando o sistema classifica uma mensagem como phishing com alta certeza, ele deve bloquear automaticamente ou apenas alertar o usuário?

- **Opção A, bloquear.** Reduz o risco de o usuário cair no golpe, mas um falso positivo impede o recebimento de mensagens legítimas sem que ninguém perceba, e o sistema decide sozinho.
- **Opção B, alertar e deixar o usuário decidir.** Preserva a autonomia e permite contestação, mas depende de o usuário ler o aviso; quem é menos atento pode ignorá-lo.

Encaminhamento: alertar sempre e só colocar em quarentena reversível quando regra e ML concordarem com alta certeza.

**Ideia do artigo ou vídeo que sustenta a análise:** responsabilidade humana sobre a decisão automatizada.

**Questão do debate, adaptada ao projeto.** Se o sistema classificar uma mensagem de um colaborador ou aluno como phishing, em que condições isso deveria ser compartilhado com o administrador ou a coordenação?

- **Quando faz sentido:** quando há risco coletivo (um golpe circulando na organização) e o compartilhamento se limita ao necessário, ou seja, o conteúdo malicioso e não a vida do destinatário.
- **Quem se beneficia:** a organização e os demais usuários, que passam a se proteger do mesmo golpe.
- **Quem pode ser prejudicado:** o destinatário, se virar suspeito de ter "recebido" ou "clicado", e o remetente legítimo classificado por engano.

## 4. Declaração de uso de sistemas de IA

### IA incorporada ao projeto

O projeto utiliza um sistema especialista híbrido (regras IF-THEN com fator de certeza MYCIN e encadeamento progressivo, combinado a TF-IDF + regressão logística) para classificar mensagens como phishing, spam ou seguro. O sistema recebe o texto da mensagem, o remetente, remetentes conhecidos, número de destinatários e anexos, e gera uma classificação, um nível de confiança e um relatório de explicação. A equipe verificou seu funcionamento por meio de uma suíte pytest com mais de 40 cenários, cobrindo base de conhecimento, extração de fatos, motor de inferência, classificador e sistema híbrido, incluindo desempenho mínimo de 70% do modelo de ML em dados sintéticos. As limitações identificadas incluem dataset sintético, pesos 60/40 não calibrados, regras que podem gerar falsos positivos em mensagens legítimas urgentes e confiança que pode parecer mais precisa do que é. Mensagens de baixa confiança, discordância entre regras e ML ou contestação do usuário exigem revisão. A revisão cabe ao administrador de segurança ou responsável pelo sistema.

### IA utilizada na elaboração do trabalho

Utilizei o Claude (Anthropic) para redigir um rascunho das respostas desta atividade a partir do README e do código do repositório do projeto. Aproveitei a estrutura da análise e os exemplos de situações, após conferir com o código e o README do projeto, ajustar o que não correspondia ao sistema e completar com minhas próprias leituras do artigo e do vídeo.

## Fontes

- [Repositório taksz/SE-filtragem-de-mensagens](https://github.com/taksz/SE-filtragem-de-mensagens)
- [hybrid_system.py](https://github.com/taksz/SE-filtragem-de-mensagens/blob/main/hybrid_system.py)
