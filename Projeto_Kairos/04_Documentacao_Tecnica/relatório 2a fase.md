# KAIRÓS - Sistema Distribuído de Despacho de Emergências

**Instituição:** Universidade Europeia / IADE  
**Curso:** Engenharia Informática  
**Unidade Curricular:** Projeto Multidisciplinar (5º Semestre - 2026/2027)  

**Elementos do Grupo:**
- Deolindo Soares
- Mateus Reis
- Pedro Afonso
- Francisco Abecasis (20240120)

---

## 1. Introdução e Pesquisa de Mercado
A Kairos é uma plataforma web de despacho de emergências que recebe ocorrências (emergências médicas, incêndios, acidentes), acompanha em tempo real a posição e o estado das unidades de socorro e atribui automaticamente a unidade mais adequada a cada ocorrência, calculando a rota mais rápida até ao local.

Por se tratar de um sistema crítico, a plataforma é construída sobre uma arquitetura distribuída e tolerante a faltas: todos os componentes estão replicados, e a falha de um servidor, de uma réplica da base de dados ou de uma máquina inteira não interrompe o serviço nem provoca a perda de ocorrências.

A decisão manual tem falhas fatais, como o facto de o operador usar a distância em linha reta em vez da rede de estradas real, e as ocorrências serem tratadas por ordem de chegada em vez de prioridade.

### Pesquisa de Mercado
Os sistemas de despacho assistido por computador (CAD – Computer-Aided Dispatch) são utilizados por serviços de emergência em todo o mundo. Em Portugal, as chamadas de emergência médica são encaminhadas para os CODU (Centros de Orientação de Doentes Urgentes) do INEM.

---

## 2. Requisitos do projeto
**Funcionalidades principais:**
- Registar uma ocorrência. 
- Classificar a ocorrência por tipo e gravidade. 
- Localizar a ocorrência no mapa. 
- Identificar unidades disponíveis. 
- Escolher automaticamente a unidade adequada. 
- Calcular a rota até à ocorrência. 
- Enviar a missão para a unidade. 
- Permitir à unidade aceitar a missão. 
- Atualizar a localização das unidades. 
- Permitir cancelar/concluir uma missão. 
- Reavaliar as atribuições quando surge uma emergência mais grave. 
- Mostrar tudo num dashboard.

---

## 3. Atores

| Ator | O que faz | Principais ações |
|---|---|---|
| **Operador** | Pessoa responsável por acompanhar e gerir as emergências | Registar ocorrências, consultar ocorrências, acompanhar unidades e missões |
| **Unidade** | Recurso que recebe e executa as missões | Receber, aceitar/rejeitar missão, atualizar estado e localização |
| **Administrador** | Responsável pela gestão e configuração | Gerir utilizadores, unidades, permissões e consultar logs |
| **Simulador** | Componente que gera ocorrências e movimentação | Criar ocorrências, alterar posições das unidades e simular |

---

## 4. Requisitos Funcionais e Não Funcionais

**Funcionais:**
* **RF01:** Autenticação de utilizadores com perfis de operador, unidade e administrador.
* **RF02:** Registo de ocorrências com tipo, localização, nome da vítima, descrição e nível de gravidade.
* **RF03:** Visualização das ocorrências e unidades do distrito num mapa em tempo real.
* **RF04:** Receção de missão e envio para a unidade selecionada.
* **RF05:** Atualização de localização das unidades em tempo real.
* **RF06:** Gestão e acompanhamento do estado das ocorrências.
* **RF07:** Reatribuição das atribuições quando surgir uma ocorrência de maior gravidade.

**Não Funcionais:**
* **RNF01 (Desempenho):** A proposta de atribuição é apresentada em menos de 2 segundos.
* **RNF02 (Tempo real):** Alterações de estado chegam aos utilizadores em menos de 1 segundo.
* **RNF03 (Recuperação):** Após falha de um componente, a redundância é reposta automaticamente.
* **RNF04 (Rastreabilidade):** Decisões guardadas e confirmadas em base de dados.
* **RNF05 (Usabilidade):** Interface responsiva, utilizável em computador e telemóvel.

---

## 5. Sistemas Distribuídos e Tolerância a Falhas

A arquitetura será constituída por vários componentes, incluindo o frontend (React), o backend (FastAPI), o sistema de mensagens e a base de dados (PostgreSQL).

