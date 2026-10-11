# Memória Descritiva — Kairos

> Versão da 1.ª entrega (11/10/2026), fase de conceção. Será atualizada nas entregas seguintes.

## a. Identificação

| Campo | Valor |
|---|---|
| **Nome do projeto** | Kairos — Sistema Distribuído de Despacho de Emergências |
| **Ano letivo** | 2026/2027 |
| **Semestre** | 1.º semestre (5.º semestre da Licenciatura em Engenharia Informática) |
| **Unidades curriculares** | Projeto de Desenvolvimento de Software; Engenharia de Software; Segurança Informática; Sistemas Distribuídos; Inteligência Artificial |
| **Docentes** | Rui Pascoal e Miguel Boavida (Projeto de Desenvolvimento de Software); Rui Ramos (Engenharia de Software); Sérgio Nunes e Pedro Brandão (Segurança Informática); Pedro Rosa (Sistemas Distribuídos); Samuel Gomes (Inteligência Artificial) |

## b. Resumo

O Kairos é um sistema distribuído de despacho de emergências médicas, desenvolvido no âmbito do projeto multidisciplinar do 5.º semestre da Licenciatura em Engenharia Informática da Universidade Europeia.

Numa emergência, o tempo até à chegada do socorro é determinante, e parte desse tempo perde-se antes de o meio sair: a decidir que ambulância enviar e por onde. Quando essa decisão depende apenas do operador, a ambulância mais próxima em linha reta pode não ser a mais rápida pelas estradas, e as ocorrências tendem a ser tratadas por ordem de chegada, o que pode deixar um caso grave sem o meio de que precisa. Além disso, uma central de emergência não pode parar: um sistema que dependa de um único servidor é um ponto único de falha inaceitável.

O Kairos responde a estes dois problemas. Para **decidir melhor**, o operador regista cada ocorrência (localização, nome da vítima, breve descrição e nível de gravidade, numa escala de cinco níveis inspirada na Triagem de Manchester) e o sistema atribui automaticamente o meio. A decisão combina dois algoritmos de Inteligência Artificial implementados pelo grupo. O A\* calcula o tempo de chegada de cada meio sobre a rede de estradas real do OpenStreetMap. Um problema de satisfação de restrições (CSP) decide que meio vai para cada ocorrência, minimizando o tempo de chegada ponderado pela gravidade. Um meio a caminho de um caso menos grave pode ser desviado para um caso mais grave, e, quando um distrito não tem meios livres, o sistema recorre aos distritos vizinhos.

Para **nunca parar**, o sistema corre num cluster Kubernetes (k3s) com três máquinas. Todos os componentes estão replicados em máquinas diferentes: ingress, frontend, API e base de dados PostgreSQL com uma réplica síncrona. A API não guarda estado, pelo que qualquer réplica atende qualquer pedido. A base de dados garante que uma ocorrência confirmada ao operador nunca se perde e que um meio nunca é atribuído a duas ocorrências ao mesmo tempo, através de uma atualização condicional. As alterações chegam aos operadores e às unidades em tempo real, por WebSockets. O sistema mantém o serviço perante a falha de uma máquina inteira.

A segurança acompanha toda a solução: comunicação cifrada (HTTPS e WSS), autenticação com tokens JWT e palavras-passe guardadas com *hash*, acesso limitado por perfil e por distrito, cifra do nome da vítima e da descrição da ocorrência (RGPD) e registo de auditoria de todas as atribuições.

O sistema foi pensado para ser multipaís: os distritos são apenas uma divisão dos dados, pelo que a mesma solução pode ser usada com condados ou outras divisões regionais.

Nesta primeira entrega, o trabalho centrou-se na conceção: análise do problema, requisitos, modelação UML, arquitetura distribuída, modelo de faltas, componentes de IA e segurança, e planeamento. As entregas seguintes incluem o protótipo funcional e, por fim, a versão final, com a demonstração prática dos mecanismos de tolerância a faltas.

## c. Contexto

### i. Problema abordado

| Problema | Consequência |
|---|---|
| Não se sabe com exatidão quanto tempo cada meio demora a chegar | O meio mais próximo em linha reta pode não ser o mais rápido pelas estradas |
| As ocorrências são tratadas por ordem de chegada | Um caso leve pode ficar com o meio de que um caso grave vai precisar |
| A central depende de um único servidor | Se o servidor falhar, deixa de haver despacho |

### ii. Motivação

O despacho de emergências é um caso em que a distribuição é **requerida**, e não apenas opcional: a disponibilidade e a integridade dos dados têm impacto direto na vida das pessoas. Este contexto permite aplicar, de forma justificada, os conceitos centrais de sistemas distribuídos (replicação, consistência, concorrência, deteção de falhas e recuperação) e oferece problemas reais para os algoritmos de procura e de satisfação de restrições lecionados em Inteligência Artificial.

### iii. Objetivos

- Desenvolver uma plataforma web responsiva para o operador da central e para as unidades de emergência.
- Atribuir automaticamente meios a ocorrências através de um CSP, com prioridade à gravidade e reatribuição para casos mais graves.
- Calcular rotas e tempos de chegada pela rede de estradas real através do A\*.
- Garantir que nenhuma ocorrência confirmada se perde e que um meio nunca é atribuído a duas ocorrências.
- Manter o serviço disponível perante a falha de qualquer componente ou de uma máquina inteira.
- Proteger os dados pessoais e controlar o acesso por perfil.
- Demonstrar experimentalmente a tolerância a faltas através de testes de falha com métricas.

