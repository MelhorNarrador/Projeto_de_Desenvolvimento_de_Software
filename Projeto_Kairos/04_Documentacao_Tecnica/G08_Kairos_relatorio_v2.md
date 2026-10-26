# Memória Descritiva — Kairós

**Sistema Distribuído de Despacho de Emergências**  
**Projeto Multidisciplinar - 5º semestre (2026/2027)**  
**Grupo 08**  
**Elementos:** Pedro António - 20241273, Mateus Reis - 20241799, Francisco Abecasis - 20240120, Deolindo Soares - 20221446  
**Palavras-chave:** sistemas distribuídos, tolerância a faltas, despacho de emergências, Kubernetes, replicação, problemas de satisfação de restrições, A*, tempo real

---

## 1. Introdução
Este relatório apresenta a segunda versão do projeto Kairos, desenvolvido no âmbito do projeto multidisciplinar de 5.º semestre da Licenciatura em Engenharia Informática.

A Kairos é uma plataforma web de despacho de emergências que recebe ocorrências (emergências médicas, incêndios, acidentes), acompanha em tempo real a posição e o estado das unidades de socorro e atribui automaticamente a unidade mais adequada a cada ocorrência, calculando a rota mais rápida até ao local.

Por se tratar de um sistema crítico, a plataforma é construída sobre uma arquitetura distribuída e tolerante a faltas: todos os componentes estão replicados, e a falha de um servidor, de uma réplica da base de dados ou de uma máquina inteira não interrompe o serviço nem provoca a perda de ocorrências.

Esta segunda entrega (Protótipo) foca-se na implementação técnica do sistema: desenvolvimento do cluster na cloud, interfaces do operador e tripulação, integração contínua (CI/CD) e execução dos primeiros testes de falha para validação da tolerância a faltas.

## 2. Metodologia
O projeto segue uma metodologia ágil baseada em Kanban. O trabalho flui de forma contínua por um quadro de tarefas, em vez de ser organizado em ciclos fechados, o que se adapta melhor a uma equipa com disponibilidades variáveis ao longo do semestre. Para garantir o cumprimento das três entregas, o quadro é complementado por milestones com datas fixas. 

O quadro é gerido no Trello o que garante a rastreabilidade de todo o trabalho realizado.

### 2.1 Quadro Kanban
| Coluna | Significado |
|---|---|
| **Backlog** | Tarefas identificadas, ainda não priorizadas |
| **To Do** | Tarefas priorizadas para o marco atual, prontas a ser iniciadas |
| **Doing** | Tarefas em desenvolvimento, com um responsável atribuído |
| **Blocked** | Tarefa bloqueada, espera por ajuda de outro elemento ou finalização de outra tarefa |
| **In Review** | Tarefa concluída, espera por testes e revisão por outro elemento |
| **Done** | Tarefa revista e integrada no ramo principal |

### 2.2 Regras de Trabalho
| Regra | Descrição |
|---|---|
| **Limite de trabalho em curso (WIP)** | Cada elemento tem no máximo 2 tarefas em "Doing" em simultâneo |
| **Uma tarefa, um cartão** | Todo o trabalho é registado como cartões no Trello, com responsável e etiquetas |
| **Definição de Done** | Uma tarefa só passa a "Done" quando o código ou documento está revisto, integrado e testado |
| **Ponto de situação semanal** | Reunião curta com o quadro como base: o que avançou, o que está bloqueado e o que se segue |

### 2.3 Etiquetas
| Tipo | Etiquetas |
|---|---|
| **Natureza da tarefa** | feature, bug, docs, teste |
| **Prioridade** | alta, média, baixa |

### 2.4 Marcos (Milestones)
| Marco | Data | Objetivo |
|---|---|---|
| **Entrega 1 – Conceção** | 11/10/2026 | Problema, requisitos, arquitetura, modelo de faltas, relatório v1 |
| **Entrega 2 – Protótipo** | 15/11/2026 | Infraestrutura cloud, frontend e API funcionais, testes de falha, relatório v2 |
| **Entrega 3 – Versão final** | 20/12/2026 | Segurança completa, testes automatizados, demonstração, relatório final |

