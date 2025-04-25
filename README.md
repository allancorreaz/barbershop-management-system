# BARBESHOP MANAGEMENT SYSTEM

## 📌 Visão Geral
Sistema completo desenvolvido em Django para gestão de barbearias, com controle de clientes, agendamentos, estoque e finanças. Projeto profissional desenvolvido como solução completa para o gerenciamento diário de estabelecimentos do ramo.

## ✨ Funcionalidades Principais

## 👥 Gestão de Clientes
- Cadastro completo com histórico de serviços
- Controle de frequência e preferências
- Acompanhantes e observações personalizadas


## ✂️ Serviços e Cortes
- Catálogo de serviços com preços e durações
- Combos e promoções personalizáveis
- Sugestões automáticas baseadas no histórico


## 💰 Controle Financeiro
- Fluxo de caixa detalhado (entradas/saídas)
- Relatórios diários, semanais e mensais
- Exportação para PDF/Excel


## 📦 Gestão de Estoque
- Controle de produtos e materiais
- Alertas de reposição automáticos
- Histórico de movimentações


## 📊 Dashboard Inteligente
- Gráficos e métricas em tempo real
- Indicadores de performance
- Alertas e notificações


## 🛠 Tecnologias Utilizadas
- Backend: Python 3.9 + Django 4.2
- Frontend: Bootstrap 5 + HTML5/CSS3/JS
- Banco de Dados: SQLite (dev) / PostgreSQL (prod)
- Bibliotecas: Django Widget Tweaks, ReportLab, django-import-export
- Deploy: PythonAnywhere (versão atual)

## 🚀 Como Executar Localmente
- Pré-requisitos
- Python 3.9+
- Pip
- Virtualenv (recomendado)


## Instalação

# Clone o repositório
- git clone https://github.com/allancorreaz/barbershop-management-system.git

# Acesse a pasta do projeto
- cd barbershop-management-system

# Crie e ative o ambiente virtual (Windows)
- python -m venv venv
- venv\Scripts\activate

# Instale as dependências
- pip install -r requirements.txt

# Execute as migrações
- python manage.py migrate

# Crie um superusuário
- python manage.py createsuperuser

# Inicie o servidor
- python manage.py runserver
