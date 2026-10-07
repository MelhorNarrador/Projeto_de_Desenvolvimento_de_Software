# [NOME] – Sistema Distribuído de Despacho de Emergências

**Universidade Europeia / IADE – Engenharia Informática**  
**Projeto Multidisciplinar – 5º semestre (2026/2027)**  
**Grupo 08**  
**Elementos do Grupo**: Pedro António (20241273), Mateus Reis (20241799), Francisco Abecasis (20240120), Deolindo Soares (20221446)

**Docentes**: Rui Pascoal / Miguel Boavida (Projeto de Desenvolvimento de Software), Pedro Rosa (Sistemas Distribuídos), Samuel Gomes (Inteligência Artificial), Rui Ramos (Engenharia de Software), Sérgio Nunes / Pedro Brandão (Segurança Informática)

**GitHub**: [Repositório GitHub](LINK_GITHUB)  
**ClickUp**: [Espaço ClickUp](LINK_CLICKUP)  
**Discord**: [Servidor do Grupo](LINK_DISCORD)

---

![Logo do [NOME]](imgs/logo.png)

---

## Palavras-chave
sistemas distribuídos, tolerância a faltas, despacho de emergências, Kubernetes, replicação, problemas de satisfação de restrições, A*, tempo real

---

## 1. Introdução

Este relatório apresenta a primeira versão do projeto **[NOME]**, desenvolvido no âmbito do projeto multidisciplinar do 5.º semestre da Licenciatura em Engenharia Informática, que integra as unidades curriculares de Projeto de Desenvolvimento de Software, Sistemas Distribuídos, Inteligência Artificial, Engenharia de Software e Segurança Informática.

O **[NOME]** é uma plataforma web de despacho de emergências que recebe ocorrências (emergências médicas, incêndios, acidentes), acompanha em tempo real a posição e o estado das unidades de socorro e **atribui automaticamente a unidade mais adequada a cada ocorrência**, calculando a rota mais rápida até ao local.

Por se tratar de um sistema crítico, a plataforma é construída sobre uma **arquitetura distribuída e tolerante a faltas**: todos os componentes estão replicados, e a falha de um servidor, de uma réplica da base de dados ou de uma máquina inteira não interrompe o serviço nem provoca a perda de ocorrências.

Esta primeira entrega centra-se na **conceção do sistema**: definição do problema, requisitos, arquitetura distribuída, **modelo de faltas**, componentes de IA e segurança, e planeamento do desenvolvimento.

---

## 2. Metodologia

O projeto segue uma **metodologia ágil**, com sprints de duas semanas alinhados com as três entregas do semestre. Cada tarefa é registada como **issue no GitHub**, e cada contribuição é integrada através de **pull request** revisto por outro elemento do grupo, o que garante rastreabilidade do trabalho realizado.

| Fase | Período | Entregáveis |
|---|---|---|
| **Fase 1 – Conceção** | até 11/10/2026 | Problema, requisitos, arquitetura, modelo de faltas, relatório v1 |
| **Fase 2 – Protótipo** | 12/10 a 15/11/2026 | Cluster Kubernetes, backend replicado, CSP e A* funcionais, relatório v2 |
| **Fase 3 – Consolidação** | 16/11 a 20/12/2026 | Frontend completo, segurança, testes de falha, demonstração, relatório final |

Este relatório corresponde aos entregáveis da Fase 1.

### 2.1 Estrutura da Equipa

| Elemento | Responsabilidade principal |
|---|---|
| Pedro António | Arquitetura distribuída, infraestrutura Kubernetes, tolerância a faltas |
| Mateus Reis | [Responsabilidade] |
| Francisco Abecasis | [Responsabilidade] |
| Deolindo Soares | [Responsabilidade] |

---

## 3. Descrição e Problema

Numa emergência, o tempo até à chegada do socorro é determinante. Em situações como uma paragem cardiorrespiratória, cada minuto de atraso reduz de forma significativa as hipóteses de sobrevivência, e parte desse tempo é gasto **antes de a unidade sair**: a decidir que meio enviar e por onde.

Em muitos cenários esta decisão depende do operador, que escolhe a unidade com base na experiência e numa lista de meios disponíveis. Esta abordagem apresenta três problemas:

