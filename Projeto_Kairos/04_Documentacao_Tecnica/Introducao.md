# 4. Metodologia

O projeto segue uma **metodologia ágil baseada em Kanban**. O trabalho flui de forma contínua por um quadro de tarefas, em vez de ser organizado em ciclos fechados, o que se adapta melhor a uma equipa com disponibilidades variáveis ao longo do semestre. Para garantir o cumprimento das três entregas, o quadro é complementado por **milestones** com datas fixas.

O quadro é gerido no **Trello** o que garante a rastreabilidade de todo o trabalho realizado.

## 4.1 Quadro Kanban

| Coluna | Significado |
|---|---|
| **Backlog** | Tarefas identificadas, ainda não priorizadas |
| **To Do** | Tarefas priorizadas para o marco atual, prontas a ser iniciadas |
| **Doing** | Tarefas em desenvolvimento, com um responsável atribuído |
| **Blocked** | Tarefa bloqueada, espera por ajuda de outro elemento ou finalização de outra tarefa |
| **In Review** | Tarefa concluída, espera por testes e revisão por outro elemento |
| **Done** | Tarefa revista e integrada no ramo principal |

## 4.2 Regras de Trabalho

| Regra | Descrição |
|---|---|
| **Limite de trabalho em curso (WIP)** | Cada elemento tem no máximo 2 tarefas em "Doing" em simultâneo |
| **Uma tarefa, um cartão** | Todo o trabalho é registado como cartões no Trello, com responsável e etiquetas |
| **Definição de Done** | Uma tarefa só passa a "Done" quando o código ou documento está revisto, integrado e testado |
| **Ponto de situação semanal** | Reunião curta com o quadro como base: o que avançou, o que está bloqueado e o que se segue |

## 4.3 Etiquetas

| Tipo | Etiquetas |
|---|---|
| **Natureza da tarefa** | `feature`, `bug`, `docs`, `teste` |
| **Prioridade** | `alta`, `média`, `baixa` |

## 4.4 Marcos (Milestones)

| Marco | Data | Objetivo |
|---|---|---|
| **Entrega 1 – Conceção** | 11/10/2026 | Problema, requisitos, arquitetura, modelo de faltas, relatório v1 |
| **Entrega 2 – Protótipo** | 15/11/2026 | Cluster Kubernetes, backend replicado, CSP e A* funcionais, primeiros testes de falha, relatório v2 |
| **Entrega 3 – Versão final** | 20/12/2026 | Frontend completo, segurança, testes de falha automatizados, demonstração, relatório final |