Cada marco agrupa os cartões que têm de estar concluídos até à respetiva data. *Este relatório corresponde ao marco Entrega 2 – Protótipo.*

## 3. Descrição e Problema
Numa emergência, o tempo até à chegada do socorro é determinante. Em situações como uma paragem cardiorrespiratória, cada minuto de atraso reduz de forma significativa as hipóteses de sobrevivência, e parte desse tempo é gasto antes de a unidade sair a decidir que meio enviar e por onde.

Em muitos cenários esta decisão depende do operador, que escolhe a unidade com base na experiência e numa lista de meios disponíveis. Esta abordagem apresenta três problemas:

| Problema | Consequência |
|---|---|
| **O operador não sabe com exatidão quanto tempo cada unidade demora a chegar** | A unidade mais próxima em linha reta pode não ser a mais rápida pelas ruas |
| **As ocorrências são tratadas por ordem de chegada** | Uma ocorrência leve pode ficar com a unidade de que uma ocorrência crítica vai precisar logo a seguir |
| **Não existe visão do conjunto** | Uma zona pode ficar sem unidades disponíveis sem que ninguém se aperceba |

A Kairos pretende resolver ambos os problemas: decidir melhor, através de algoritmos, e nunca parar, através de uma arquitetura distribuída e tolerante a faltas.

## 4. Objetivos & Motivação

### 4.1 Objetivos
* Desenvolver uma plataforma web responsiva de despacho de emergências.
* Registar ocorrências e acompanhar unidades de socorro num mapa em tempo real.
* Atribuir automaticamente unidades a ocorrências, com reatribuição quando surge uma ocorrência mais grave.
* Calcular rotas pela rede de estradas real através do algoritmo A*.
* Garantir que nenhuma ocorrência confirmada é perdida, mesmo perante a falha de componentes.
* Manter o serviço disponível perante a falha de qualquer componente individual ou de uma máquina inteira.

### 4.2 Motivação
Os sistemas de despacho são um exemplo claro de sistema onde a distribuição é necessária, a disponibilidade e a integridade dos dados têm impacto direto na vida das pessoas. Este contexto permite trabalhar todos os conceitos centrais de sistemas distribuídos (replicação, consistência, deteção de falhas e recuperação).

## 5. Atores
| Ator | Descrição | Necessidade principal |
|---|---|---|
| **Operador da central** | Recebe chamadas e regista ocorrências | Ver rapidamente que unidade enviar e confirmar a atribuição |
| **Unidade de socorro** | Tripulação de ambulância, bombeiros ou polícia | Receber a missão, a rota e atualizar o seu estado (a caminho, no local, disponível) |
| **Administrador** | Gere utilizadores, unidades e bases | Configurar o sistema e consultar o registo de auditoria |

## 6. Pesquisa de Mercado
Os sistemas de despacho assistido por computador (CAD) são utilizados por serviços de emergência em todo o mundo. A Kairos diferencia-se por combinar, num só sistema:
1. Atribuição otimizada de várias ocorrências em simultâneo (CSP).
2. Reatribuição dinâmica de unidades em trânsito.
3. Tempos de chegada reais, calculados pela rede de estradas (A*).
4. Tolerância a faltas demonstrável, com garantias explícitas sobre disponibilidade.

## 7. Requisitos Funcionais
| ID | Requisito |
|---|---|
| **RF01** | Autenticação de utilizadores com perfis de operador, unidade e administrador |
| **RF02** | Registo de ocorrências com tipo, localização (pesquisa de moradas), descrição e gravidade |
| **RF03** | Visualização das ocorrências e unidades do distrito num mapa em tempo real |
| **RF04** | Proposta automática de atribuição de unidades |
| **RF07** | Cálculo e apresentação da rota mais rápida até à ocorrência |
| **RF08** | Vista da unidade: escolher viatura, receber missão, ver rota e atualizar estado |
| **RF09** | Atualizações automáticas de dados entre clientes |