| Problema | Consequência |
|---|---|
| O operador não sabe com exatidão **quanto tempo** cada unidade demora a chegar | A unidade mais próxima em linha reta pode não ser a mais rápida pelas ruas |
| As ocorrências são tratadas por **ordem de chegada** | Uma ocorrência leve pode ficar com a unidade de que uma ocorrência crítica vai precisar logo a seguir |
| Não existe **visão do conjunto** | Uma zona pode ficar sem unidades disponíveis sem que ninguém se aperceba |

A estes problemas soma-se um requisito técnico: uma central de emergência **não pode parar**. Se o servidor que a suporta falhar, as ocorrências deixam de ser registadas e atribuídas. Um sistema centralizado num único servidor representa um ponto único de falha inaceitável neste contexto.

O **[NOME]** pretende resolver ambos os problemas: **decidir melhor**, através de Inteligência Artificial, e **nunca parar**, através de uma arquitetura distribuída e tolerante a faltas.

---

## 4. Objetivos & Motivação

### 4.1 Objetivos

- Desenvolver uma plataforma web responsiva de despacho de emergências.
- Registar ocorrências e acompanhar unidades de socorro num mapa em tempo real.
- Atribuir automaticamente unidades a ocorrências através de um **CSP**, com reatribuição quando surge uma ocorrência mais grave.
- Calcular rotas pela rede de estradas real através do algoritmo **A\***.
- Garantir que **nenhuma ocorrência confirmada é perdida**, mesmo perante a falha de componentes.
- Manter o serviço disponível perante a falha de qualquer componente individual ou de uma máquina inteira.
- Demonstrar experimentalmente a tolerância a faltas através de testes de falha.

### 4.2 Motivação

Os sistemas de despacho são um exemplo claro de sistema onde a **distribuição é requerida** e não opcional: a disponibilidade e a integridade dos dados têm impacto direto na vida das pessoas. Este contexto permite trabalhar, de forma justificada, todos os conceitos centrais de sistemas distribuídos (replicação, consistência, deteção de falhas e recuperação), ao mesmo tempo que oferece problemas reais para os algoritmos de IA lecionados.

---

## 5. Atores

| Ator | Descrição | Necessidade principal |
|---|---|---|
| **Operador da central** | Recebe chamadas e regista ocorrências; supervisiona o estado de todas as unidades | Ver rapidamente que unidade enviar e confirmar a atribuição |
| **Unidade de socorro** | Tripulação de ambulância, bombeiros ou polícia | Receber a missão, a rota e atualizar o seu estado (a caminho, no local, disponível) |
| **Administrador** | Gere utilizadores, unidades e bases | Configurar o sistema e consultar o registo de auditoria |
| **Simulador** (sistema externo) | Gera ocorrências e movimenta unidades para testes e demonstração | Enviar dados através da API como um cliente real |

---

## 6. Estado da Arte

Os sistemas de despacho assistido por computador (**CAD – Computer-Aided Dispatch**) são utilizados por serviços de emergência em todo o mundo. Em Portugal, as chamadas de emergência médica são encaminhadas para os **CODU** (Centros de Orientação de Doentes Urgentes) do INEM.

| Solução | Pontos fortes | Limitações | Oportunidade para o [NOME] |
|---|---|---|---|
| **Sistemas CAD comerciais** | Completos, integrados com comunicações rádio e telefone | Soluções proprietárias, de custo elevado e pouco transparentes | Demonstrar os mecanismos de decisão e de tolerância a faltas de forma aberta |
| **Despacho manual com mapa** | Simples, controlado pelo operador | Decisão dependente da experiência; sem estimativa de tempos reais | Proposta automática baseada em tempos de chegada calculados |
| **Atribuição pela unidade mais próxima** | Rápida e fácil de implementar | Decisão isolada por ocorrência; ignora prioridades e cobertura | Decisão conjunta de várias ocorrências, com reatribuição por prioridade |

O **[NOME]** diferencia-se por combinar, num só sistema:

