# Kairos — Roadmap

Última atualização: 26/10/2026

## Entregas

| Entrega | Data | Conteúdo |
|---|---|---|
| E1 ✅ | 09–11/10/2026 | Conceito, arquitetura, relatório v1, apresentação |
| **E2** | **15/11/2026** | Protótipo a funcionar na cloud: cálculo de rotas, atribuição automática de meios e primeiros testes de falha |
| E3 | 20/12/2026 | Versão final: login seguro, proteção dos dados das vítimas, redirecionamento de meios, ajuda entre distritos e demonstração completa de falhas |

## Já feito

| O quê | Estado |
|---|---|
| Organizar o repositório e guardar os dados (ocorrências, meios, utilizadores, distritos) | ✅ |
| Registar e consultar ocorrências; consultar os meios de cada distrito | ✅ |
| Tripulação: iniciar e terminar turno, enviar a localização, atualizar o estado da missão | ✅ |
| Calcular rotas e tempos de chegada pelas estradas reais (Lisboa e Setúbal) | ✅ |
| Escolher automaticamente o melhor meio para cada ocorrência: as mais graves primeiro, nunca duas ambulâncias para o mesmo sítio, e quem espera há mais tempo ganha prioridade | ✅ |
| Testar com várias cópias do sistema a funcionar ao mesmo tempo, incluindo 20 ocorrências em simultâneo | ✅ |

## Semana de 26/10 a 01/11 — a aplicação

- Mapa do operador com as ocorrências e os meios do distrito
- Registar uma ocorrência com pesquisa de moradas enquanto se escreve (ou clicando no mapa)
- Ecrã da tripulação no telemóvel: escolher a viatura, ver a missão e o caminho até ao local
- Atualizações automáticas: o mapa e o telemóvel mudam sozinhos, sem recarregar a página
- Preparar o sistema para ser instalado automaticamente na cloud: gerar as versões prontas a instalar e descrever quantas cópias de cada parte correm e como se ligam (feito já esta semana, para descobrir problemas cedo)

## Semana de 02/11 a 08/11 — a cloud

- Pôr o sistema a funcionar em 3 máquinas na cloud (Azure), com as cópias de cada parte espalhadas pelas máquinas e substituídas automaticamente se uma falhar
- Base de dados com cópias em várias máquinas, para não se perder nada se uma falhar
- Acesso seguro (HTTPS) e duas portas de entrada, para o site continuar disponível se uma cair

**08/11 — ponto de decisão:** se a gestão automática do sistema não estiver a funcionar, passamos para uma forma mais simples de o gerir **nas mesmas 3 máquinas** (plano B). O sistema continua distribuído: várias máquinas, várias cópias e base de dados com cópia; perde-se apenas a substituição automática da base de dados principal.
Só se não houver máquinas na cloud disponíveis é que a demonstração é feita num único computador (plano C, último recurso).

## Semana de 09/11 a 15/11 — entrega E2

- Testes de falha: desligar uma máquina, a base de dados principal e uma cópia do sistema, e mostrar que continua a funcionar
- Relatório v2 e slides
- **15/11: entrega E2**

## Até à E3 (20/12)

- Login seguro para operadores, tripulações e administrador
- Cada operador só vê as ocorrências e os meios do seu distrito
- Proteger o nome da vítima e a descrição da ocorrência
- Redirecionar uma ambulância a caminho para uma ocorrência mais grave
- Pedir meios aos distritos vizinhos quando faltam
- Demonstração completa de falhas
