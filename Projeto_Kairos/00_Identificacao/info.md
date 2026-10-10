## 1. Título do projeto

**Kairos - Sistema Distribuído de Despacho de Emergências**

*O meio certo, no momento certo.*

## 2. Ano letivo

2026/2027

## 3. Semestre

1.º semestre (5.º semestre da licenciatura)

## 4. Curso(s) envolvido(s)

Licenciatura em Engenharia Informática (L-EI) - IADE

## 5. Unidade(s) curricular(es)

- Projeto de Desenvolvimento de Software
- Engenharia de Software
- Segurança Informática
- Sistemas Distribuídos
- Inteligência Artificial

## 6. Docente(s)

| Unidade curricular | Docente(s) |
|---|---|
| Projeto de Desenvolvimento de Software | Miguel Boavida |
| Engenharia de Software | Rui Ramos |
| Segurança Informática | Sérgio Nunes |
| Sistemas Distribuídos | Pedro Rosa |
| Inteligência Artificial | Samuel Gomes |

## 7. Estudantes participantes

Grupo 08

| Nome completo | Número | Curso | Ano curricular | Contacto institucional |
|---|---|---|---|---|
| Pedro António | 20241273 | L-EI | 3.º | -- |
| Mateus Reis | 20241799 | L-EI | 3.º | -- |
| Francisco Abecasis | 20240120 | L-EI | 3.º | -- |
| Deolindo Soares | 20221446 | L-EI | 3.º | -- |

## 8. Palavras-chave

Sistemas distribuídos; tolerância a faltas; replicação; despacho de emergências; inteligência artificial; A*; problemas de satisfação de restrições; Kubernetes; segurança informática;

## 9. Tecnologias utilizadas

| Camada | Tecnologias |
|---|---|
| Frontend | React, Leaflet, OpenStreetMap |
| Backend | Python, FastAPI, WebSockets, JWT, bcrypt |
| Inteligência Artificial | A* e CSP implementados em Python, OSMnx (exportação do grafo de estradas) |
| Base de dados | PostgreSQL, CloudNativePG |
| Infraestrutura | Docker, Kubernetes (k3s), Traefik |
| Ferramentas | GitHub, Trello, Visual Studio Code, Postman, Canva |

## 10. Resumo

O Kairos é um sistema distribuído de despacho de emergências médicas. O operador da central regista cada ocorrência com a localização, a identificação da vítima, uma breve descrição e o nível de gravidade, e o sistema atribui automaticamente o meio mais adequado. A atribuição combina dois algoritmos de Inteligência Artificial: o A*, que calcula o tempo de chegada de cada meio sobre a rede de estradas real, e um problema de satisfação de restrições (CSP), que decide que meio vai para cada ocorrência, dando prioridade aos casos mais graves. O sistema corre num cluster Kubernetes de três máquinas, com todos os componentes replicados e uma base de dados com réplica síncrona, mantendo o serviço disponível e sem perda de dados perante a falha de uma máquina. A comunicação é cifrada, o acesso é controlado por perfil e os dados pessoais das vítimas são protegidos.