1. **Atribuição otimizada** de várias ocorrências em simultâneo, com restrições explícitas (CSP).
2. **Reatribuição dinâmica** de unidades em trânsito quando surge uma ocorrência mais grave.
3. **Tempos de chegada reais**, calculados pela rede de estradas (A*).
4. **Tolerância a faltas demonstrável**, com garantias explícitas sobre disponibilidade e perda de dados.

---

## 7. Requisitos

### 7.1 Requisitos Funcionais

| ID | Requisito |
|---|---|
| RF01 | Autenticação de utilizadores com perfis de operador, unidade e administrador |
| RF02 | Registo de ocorrências com tipo, localização, prioridade e meios necessários |
| RF03 | Visualização de ocorrências e unidades num mapa em tempo real |
| RF04 | Atribuição automática de unidades a ocorrências (CSP), com confirmação pelo operador |
| RF05 | Reatribuição de unidades em trânsito quando surge uma ocorrência de prioridade superior |
| RF06 | Cálculo e apresentação da rota mais rápida até à ocorrência (A*) |
| RF07 | Vista da unidade: receber missão, ver rota e atualizar estado |
| RF08 | Atualização periódica da posição das unidades |
| RF09 | Gestão de unidades, bases e utilizadores (administrador) |
| RF10 | Registo de auditoria de todas as atribuições e alterações relevantes |
| RF11 | Simulador de ocorrências e de movimento de unidades |

### 7.2 Requisitos Não Funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF01 | Disponibilidade | O serviço mantém-se disponível perante a falha de qualquer componente individual ou de uma máquina do cluster |
| RNF02 | Durabilidade | Nenhuma ocorrência confirmada ao operador é perdida |
| RNF03 | Consistência | Uma unidade nunca está atribuída a duas ocorrências ao mesmo tempo |
| RNF04 | Desempenho | A proposta de atribuição é apresentada em menos de 2 segundos após o registo da ocorrência |
| RNF05 | Tempo real | Alterações de estado chegam ao mapa dos operadores em menos de 1 segundo |
| RNF06 | Recuperação | Após a falha de um componente, a redundância é reposta automaticamente |
| RNF07 | Segurança | Toda a comunicação externa é cifrada (HTTPS) e o acesso é controlado por perfil |
| RNF08 | Rastreabilidade | Todas as decisões de atribuição ficam registadas com autor e data |
| RNF09 | Usabilidade | Interface responsiva, utilizável em computador e no telemóvel da unidade |

### 7.3 Casos de Uso

| ID | Caso de uso | Ator | RF |
|---|---|---|---|
| UC01 | Autenticar-se | Todos | RF01 |
| UC02 | Registar ocorrência | Operador | RF02 |
| UC03 | Confirmar atribuição proposta | Operador | RF04 |
| UC04 | Acompanhar ocorrências e unidades no mapa | Operador | RF03 |
| UC05 | Receber missão e rota | Unidade | RF06, RF07 |
| UC06 | Atualizar estado da unidade | Unidade | RF07 |
| UC07 | Gerir unidades e utilizadores | Administrador | RF09 |
| UC08 | Consultar auditoria | Administrador | RF10 |

![Diagrama de Casos de Uso](imgs/uml_casos_de_uso.png)

### 7.4 Modelo de Domínio

| Entidade | Atributos principais | Relações |
|---|---|---|
| **Utilizador** | id, nome, email, hash da palavra-passe, perfil | Pode estar associado a uma Unidade |
| **Unidade** | id, tipo, nível de suporte, estado, posição, base | Pertence a uma Base; tem 0..1 Atribuição ativa |
| **Base** | id, nome, localização | Tem várias Unidades |
| **Ocorrência** | id, tipo, prioridade, localização, estado, meios necessários, data | Tem várias Atribuições |
| **Atribuição** | id, ocorrência, unidade, estado, tempo estimado, data | Liga Ocorrência e Unidade |
| **Registo de auditoria** | id, utilizador, ação, entidade, data | Referencia Utilizador |

![Modelo de Domínio](imgs/uml_dominio.png)

---

## 8. Arquitetura Distribuída

### 8.1 Visão Geral

