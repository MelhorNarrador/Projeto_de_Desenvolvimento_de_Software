# 1. Introdução e Pesquisa de Mercado

**Palavras-chave:** sistemas distribuídos, tolerância a faltas, despacho de emergências, Kubernetes, replicação, problemas de satisfação de restrições, A*, tempo real

## 1.1 Introdução

Este relatório apresenta a primeira versão do projeto **Kairos**, desenvolvido no âmbito do projeto multidisciplinar de 5.º semestre da Licenciatura em Engenharia Informática.

A **Kairos** é uma plataforma web de despacho de emergências que recebe ocorrências (emergências médicas, incêndios, acidentes), acompanha em tempo real a posição e o estado das unidades de socorro e **atribui automaticamente a unidade mais adequada a cada ocorrência**, calculando a rota mais rápida até ao local.

Por se tratar de um sistema crítico, a plataforma é construída sobre uma **arquitetura distribuída e tolerante a faltas**: todos os componentes estão replicados, e a falha de um servidor, de uma réplica da base de dados ou de uma máquina inteira não interrompe o serviço nem provoca a perda de ocorrências.

Esta primeira entrega centra-se na **conceção do sistema**: definição do problema, requisitos, arquitetura distribuída, **modelo de faltas**, componentes de IA e segurança, e planeamento do desenvolvimento.

## 1.2 Pesquisa de Mercado

Os sistemas de despacho assistido por computador (**CAD – Computer-Aided Dispatch**) são utilizados por serviços de emergência em todo o mundo. Em Portugal, as chamadas de emergência médica são encaminhadas para os **CODU** (Centros de Orientação de Doentes Urgentes) do INEM.