## 8. Arquitetura Distribuída
*(Consulte o Diagrama de Arquitetura na pasta `1 Documentacao_Tecnica`)*

O sistema corre num cluster Kubernetes (k3s) com três nós, cada um numa máquina virtual distinta na cloud (Azure). Todos os nós executam serviços aplicacionais, e os componentes replicados são distribuídos por nós diferentes.

| Camada | Componente | Função | Mecanismo de redundância |
|---|---|---|---|
| **Entrada** | Ingress (Traefik) | Ponto de entrada HTTPS seguro | 2 portas de entrada em nós diferentes. |
| **Cliente** | Frontend (React + Leaflet) | Interface web responsiva | Deployment replicado |
| **Serviços** | API (FastAPI) | Lógica de negócio, WebSockets | Deployment stateless, o Service distribui pedidos |
| **Dados** | PostgreSQL | Ocorrências, unidades e atribuições | CloudNativePG com cópias síncronas em várias máquinas |

## 9. Modelo de Faltas
| Questão | Resposta |
|---|---|
| **Componentes que podem falhar** | Pods da API, do frontend e do ingress. Primária ou réplica do PostgreSQL. Uma máquina inteira do cluster na Azure. |
| **Funcionalidades após falha** | Todas: registo, rotas, mapa e vista das unidades continuam operacionais. |
| **Recuperação** | O Kubernetes recria os pods; o CloudNativePG promove a réplica da BD a primária. |
| **Perda de dados** | Nenhuma ocorrência ou atribuição confirmada é perdida (replicação síncrona). |

## 10. Cenários de Demonstração de Falhas
| # | O que falha | Deteção | O que mantém o serviço | Impacto |
|---|---|---|---|---|
| **F1** | Pod da API | Probe do k8s | As outras réplicas recebem os pedidos | WebSockets religam à réplica ativa |
| **F3** | BD primária | CloudNativePG | Réplica promovida a primária | Escritas falham durante curtos segundos, sem perda de dados |
| **F4** | Máquina inteira | Nó passa a NotReady | Réplicas nos outros nós continuam a servir | Pods recriados nos restantes nós |

## 11. Componentes Algorítmicos
* **Atribuição (CSP):** Corre periodicamente para atribuir meios às ocorrências pendentes minimizando tempos de chegada. Resolve desempates priorizando ocorrências mais graves e antigas.
* **Cálculo de Rotas (A*):** Utiliza a rede de estradas (OpenStreetMap) para calcular o caminho ótimo, cujos tempos alimentam a decisão do CSP e a rota visual no ecrã da tripulação.

---

## 15. Desenvolvimento do Protótipo (2ª Entrega)
Nesta segunda entrega, o projeto transitou da fase de conceção teórica para a implementação prática. De acordo com o roadmap planeado, foram desenvolvidas e integradas as seguintes funcionalidades e componentes:

### 15.1. Interfaces e Funcionalidades da Aplicação
* **Mapa do Operador:** Foi desenvolvido o painel interativo que permite ao operador visualizar, em tempo real, todas as ocorrências ativas e os meios do distrito.
* **Registo de Ocorrências:** Implementou-se o formulário de registo de emergências com a funcionalidade integrada de pesquisa de moradas, facilitando a submissão exata do local.
* **Ecrã da Tripulação:** Criou-se a vista dedicada às unidades de socorro. A interface permite que a equipa escolha a viatura, visualize a sua missão atribuída e acompanhe o caminho (rota) até ao local no mapa.
* **Atualizações Automáticas:** Foram integrados mecanismos de sincronização em tempo real (via WebSockets), garantindo que todos os clientes são atualizados automaticamente e em simultâneo quando o estado de uma ocorrência ou meio se altera.