O sistema corre num cluster **Kubernetes (k3s)** com **três nós**, cada um numa máquina virtual distinta. Todos os nós executam serviços aplicacionais, e os componentes replicados são distribuídos por nós diferentes (*anti-affinity*), de forma a que a perda de uma máquina não elimine todas as réplicas de um componente.

![Diagrama de Arquitetura](imgs/arquitetura.png)

### 8.2 Componentes

| Camada | Componente | Função | Réplicas | Mecanismo de redundância |
|---|---|---|---|---|
| Entrada | **Ingress (Traefik)** | Ponto de entrada HTTPS; encaminha pedidos para o frontend e a API | 2 | Exposto em todos os nós; pods em nós diferentes |
| Cliente | **Frontend** (React + Leaflet) | Interface web responsiva | 2 | `Deployment` com 2 réplicas |
| Serviços | **API** (FastAPI) | Autenticação, ocorrências, rotas (A*), WebSockets | 3 | `Deployment` stateless; `Service` distribui os pedidos |
| Serviços | **Workers de despacho** | Consomem ocorrências da fila e executam o CSP | 2 | Consumo competitivo da fila; *ack* apenas após gravar a atribuição |
| Mensagens | **RabbitMQ** | Fila de ocorrências e difusão de eventos em tempo real | 3 | **Quorum queues** (replicação por consenso Raft), gerido pelo RabbitMQ Cluster Operator |
| Dados | **PostgreSQL** | Ocorrências, unidades, atribuições, utilizadores, auditoria | 1 primária + 2 réplicas | **CloudNativePG**: replicação em streaming, réplica síncrona e failover automático |
| Testes | **Simulador** | Gera ocorrências e movimento de unidades | 1 | Não crítico |

### 8.3 Fluxo Principal

| # | Passo |
|---|---|
| 1 | O operador regista a ocorrência; o pedido chega a qualquer instância da API |
| 2 | A API grava a ocorrência na BD e publica-a na fila replicada; só responde ao operador depois de ambas as operações estarem confirmadas |
| 3 | Um worker consome a ocorrência e executa o CSP, usando os tempos de chegada calculados pelo A* |
| 4 | O worker grava a atribuição numa transação que verifica se a unidade continua disponível, e só depois confirma (*ack*) a mensagem |
| 5 | O worker publica um evento de atribuição numa *exchange* de difusão |
| 6 | Todas as instâncias da API recebem o evento e enviam-no por WebSocket aos seus clientes (operadores e unidade) |

O passo 6 resolve um problema próprio da distribuição: como os clientes estão ligados a instâncias diferentes da API, um evento produzido numa instância tem de chegar a todas. A difusão através do RabbitMQ garante que todos os operadores veem o mesmo estado, independentemente da instância a que estão ligados.

### 8.4 Decisões Arquiteturais

| Decisão | Justificação |
|---|---|
| **Kubernetes** em vez de Docker Compose | Recria automaticamente componentes que falham, distribui réplicas por várias máquinas e oferece deteção de falhas nativa (*probes*) |
| **API stateless** com autenticação **JWT** | Qualquer instância atende qualquer pedido; a falha de uma instância não termina sessões |
| **Fila replicada** entre a API e os workers | Desacopla a receção do processamento; uma ocorrência aceite fica guardada mesmo que nenhum worker esteja disponível |
| **Quorum queues** | Mantêm as mensagens com a falha de 1 de 3 nós; consistência garantida por consenso |
| **Réplica síncrona** no PostgreSQL | Uma transação só é confirmada depois de existir também na réplica, pelo que o failover não perde dados confirmados |
| **Consistência forte** nas atribuições | Atribuir a mesma unidade a duas ocorrências é inaceitável; prefere-se rejeitar e recalcular do que aceitar um conflito |
| **Processamento idempotente** | A fila garante entrega *pelo menos uma vez*; os workers verificam se a ocorrência já foi atribuída antes de a processar novamente |

---

## 9. Modelo de Faltas