## d. Processo

### i. Metodologia utilizada

O projeto segue uma metodologia ágil baseada em **Kanban**, com um quadro no Trello (Backlog → Em curso → Bloqueado → Em revisão → Concluído) e um limite de duas tarefas em curso por pessoa. O código é gerido no GitHub: todas as alterações entram por *pull request* revisto por outro elemento do grupo. O trabalho está organizado em três marcos, um por entrega:

| Marco | Data | Objetivo |
|---|---|---|
| Entrega 1 – Conceção | 11/10/2026 | Problema, requisitos, modelação, arquitetura, modelo de faltas, relatório v1 |
| Entrega 2 – Protótipo | 15/11/2026 | Cluster Kubernetes, base de dados replicada, API, A\* e CSP, primeiros testes de falha |
| Entrega 3 – Versão final | 20/12/2026 | Frontend completo, segurança, testes de falha com métricas, demonstração |

### ii. Ferramentas utilizadas

GitHub (código e revisões), Trello (quadro Kanban), Visual Studio Code, Postman (testes à API), Discord (comunicação), PlantUML (diagramas UML) e Canva (apresentações).

### iii. Tecnologias utilizadas

| Camada | Tecnologias |
|---|---|
| Frontend | React, Leaflet, OpenStreetMap |
| Backend | Python, FastAPI, WebSockets, JWT, bcrypt |
| Inteligência Artificial | A\* e CSP implementados em Python; OSMnx, usado apenas para exportar o grafo de estradas |
| Base de dados | PostgreSQL, CloudNativePG |
| Infraestrutura | Docker, Kubernetes (k3s), Traefik, Azure for Students; Docker Compose como plano alternativo |

### iv. Estrutura da equipa

| Elemento | Responsabilidade principal |
|---|---|
| Pedro António | Arquitetura distribuída, infraestrutura Kubernetes, tolerância a faltas |
| Mateus Reis | [Responsabilidade] |
| Francisco Abecasis | [Responsabilidade] |
| Deolindo Soares | [Responsabilidade] |

## e. Resultados

### i. Descrição da solução desenvolvida

Na 1.ª entrega foi concebida a solução completa. O fluxo principal é o seguinte:

1. O operador regista a ocorrência num formulário.
2. A API grava-a na base de dados primária, que a copia para a réplica antes de confirmar.
3. O A\* calcula os tempos de chegada e o CSP escolhe o meio.
4. A atribuição é gravada só se o meio ainda estiver livre.
5. Todas as réplicas da API são avisadas e enviam a missão, por WebSocket, ao operador e à unidade.

| Componente | Réplicas |
|---|---|
| Ingress (Traefik) | 2 |
| Frontend (React + Leaflet) | 2 |
| API (FastAPI) | 3 |
| PostgreSQL | 1 primária + 1 réplica síncrona |

### ii. Funcionalidades principais

- Registo de ocorrências com nível de gravidade (5 níveis).
- Atribuição automática do meio (CSP + A\*), com desempate por gravidade, por quem perde mais sem o meio e por ordem de chegada.
- Reatribuição de meios para ocorrências mais graves e recurso a distritos vizinhos.
- Mapa em tempo real para o operador; missão e rota no telemóvel da unidade.
- Gestão de distritos, meios e utilizadores, e consulta da auditoria pelo administrador.
- Tolerância à falha de uma máquina, sem perda de ocorrências confirmadas.

### iii. Contributos relevantes

- Integração de IA (A\* e CSP) com uma arquitetura distribuída num problema real de despacho.
- Garantia de consistência na atribuição concorrente através da própria base de dados, sem componentes adicionais.
- Modelo de faltas explícito, com cenários de falha a demonstrar e a medir.
- Solução independente do país, com a divisão regional tratada como dados.

## f. Reflexão

### i. Lições aprendidas

- A solução mais simples que cumpre os requisitos é a mais robusta. A versão inicial previa eleição de líder e fila de mensagens; a versão final dispensa ambos, porque a base de dados replicada já garante a consistência e cada componente a menos é um ponto de falha a menos.
- Separar claramente máquinas (nós do cluster), réplicas (cópias de cada componente) e distritos (dados) foi essencial para desenhar uma arquitetura correta.
- Definir o modelo de faltas cedo obriga a pensar no que acontece em cada falha, e não apenas no funcionamento normal.

### ii. Limitações

- O cluster tem um único *control plane*.
- O sistema não suporta a falha simultânea de duas máquinas.
- O A\* usa velocidades fixas por tipo de estrada, sem dados de trânsito.
- Em sobrecarga, ocorrências pouco graves podem aguardar mais tempo, por opção de prioridade.
- O tráfego dentro do cluster não é cifrado.

### iii. Trabalho futuro

- Integrar dados de trânsito em tempo real nos pesos do grafo de estradas.
- Distribuir as máquinas por vários centros de dados, para tolerar a falha de um local inteiro.
- Suportar mais do que uma falha simultânea, com mais réplicas e *control plane* replicado.
- Alertar o operador quando uma ocorrência ultrapassa o tempo-alvo do seu nível de gravidade.
