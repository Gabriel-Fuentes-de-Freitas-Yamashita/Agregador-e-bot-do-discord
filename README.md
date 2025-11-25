# 🎯 Hardware Sniper Bot

> **Monitor de promoções em tempo real com inteligência de filtragem e alertas visuais.**

[![Deploy Status](https://img.shields.io/badge/Render-Live-success?style=for-the-badge&logo=render)]([SEU_LINK_DO_RENDER_AQUI])
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Dev_Env-2496ED?style=for-the-badge&logo=docker)

## 🧐 Sobre o Projeto

Este projeto nasceu da necessidade de monitorar "bugs de preço" e lançamentos de hardware (GPUs, CPUs, Consoles) sem precisar atualizar manualmente dezenas de sites o dia todo.

O **Hardware Sniper Bot** é um sistema backend autônomo que varre feeds RSS de grandes portais de tecnologia (como Pelando, Adrenaline, Gatry) a cada 5 minutos. Ele utiliza um filtro "Sniper" para ignorar promoções genéricas e focar apenas em itens de alto interesse, enviando um alerta rico (com imagem e link direto) para um canal do Discord assim que a oferta é detectada.

## 📸 Demonstração

### 1. Alertas Visuais no Discord
O bot extrai a imagem do produto diretamente do HTML da fonte, gerando cards visuais fáceis de identificar.

![Print do Discord com Alertas]
<img width="1278" height="992" alt="image" src="https://github.com/user-attachments/assets/ad1e0ed7-94f3-486b-96d5-8d629cd6f8d8" />


### 2. Monitoramento Contínuo na Nuvem
O sistema roda em um loop infinito no Render.com, sem intervenção humana.

![Print dos Logs do Render]
<img width="1578" height="795" alt="image" src="https://github.com/user-attachments/assets/a9d17b86-bce7-4918-a16a-78bd384f5cf5" />


## 🚀 Diferenciais Técnicos

* **Arquitetura Assíncrona (AsyncIO):** Utiliza `httpx` e `asyncio` para realizar múltiplas requisições HTTP e processamento de dados de forma não bloqueante, garantindo alta performance mesmo monitorando dezenas de fontes.
* **Sniper Mode (Filtragem Inteligente):** Lógica dedicada (`services.py`) que filtra o ruído usando uma lista de keywords específicas (ex: "RTX 4070", "Ryzen 7800X3D"), ignorando ofertas irrelevantes.
* **Web Scraping Integrado:** Uso de `BeautifulSoup4` para analisar o HTML das descrições dos feeds RSS e extrair imagens que normalmente ficam ocultas.
* **Segurança via API Key:** Proteção de rotas administrativas (`POST`) contra uso não autorizado, exigindo um cabeçalho de autenticação personalizado.
* **Persistência Híbrida:**
    * **Desenvolvimento:** Configurado para usar **SQL Server** via Docker.
    * **Produção (Cloud):** Detecta automaticamente o ambiente e conecta ao **PostgreSQL** (Neon Tech).
* **Estratégia de Caching (Redis):** Implementação pronta para uso de Redis para cachear buscas na API (opcional na nuvem).

## 🛠️ Tech Stack

* **Linguagem:** Python 3.11
* **Framework Web:** FastAPI (Uvicorn/Gunicorn)
* **Banco de Dados:** PostgreSQL (Produção) / SQL Server 2022 (Dev)
* **ORM:** SQLAlchemy (Async) + Asyncpg/Aioodbc
* **ETL/Scraping:** Feedparser, BeautifulSoup4, Lxml
* **Infraestrutura:** Docker Compose, Render (Cloud PaaS)

## ⚙️ Instalação e Execução Local

### Pré-requisitos
* Python 3.10+
* Docker (Opcional, para rodar banco local)

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/](https://github.com/)[SEU_USUARIO]/hardware-sniper-bot.git
    cd hardware-sniper-bot
    ```

2.  **Configure o ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Configure o Webhook:**
    Abra o arquivo `services.py` e adicione a URL do seu Webhook do Discord na variável `DISCORD_WEBHOOK_URL`.

4.  **Suba o banco de dados (Docker):**
    ```bash
    docker-compose up -d sqlserver redis
    ```
    *(Ou configure a URL para um Postgres local no arquivo `database.py`)*

5.  **Execute a aplicação:**
    ```bash
    uvicorn main:app --reload
    ```
    O bot iniciará o loop de monitoramento automático imediatamente no terminal.

## ☁️ Deploy

O projeto está atualmente hospedado no **Render.com** (plano gratuito), conectado a um banco de dados **PostgreSQL no Neon.tech**. O deploy é contínuo (CI/CD) a cada push na branch `main`.

A API pode ser acessada em: `https://agregador-e-bot-do-discord.onrender.com/docs`

---
Desenvolvido por Gabriel Fuentes.