| Questão | Resposta |
|---|---|
| **Componentes que podem falhar** | Pods da API, workers, frontend e ingress; nós do RabbitMQ; instância primária ou réplica do PostgreSQL; uma máquina inteira do cluster; ligação de rede de um cliente |
| **Tipos de falha considerados** | Falha por paragem (*crash*): o componente deixa de responder. Interrupção temporária de comunicação. **Não são consideradas** falhas bizantinas (componentes com comportamento malicioso ou arbitrário) |
| **Falhas simultâneas suportadas** | A falha de **uma máquina do cluster** (e de todos os pods que nela correm), ou a falha simultânea de um pod de cada componente |
| **Funcionalidades disponíveis após a falha** | Todas: registo de ocorrências, atribuição, rotas, mapa em tempo real e vista das unidades |
| **Deteção da falha** | *Liveness* e *readiness probes* do Kubernetes nos pods; estado *NotReady* dos nós por ausência de *heartbeat*; eleição de líder Raft no RabbitMQ; monitorização da primária pelo CloudNativePG |
| **Recuperação ou substituição** | O Kubernetes recria os pods em falha (noutro nó, se necessário); o tráfego deixa de ser enviado para pods não prontos; mensagens sem *ack* são reentregues a outro worker; o CloudNativePG promove uma réplica a primária |
| **Informação que pode ser perdida** | Nenhuma ocorrência ou atribuição **confirmada**. Pedidos em curso no momento da falha podem falhar e ser repetidos pelo cliente. A última atualização de posição de uma unidade (alguns segundos) pode perder-se, sendo substituída pela seguinte |
| **Consistência entre réplicas** | RabbitMQ: escrita confirmada por maioria (Raft). PostgreSQL: *commit* síncrono para uma réplica. Atribuições: transação com verificação de disponibilidade da unidade, com recálculo do CSP em caso de conflito |

### 9.1 Limitações Assumidas

| Limitação | Impacto |
|---|---|
| O cluster tem um único nó de *control plane* | Se esse nó falhar, os serviços em execução continuam a funcionar, mas o cluster deixa de recriar pods e de promover réplicas até ser recuperado |
| Falha de duas máquinas em simultâneo | O RabbitMQ perde o quórum e deixa de aceitar ocorrências; o sistema não garante disponibilidade neste cenário |
| Réplica síncrona indisponível | O PostgreSQL passa a confirmar escritas apenas na primária para não bloquear o serviço, o que reduz temporariamente a garantia de durabilidade |
| Tempo de deteção da falha de um nó | Por omissão, o Kubernetes demora vários minutos a mover pods de um nó perdido; estes tempos serão reduzidos na configuração e medidos nos testes |

---

## 10. Cenários de Demonstração de Falhas

| # | Componente que falha | Deteção | Mecanismo que mantém o serviço | Impacto nos utilizadores | Perda de dados | Recuperação | Reposição da redundância |
|---|---|---|---|---|---|---|---|
| F1 | Pod da API | *Liveness probe* | `Service` envia pedidos às restantes instâncias | WebSockets da instância caída reconectam automaticamente | Nenhuma | Pod recriado pelo Kubernetes | Volta a 3 réplicas automaticamente |
| F2 | Worker a meio de uma atribuição | Ligação ao RabbitMQ fechada | Mensagem sem *ack* volta à fila e é processada por outro worker | Atribuição atrasa alguns segundos | Nenhuma (processamento idempotente) | Pod recriado | Volta a 2 réplicas |
| F3 | Nó do RabbitMQ | Eleição de líder Raft | Os 2 nós restantes mantêm o quórum | Nenhum | Nenhuma | Pod recriado pelo operador | O nó sincroniza as filas ao voltar |
| F4 | PostgreSQL primária | CloudNativePG | Réplica síncrona promovida a primária | Escritas falham durante alguns segundos | Nenhuma transação confirmada | Antiga primária volta como réplica | Nova réplica sincronizada |
| F5 | Máquina inteira do cluster | Nó passa a *NotReady* | Réplicas nos outros nós continuam a servir | Breve degradação durante a reorganização | Nenhuma confirmada | Pods recriados nos nós restantes | Ao voltar, o nó recebe novamente pods |
| F6 | Ligação de rede de uma unidade | Falha de envio no cliente | Cliente guarda as atualizações localmente | Posição da unidade desatualizada temporariamente | Nenhuma | Cliente reenvia ao recuperar a ligação | Não aplicável |

