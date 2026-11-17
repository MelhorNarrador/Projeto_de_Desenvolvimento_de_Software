# KAIRÓS - Sistema Distribuído de Despacho de Emergências



**Universidade Europeia / IADE - Engenharia Informática**

Projeto Multidisciplinar - 5º semestre (2026/2027)

**Grupo 08**



**Elementos do Grupo:**

* Deolindo Soares

* Mateus Reis

* Pedro Afonso

* Francisco Abecasis (20240120)



**GitHub:** [Repositório GitHub](#) | **Trello:** [Quadro Trello](#)



*Palavras-chave: sistemas distribuídos, tolerância a faltas, despacho de emergências, Kubernetes, replicação, problemas de satisfação de restrições, A\*, tempo real*



---



## 1. Introdução



Este relatório apresenta o projeto Kairos, desenvolvido no âmbito do projeto multidisciplinar de 5.º semestre da Licenciatura em Engenharia Informática. A Kairos é uma plataforma web de despacho de emergências que recebe ocorrências (emergências médicas, incêndios, acidentes), acompanha em tempo real a posição e o estado das unidades de socorro e atribui automaticamente a unidade mais adequada a cada ocorrência, calculando a rota mais rápida até ao local.



Por se tratar de um sistema crítico, a plataforma é construída sobre uma arquitetura distribuída e tolerante a faltas: todos os componentes estão replicados, e a falha de um servidor, de uma réplica da base de dados ou de uma máquina inteira não interrompe o serviço nem provoca a perda de ocorrências. Este documento funde a conceção inicial do sistema (requisitos, arquitetura, modelo de faltas) com o protótipo detalhado de Inteligência Artificial implementado na segunda fase do projeto.



## 2. Metodologia



O projeto segue uma metodologia ágil baseada em Kanban. O trabalho flui de forma contínua por um quadro de tarefas gerido no Trello. As regras de trabalho incluem um Limite de trabalho em curso (WIP) de 2 tarefas em "Doing" por elemento, registo integral em cartões e pontos de situação semanais. O desenvolvimento está dividido em três grandes marcos (Milestones): Conceção (E1), Protótipo IA e Cluster (E2), e Versão Final com segurança e testes de métricas (E3).



## 3. Descrição e Problema



Numa emergência, o tempo até à chegada do socorro é determinante. Em muitas centrais, a decisão de despacho depende do operador, apresentando três problemas principais:

1. O operador não sabe com exatidão o tempo real da rota pelas ruas;

2. As ocorrências são tratadas por ordem de chegada, prejudicando casos críticos;

3. Falta visão de conjunto do distrito.



A Kairos resolve estes problemas automatizando a decisão por IA e garantindo que o sistema central nunca falha perante a queda de um servidor.



## 4. Objetivos & Motivação



Os principais objetivos passam por desenvolver uma plataforma web responsiva, atribuir automaticamente unidades através de CSP, reatribuir dinamicamente perante ocorrências mais graves, calcular rotas reais através do algoritmo A\*, e manter o serviço 100% disponível perante falhas. Sistemas de despacho são o exemplo perfeito de sistemas onde a distribuição e a replicação de dados salvam ativamente vidas.



## 5. Atores



| Ator | Descrição | Necessidade principal | 

| ----- | ----- | ----- | 

| **Operador da central** | Recebe chamadas e regista ocorrências. | Ver rapidamente que unidade enviar e confirmar a atribuição. | 

| **Unidade de socorro** | Tripulação de ambulância, bombeiros, etc. | Receber a missão, a rota e atualizar o estado. | 

| **Administrador** | Gere utilizadores, unidades e bases. | Configurar o sistema e consultar auditoria. | 



## 6. Pesquisa de mercado



Os sistemas CAD comerciais são completos mas proprietários e dispendiosos. O despacho manual baseia-se na experiência sem tempos de rota reais. A Kairos diferencia-se por oferecer uma atribuição otimizada com restrições explícitas, reatribuição dinâmica por prioridade, cálculo de chegada real pela rede de estradas (A\*) e tolerância a faltas transparente e demonstrável.



## 7. Requisitos



### 7.1 Requisitos Funcionais e Não Funcionais



O sistema exige Autenticação por perfil (RF01), Registo com nível de gravidade (RF02), Proposta de atribuição via CSP (RF04), Reatribuição de unidades em trânsito (RF05) e Cálculo de rota A\* (RF07). Nos Requisitos Não Funcionais destacam-se: Desempenho inferior a 2 segundos para atribuição (RNF01), Tempo real (RNF02), e Integridade onde nenhuma ocorrência confirmada é perdida (RNF07).



### 7.2 Escala de Gravidade (Triagem de Manchester)



| Nível | Cor | Exemplos | Tempo-alvo | Peso (CSP) | 

| ----- | ----- | ----- | ----- | ----- | 

| **1 - Emergente** | Vermelho | Paragem cardiorrespiratória, inconsciente | 8 min | 16 | 

| **2 - Muito urgente** | Laranja | Dor torácica, suspeita de AVC | 15 min | 8 | 

| **3 - Urgente** | Amarelo | Fratura exposta, queimadura moderada | 30 min | 4 | 

| **4 - Pouco urgente** | Verde | Fratura fechada, entorse | 60 min | 2 | 

| **5 - Não urgente** | Azul | Transporte não urgente | 120 min | 1 | 



## 8. Arquitetura Distribuída



*(Inserir Diagrama de Arquitetura - Ingress, React, FastAPI, PostgreSQL)*



O sistema corre num cluster Kubernetes (k3s) com três máquinas virtuais distintas. O tráfego entra pelo Traefik Ingress (2 réplicas) e é servido por 3 réplicas *stateless* da API FastAPI. Os dados assentam numa base de dados PostgreSQL gerida pelo CloudNativePG com 3 instâncias (replicação síncrona), garantindo que a falha de uma máquina não elimina as réplicas aplicacionais.



## 9. Modelo de Faltas e Cenários



O sistema suporta a falha por paragem (*crash*) de qualquer componente isolado ou de uma máquina inteira do cluster. A consistência forte é assegurada pela réplica síncrona do PostgreSQL. Nos cenários de falha, se um Pod da API falhar a meio de um registo, o Kubernetes recria o Pod e a ocorrência, guardada na BD como pendente, será atribuída na execução seguinte do CSP, atrasando no máximo 30 segundos sem perda de dados.



## 10. Componente de Inteligência Artificial (Implementação)



A solução materializa o motor lógico central do processo de despacho de emergências, operando sobre o grafo da rede rodoviária real extraído do OpenStreetMap. A resolução processa-se sequencialmente.



### 10.1 Atribuição de Meios (Constraint Satisfaction Problem)



O primeiro passo da IA reduz o espaço de procura computacional recorrendo a um modelo de satisfação de restrições (CSP):

* **Variáveis:** Cada ocorrência pendente atua como uma variável que exige alocação.

* **Domínio:** O conjunto de todas as unidades disponíveis no distrito.

* **Restrições Obrigatórias:** Uma unidade é descartada se não possuir a adequação tipológica (ex: suporte avançado para níveis 1 e 2) ou se não estiver estritamente disponível (exceto se puder ser desviada de uma ocorrência menos grave).



### 10.2 Cálculo de Rotas (Algoritmo A\*)



Para as unidades validadas pelo CSP, o motor invoca o algoritmo de pesquisa heurística A\*. O objetivo é o tempo real de chegada pela rede rodoviária e não a distância em linha reta. A heurística desenhada garante admissibilidade:

> **Heurística (h) = Distância Euclidiana em linha reta ÷ Velocidade máxima da rede**



O algoritmo calcula o menor custo real acumulado somado à estimativa heurística até atingir o nó da ocorrência, devolvendo o tempo total de viagem.



### 10.3 Execução e Análise de Decisão



O motor minimiza a função de custo global: **Soma dos tempos de chegada × Peso da gravidade**. Em caso de ocorrências simultâneas a disputar o mesmo meio, aplicam-se os critérios de desempate:

1. Gravidade da ocorrência;

2. Qual vítima "perde mais" caso fique sem essa viatura;

3. Antiguidade do registo.



### 10.4 Integração na Arquitetura (PBL)



O algoritmo de IA (em Python) integra os pods da API desenvolvida em FastAPI de forma *stateless*. O CSP consome as ocorrências a partir do PostgreSQL, que atua simultaneamente como persistência e fila de trabalho. A consistência forte previne colisões: se duas instâncias tentarem atribuir a mesma ambulância, a BD valida apenas a primeira transação. Após a decisão, o FastAPI emite a atualização via WebSockets, refletindo-se na interface em menos de 1 segundo.



## 11. Segurança, Tecnologias e Testes



O sistema utiliza autenticação JWT, palavras-passe com *hash* (bcrypt), e cifra de dados pessoais (RGPD). As tecnologias incluem React e Leaflet no Frontend, FastAPI e OSMnx no Backend, CloudNativePG para dados e Docker/k3s para infraestrutura. Os guiões de teste validam o registo central, reatribuição dinâmica por gravidade, cenários de concorrência e resiliência a falhas de pods.



## 12. Dados de Investigação e Levantamento de Requisitos



### 12.1. Guião de Entrevista e Teste de Protótipo



Para alinhar a plataforma com a realidade das equipas de emergência, foi estruturado o seguinte guião de investigação:

* Como recebem a missão e que informações lhes são passadas exatamente?

* Existe alguma informação que vos costuma faltar quando saem?

* Já tiveram de ligar para a central a confirmar dados?

* Como escolhem o caminho? Usam GPS? Sistema próprio? Confiam nele?

* Já foram para a morada errada ou demoraram a encontrar o local? O que aconteceu?

* Como avisam a central de que saíram, de que chegaram ou de que ficaram livres?

* No início do turno, como é que a central sabe quem está em que viatura?

* Já foram desviados a caminho de uma ocorrência para outra mais grave? Como vos avisaram?



**Teste de Protótipo:**

* "Começou o turno. Entre e fique com a AMB-LX-02" | *Percebe o ecrã de escolher viatura?*

* (Criamos uma ocorrência) "Chegou-lhe uma missão. O que é e para onde vai?" | *Repara na missão sozinho? Percebe a gravidade, a morada e a rota?*

* Saiu do quartel → Chegou ao local → Terminou | *Encontra os botões? A ordem faz sentido?*

* "Acabou o turno" | *Sabe como sair?*



**Feedback Pós-Teste:** Que informação aqui não lhe serve e qual falta? Sente que este sistema auxiliaria ou seria uma "coisa" a mais? Que funcionalidades gostava que fossem adicionadas?



### 12.2. Termo de Consentimento Informado



*Projeto Kairos - Universidade Europeia · Licenciatura em Engenharia Informática · 2026/2027 · Grupo 08*

* **Objetivo:** Perceber como as equipas de emergência recebem e executam missões, e testar um protótipo de aplicação de despacho.

* **O que envolve:** Uma entrevista de ~40 min e um teste do protótipo num portátil/telemóvel.

* **Participação voluntária:** Pode recusar responder a qualquer pergunta e desistir a qualquer momento, sem dar justificação.

* **Dados:** As respostas são usadas apenas para fins académicos e não são partilhadas com a sua entidade empregadora. Não serão recolhidos dados de doentes nem de ocorrências reais.



## 13. Trabalho Futuro



1. **Recuperar mais depressa:** Baixar os ~140s do tempo de recuperação no teste da falha da BD primária.

2. **JWT e permissões:** Cada pedido autenticado validado estritamente, garantindo que o operador só vê o seu distrito.

3. **Dados da vítima cifrados:** Nome e descrição cifrados na base de dados para conformidade absoluta com o RGPD.

4. **Load Balancer:** Configuração de um IP único à frente das 3 máquinas (ex: Google Cloud).

5. **Página da vítima:** Portal onde quem pediu socorro pode acompanhar a chegada da ambulância através de um link.



## 14. Conclusão



O projeto Kairos demonstra como uma arquitetura distribuída e tolerante a faltas pode suportar um sistema crítico de emergências. Ao combinar a resiliência do Kubernetes e do PostgreSQL síncrono com a tomada de decisão otimizada do CSP e Algoritmo A\*, o sistema elimina os pontos únicos de falha e substitui a incerteza do despacho manual por decisões matemáticas transparentes e instantâneas que privilegiam a vida humana.