### 15.2. Infraestrutura e Cloud
* **Deploy e Automação (CI/CD):** O sistema foi preparado para ser instalado automaticamente através da criação de pipelines no GitHub Actions e manifestos do Kubernetes.
* **Cluster na Cloud:** A plataforma encontra-se operacional e distribuída por 3 máquinas virtuais na cloud (Azure), utilizando a distribuição leve k3s.
* **Base de Dados Replicada:** Configurou-se a camada de dados no cluster utilizando o operador CloudNativePG, garantindo cópias da base de dados PostgreSQL em várias máquinas para suportar a tolerância a falhas.
* **Segurança de Entrada:** Implementou-se acesso seguro (HTTPS) gerido através de duas portas de entrada controladas pelo Ingress Traefik.

### 15.3. Validação e Testes
* **Testes de Falha:** Foram realizados testes provocando falhas nos nós e serviços para garantir que a arquitetura distribuída consegue recuperar automaticamente sem perda de registos críticos.

## 16. Planeamento e Roadmap

### 16.1 Detalhe de Tarefas (Sprint da 2ª Entrega)
O desenvolvimento do protótipo foi executado de acordo com o seguinte roadmap aprovado pelo grupo:

| Data Limite | # | Tarefa / Componente |
|---|---|---|
| 26/10/2026 | 1 | Mapa do operador com as ocorrências e os meios do distrito |
| 26/10/2026 | 2 | Registar uma ocorrência com pesquisa de moradas |
| 26/10/2026 | 3 | Ecrã da tripulação: escolher a viatura, ver a missão e o caminho até ao local |
| 26/10/2026 | 4 | Atualizações automáticas |
| 26/10/2026 | 5 | Preparar o sistema para ser instalado automaticamente na cloud (GitHub Actions, Kubernetes) |
| 30/10/2026 | 6 | Sistema a funcionar em 3 máquinas na cloud (Azure, k3s) |
| 30/10/2026 | 7 | Base de dados com cópias em várias máquinas (CloudNativePG) |
| 02/11/2026 | 8 | Acesso seguro e duas portas de entrada (HTTPS, Traefik) |
| 02/11/2026 | 9 | Testes de falha |
| 06/11/2026 | 10 | Relatório v2 e slides |
| 09/11/2026 | 11 | Testes finais e guião para apresentação |

## 17. Conclusão
A Kairos pretende demonstrar como uma arquitetura distribuída e tolerante a faltas, combinada com algoritmos de IA, pode suportar um sistema crítico de despacho.

Na primeira fase (Entrega 1) foram definidos os requisitos e o modelo de faltas. Nesta **segunda entrega**, provou-se a viabilidade técnica do sistema com a entrega do protótipo funcional. O desenvolvimento incluiu o mapa do operador, o ecrã da tripulação, o registo com moradas e atualizações automáticas. Do ponto de vista de infraestrutura, o sistema está a correr na cloud (Azure) num cluster k3s com CI/CD (GitHub Actions), garantindo o acesso seguro via Traefik e a persistência de dados em múltiplas máquinas via CloudNativePG.

Na 3.ª entrega, o projeto focará a finalização do frontend, testes automatizados e o fecho completo do produto para a avaliação final.

## 18. Bibliografia
* [1] Kubernetes Documentation – https://kubernetes.io/docs
* [2] K3s Documentation – https://docs.k3s.io
* [3] PostgreSQL Documentation – https://www.postgresql.org/docs
* [4] CloudNativePG Documentation – https://cloudnative-pg.io/documentation
* [5] FastAPI Documentation – https://fastapi.tiangolo.com
* [6] OpenStreetMap – https://www.openstreetmap.org
* [7] Leaflet – https://leafletjs.com
* [8] Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks.
* [9] INEM – Instituto Nacional de Emergência Médica – https://www.inem.pt