Para cada cenário serão registados os **tempos de deteção e de recuperação** e verificada a integridade dos dados após a falha, através de testes automatizados que geram carga contínua durante a injeção de falhas.

---

## 11. Componente de Inteligência Artificial

A IA resolve dois problemas, ambos implementados pelo grupo, sem recurso a serviços externos.

### 11.1 Atribuição de Unidades – CSP

| Elemento | Descrição |
|---|---|
| **Variáveis** | Uma por meio necessário em cada ocorrência pendente |
| **Domínios** | Unidades do tipo certo disponíveis ou desviáveis, mais o valor *em espera* |
| **Restrições obrigatórias** | Unicidade da unidade, tipo de unidade, nível de suporte, disponibilidade, desvio apenas para prioridade superior |
| **Preferências (custo)** | Tempo de chegada ponderado pela prioridade, não usar meios avançados em ocorrências leves, manter cobertura do território, evitar desvios |
| **Resolução** | Backtracking com MRV, LCV e *branch and bound* |

As ocorrências que chegam numa janela curta (por exemplo, 5 segundos) são resolvidas em conjunto, evitando as más decisões de uma atribuição por ordem de chegada.

### 11.2 Cálculo de Rotas – A*

| Elemento | Descrição |
|---|---|
| **Grafo** | Rede de estradas da região, obtida do OpenStreetMap |
| **Custo** | Tempo de viagem de cada troço (comprimento ÷ velocidade máxima) |
| **Heurística** | Distância em linha reta ÷ velocidade máxima da rede (admissível) |
| **Utilização** | Tempos de chegada para o CSP e rota apresentada no mapa |

A descrição completa encontra-se no documento da componente de IA entregue à respetiva unidade curricular.

---

## 12. Segurança

| Área | Medida |
|---|---|
| **Autenticação** | Palavras-passe guardadas com *hash* (bcrypt/Argon2); tokens **JWT** de curta duração com *refresh token* |
| **Autorização** | Controlo de acesso por perfil (operador, unidade, administrador) em cada endpoint |
| **Comunicação** | HTTPS no ingress; WebSockets sobre TLS (WSS) |
| **Segredos** | Chaves e credenciais guardadas em *Secrets* do Kubernetes, nunca no repositório |
| **Isolamento** | *NetworkPolicies*: a base de dados e o RabbitMQ só aceitam ligações da API e dos workers |
| **Auditoria** | Registo de todas as atribuições, reatribuições e alterações administrativas, com utilizador e data |
| **Proteção da API** | Validação de todos os dados de entrada; limitação do número de pedidos (*rate limiting*) |

---

## 13. Tecnologias a Utilizar

| Camada | Tecnologias |
|---|---|
| **Frontend** | React, Leaflet, OpenStreetMap, WebSockets |
| **Backend** | Python, FastAPI |
| **Inteligência Artificial** | Python (implementação própria de CSP e A*), OSMnx (obtenção do grafo de estradas) |
| **Mensagens** | RabbitMQ (quorum queues), RabbitMQ Cluster Operator |
| **Base de Dados** | PostgreSQL, CloudNativePG |
| **Infraestrutura** | Docker (imagens), Kubernetes (k3s), Traefik, Azure for Students (máquinas virtuais) |
| **Ferramentas** | GitHub, VSCode, Postman, ClickUp, Discord, draw.io |

---

## 14. Guiões de Teste

### Guião 1 – Registar e atribuir ocorrência (Core)

1. O operador autentica-se na plataforma.
2. Regista uma ocorrência médica crítica, indicando a localização no mapa.
3. O sistema propõe a ambulância de suporte avançado com menor tempo de chegada.
4. O operador confirma a atribuição.
5. A rota aparece no mapa do operador e na vista da unidade.

**Resultado esperado**: A ocorrência é atribuída em menos de 2 segundos e ambos os utilizadores veem a rota.

### Guião 2 – Reatribuição por prioridade

1. Uma ambulância está a caminho de uma ocorrência não urgente.
2. É registada uma ocorrência crítica próxima, sem outra unidade adequada disponível.
3. O sistema propõe desviar a ambulância para a ocorrência crítica.
4. A ocorrência não urgente volta ao estado *em espera* ou recebe outra unidade.