* **Múltiplas instâncias do backend:** Para aumentar a disponibilidade, existem 3 instâncias do backend a executar simultaneamente geridas pelo Kubernetes.
* **Base de Dados Replicada:** Utiliza-se CloudNativePG com replicação em streaming e réplica síncrona. Se o pod principal falhar, o failover é automático.
* **Tolerância a Falhas:** A arquitetura distribuída permite que o sistema continue a funcionar perante falhas severas. A queda de um nó (máquina virtual) do Kubernetes não dita a paragem do serviço, pois os pods são recriados noutros nós saudáveis.

---

## 6. Inteligência Artificial (Milestone 2)

O protótipo de Inteligência Artificial desenvolvido e testado isoladamente (presente na pasta `protoIA`) atua como o motor de decisão para despacho.

### 6.1 Problema de Atribuição de Unidades (CSP)
O problema de atribuição é modelado como um **Constraint Satisfaction Problem (CSP)**. Cada ocorrência atua como uma variável, e a frota representa o domínio. A IA aplica as seguintes restrições obrigatórias:
1. **Adequação Tipológica:** O tipo de unidade tem de ser compatível (ex: suporte avançado).
2. **Disponibilidade:** A unidade tem de estar estritamente disponível ou a caminho de um caso menos grave (reatribuição).

### 6.2 Cálculo de Rotas (Algoritmo A*)
Para as unidades validadas pelo CSP, o motor invoca o algoritmo de pesquisa heurística **A*** (A-Star), calculando o custo de deslocação sobre o grafo da rede rodoviária real.
* **Heurística utilizada:** `Distância em linha reta / Velocidade máxima da rede`. Esta heurística é admissível e garante a otimização da rota real.

### 6.3 Execução e Análise de Decisão
O motor cruza os tempos do A* com os pesos de gravidade clínica para minimizar a função de custo global. A escala baseia-se na Triagem de Manchester:

| Nível | Cor | Exemplos Clínicos | Tempo-alvo | Peso (CSP) |
|---|---|---|---|---|
| **1 – Emergente** | Vermelho | Paragem cardiorrespiratória, inconsciente | 8 min | 16 |
| **2 – Muito urgente** | Laranja | Dor torácica, AVC, hemorragia | 15 min | 8 |
| **3 – Urgente** | Amarelo | Fratura exposta, queimadura moderada | 30 min | 4 |
| **4 – Pouco urgente** | Verde | Fratura fechada, ferida ligeira | 60 min | 2 |
| **5 – Não urgente** | Azul | Transporte não urgente | 120 min | 1 |

*Em caso de concorrência por uma viatura, o desempate obedece a: 1º Gravidade absoluta; 2º Impacto de Perda (quem perde mais tempo se usar a 2ª alternativa); 3º Antiguidade do registo.*

### 6.4 Integração Técnica
O modelo IA será consumido de forma *stateless* no Kubernetes. Consome ocorrências "Pendentes" a partir do PostgreSQL (que atua como fila), processa o CSP e o A*, e o FastAPI despacha a resposta aos clientes por WebSockets (Traefik Ingress) em tempo real.

---

## 7. Segurança
* **Autenticação:** Utilizadores iniciam sessão com palavras-passe cifradas e tokens JWT.
* **Autorização e permissões:** Perfis separados para operador, unidade e administrador.
* **Comunicação Segura:** Todo o tráfego é encaminhado por HTTPS e WebSockets cifrados.

---

## 8. Dados Investigação e Consentimento
Foi elaborado um guião de entrevista e um teste do protótipo com os tripulantes de emergência:
* Avaliação da forma como recebem missões (falta de dados, problemas de navegação).
* Teste de usabilidade aos ecrãs de "Início de turno", "Missão Atribuída" e "Rota".
* Preenchimento do Termo de Consentimento Informado (aprovando gravação áudio/vídeo apenas para fins académicos).

---

## 9. Trabalho Futuro
1. **Recuperar mais depressa:** Otimizar e baixar os tempos de failover em caso de queda da Base de Dados primária.
2. **Dados da vítima cifrados:** Mascarar Nome e descrição (RGPD) diretamente na base de dados.
3. **Página da vítima:** Criar mecanismo web para quem pediu socorro acompanhar a ambulância por um link seguro.

---

## 10. Conclusão
A combinação de Sistemas Distribuídos com Inteligência Artificial garante uma central resiliente (nunca vai abaixo) e inteligente (decide sem falhas humanas). O motor IA validado no Milestone 2 cumpre o objetivo de processar regras complexas num grafo real em menos de 2 segundos, provando a viabilidade técnica da arquitetura Kairos.
