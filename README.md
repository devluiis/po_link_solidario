# Link Solidário: Conectando Pessoas, Transformando Vidas

![Banner do Projeto Link Solidário - Opcional, se tiver um banner](https://via.placeholder.com/1200x400?text=Link+Solidario+Banner) 
*(Você pode substituir esta linha por um link para um banner do seu projeto se tiver um)*

Um sistema web para facilitar a doação e troca solidária de produtos em comunidades do Tocantins. Desenvolvido como Projeto Integrador do 3º Período de Análise e Desenvolvimento de Sistemas da UNITINS.

## 🌟 Visão Geral do Projeto

O **Link Solidário** é uma iniciativa que visa combater o desperdício e fortalecer laços comunitários, criando uma ponte digital entre quem tem itens em desuso e quem precisa deles. A plataforma atua como um hub para doações e trocas, promovendo a reutilização e o consumo consciente em comunidades.

### Problema Abordado

A coexistência de recursos subutilizados e necessidades não atendidas em comunidades, agravada pela falta de um canal eficiente para a reutilização e solidariedade.

### Solução Proposta

Uma plataforma web intuitiva que conecta doadores/trocadores a indivíduos, ONGs e associações comunitárias que precisam de itens, otimizando o fluxo de doações e trocas.

## ✨ Funcionalidades (MVP)

O Produto Mínimo Viável (MVP) do Link Solidário inclui as seguintes funcionalidades principais:

* **Cadastro e Autenticação de Usuários:** Registro e login para moradores, ONGs e associações.
* **Gestão de Perfil:** Visualização e atualização de informações do usuário.
* **Cadastro de Produtos:** Publicação de itens para doação ou troca com detalhes como categoria, condição e descrição.
* **Listagem e Busca de Produtos:** Exploração de itens disponíveis com filtros por categoria e tipo de transação.
* **Detalhes do Produto:** Visualização aprofundada de um item específico.
* **Manifestação de Interesse:** Indicação de interesse em um produto por parte de um usuário.
* **Gestão de Produtos do Usuário:** Edição e remoção de itens cadastrados pelo próprio usuário.
* **Painel Administrativo:** Gerenciamento básico de usuários e moderação de produtos.

## 🚀 Tecnologias Utilizadas

Este projeto foi construído com um stack tecnológico robusto e moderno:

* **Backend:**
    * **Python:** Linguagem de programação principal.
    * **Flask:** Microframework web para o desenvolvimento das APIs e lógica de negócio.
    * **Flask-SQLAlchemy:** ORM (Object-Relational Mapper) para interação com o banco de dados.
    * **PyMySQL:** Driver de conexão com o banco de dados MySQL.
    * **Gunicorn:** Servidor WSGI para execução da aplicação Flask em ambiente de produção/teste.
* **Frontend:**
    * **HTML:** Estrutura das páginas.
    * **Jinja2:** Motor de templates para renderização dinâmica do HTML.
    * **Tailwind CSS:** Framework CSS "utility-first" para estilização rápida e responsiva.
* **Banco de Dados:**
    * **MySQL:** Sistema de Gerenciamento de Banco de Dados Relacional (SGBDR).
    * **phpMyAdmin:** Interface gráfica web para gerenciamento do MySQL.
* **Outras Ferramentas:**
    * **Git:** Sistema de Controle de Versão.
    * **GitHub:** Plataforma para hospedagem do repositório de código.
    * **Ubuntu 22.04 LTS:** Sistema Operacional (utilizado em Máquina Virtual).

## 💻 Como Rodar o Projeto (Localmente)

Siga estes passos para configurar e executar o projeto em sua máquina local (Ubuntu recomendado, similar em outros sistemas Linux/macOS):

### Pré-requisitos

* **Python 3.10+** e `pip` (gerenciador de pacotes Python)
* **Node.js (v18+ LTS recomendado) e npm** (para Tailwind CSS)
* **MySQL Server** (e opcionalmente phpMyAdmin)
* **Git**

### 1. Clonar o Repositório

```bash
git clone [https://github.com/devluiis/po_link_solidario.git](https://github.com/devluiis/po_link_solidario.git)
cd po_link_solidario