**Resultado esperado**: A unidade é desviada e a ocorrência original não fica esquecida.

### Guião 3 – Atualização de estado pela unidade

1. A tripulação abre a vista da unidade no telemóvel.
2. Aceita a missão e marca "a caminho", depois "no local" e por fim "disponível".
3. O operador vê cada mudança de estado no mapa.

**Resultado esperado**: As alterações chegam ao operador em menos de 1 segundo.

### Guião 4 – Falha durante o funcionamento

1. O simulador gera ocorrências de forma contínua.
2. É eliminado um pod da API e, de seguida, a instância primária do PostgreSQL.
3. Verifica-se o número de ocorrências geradas, registadas e atribuídas.

**Resultado esperado**: O serviço continua disponível, todas as ocorrências confirmadas estão registadas e a redundância é reposta automaticamente (ver secção 10).

---

## 15. Planeamento

### 15.1 Sprints

| Sprint | Período | Objetivos |
|---|---|---|
| 1 | 28/09 – 11/10 | Conceção, requisitos, arquitetura, modelo de faltas, relatório v1 |
| 2 | 12/10 – 25/10 | Cluster k3s, PostgreSQL e RabbitMQ replicados, estrutura da API |
| 3 | 26/10 – 08/11 | A* e grafo de estradas, CSP, workers, simulador |
| 4 | 09/11 – 15/11 | Integração, primeiros testes de falha, relatório v2 |
| 5 | 16/11 – 29/11 | Frontend completo, WebSockets, vista da unidade |
| 6 | 30/11 – 13/12 | Segurança, reatribuição, testes de falha automatizados, métricas |
| 7 | 14/12 – 20/12 | Demonstração final, documentação, arquivo documental |

### 15.2 Gráfico de Gantt e WBS

**Gantt**: [Gráfico de Gantt e WBS](LINK_GANTT)

![Gantt do Projeto](imgs/gantt.png)

### 15.3 Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Complexidade do Kubernetes atrasa o projeto | Média | Alto | Imagens Docker desenvolvidas desde o início; **plano alternativo com Docker Compose** mantendo a mesma arquitetura replicada |
| Grafo de estradas demasiado grande para o A* | Média | Médio | Limitar a região da demonstração (ex.: Lisboa) |
| CSP lento com muitas ocorrências | Baixa | Médio | Janelas curtas, tempo limite e devolução da melhor solução encontrada |
| Limite de créditos na cloud | Baixa | Médio | Desenvolvimento local (k3d); VMs ligadas apenas para testes e demonstração |

---

## 16. Conclusão

O **[NOME]** pretende demonstrar como uma arquitetura distribuída e tolerante a faltas, combinada com algoritmos de Inteligência Artificial, pode suportar um sistema crítico como uma central de despacho de emergências.

Nesta primeira fase foram definidos o problema, os requisitos, a arquitetura distribuída, o modelo de faltas e os cenários de falha a demonstrar. Na **2.ª entrega** será desenvolvido um protótipo funcional com:

- Cluster Kubernetes com PostgreSQL e RabbitMQ replicados;
- API replicada com registo de ocorrências;
- Implementação do A* sobre o grafo de estradas e do CSP de atribuição;
- Primeiros testes de falha.

---

## 17. Bibliografia

[1] Kubernetes Documentation – https://kubernetes.io/docs  
[2] K3s Documentation – https://docs.k3s.io  
[3] RabbitMQ – Quorum Queues – https://www.rabbitmq.com/docs/quorum-queues  
[4] CloudNativePG Documentation – https://cloudnative-pg.io/documentation  
[5] FastAPI Documentation – https://fastapi.tiangolo.com  
[6] OpenStreetMap – https://www.openstreetmap.org  
[7] Leaflet – https://leafletjs.com  
[8] Boeing, G. (2017). *OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks*. Computers, Environment and Urban Systems, 65, 126–139.  
[9] Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4.ª ed.). Pearson.  
[10] Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2011). *Distributed Systems: Concepts and Design* (5.ª ed.). Addison-Wesley.  
[11] INEM – Instituto Nacional de Emergência Médica – https://www.inem.pt
