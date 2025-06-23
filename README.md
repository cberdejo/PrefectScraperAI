# Prefect Scraper AI 

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-FF4F00?style=for-the-badge&logo=MinIO&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B0082?style=for-the-badge)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformer-FFCC00?style=for-the-badge)




This project implements a web scraping pipeline orchestrated with **Prefect**. It scrapes real estate data using **Selenium** and **BeautifulSoup**, stores the data in **PostgreSQL**, and generates **embeddings** with **SentenceTransformer** to enable advanced similarity searches. Reports and intermediate results are saved in **MinIO**.

---

## 🚀 Main Technologies Used

- **Python 3.11**: Main programming language.
- **Apache Airflow**: Orchestrates and schedules scraping and data-processing tasks.
- **PostgreSQL**: Stores structured data and embeddings.
- **MinIO**: Object storage compatible with Amazon S3, used for storing reports.
- **Selenium**: Automates interactions with dynamic websites.
- **BeautifulSoup**: Parses and extracts data from static HTML.
- **SentenceTransformer**: Generates semantic embeddings for similarity comparison.
- **SQLAlchemy**: ORM for interacting with PostgreSQL.



## 🗂️ Project Structure
```
scraping-pipeline
├─ 📁airflow_scrap
│  ├─ 📁src
│  │  └─ 📁dags
│  │     ├─ 📄main.py
│  │     └─ 📄__init__.py
│  ├─ 📄Dockerfile
│  ├─ 📄pyproject.toml
│  ├─ 📄README.md
│  └─ 📄uv.lock
├─ 📁prefect_scrap
│  ├─ etc[...]
│  ├─ 📄Dockerfile
│  ├─ 📄pyproject.toml
│  ├─ 📄README.md
│  └─ 📄uv.lock
├─ 📁scrap_utils
│  ├─ 📁src
│  │  ├─ 📁config
│  │  ├─ 📁helpers
│  │  ├─ 📁models
│  │  └─ 📁tasks
│  ├─ 📄README.md
│  └─ 📄uv.lock
├─ 📄.dockerignore
├─ 📄.gitignore
├─ 📄.pre-commit-config.yaml
├─ 📄docker-compose.airflow.yml
├─ 📄docker-compose.prefect.yml
├─ 📄LICENSE
└─ 📄README.md
```
```
PrefectScraperAI
├─ 📁src
│  ├─ 📁config
│  │  ├─ 📄logger.py
│  │  ├─ 📄minio.py
│  │  ├─ 📄postgres.py
│  │  └─ 📄__init__.py
│  ├─ 📁helpers
│  │  ├─ 📄utils.py
│  │  └─ 📄__init__.py
│  ├─ 📁models
│  │  ├─ 📄pydantic_models.py
│  │  ├─ 📄sqlalchemy_models.py
│  │  └─ 📄__init__.py
│  ├─ 📁pipeline
│  │  ├─ 📄main.py
│  │  ├─ 📄prefect_pipeline.py
│  │  └─ 📄__init__.py
│  └─ 📁tasks
│     ├─ 📄generate_embedding.py
│     ├─ 📄load_to_postgres.py
│     ├─ 📄scrape_pisos.py
│     ├─ 📄scrape_solvia.py
│     ├─ 📄upload_report.py
│     └─ 📄__init__.py
├─ 📄.dockerignore
├─ 📄.env-template
├─ 📄.gitignore
├─ 📄.python-version
├─ 📄docker-compose.yml
├─ 📄Dockerfile
├─ 📄LICENSE
├─ 📄pyproject.toml
├─ 📄README.md
└─ 📄uv.lock
```
## ⚙️ How to Use

### 🔁 With Docker

Clone the repository:

```bash
git clone https://github.com/cberdejo/PrefectScraperAI.git
cd web-scraping-dag
```

Build and run services:

```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** on port `5432`
- **MinIO** on port `9100` (API) and `9101` (web console)
- A container that executes the pipeline via `src/main.py`

You can customize services via `docker-compose.yml`.

---

### 💻 Running Locally

Make sure Python 3.11 is installed.

#### Using [uv](https://github.com/astral-sh/uv)

```bash
uv run src/main.py
```

#### Or manually:

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

2. Install dependencies:

```bash
pip install .
```

3. Run the main flow:

```bash
python src/main.py
```

> ⚠️ Ensure that PostgreSQL and MinIO are running and accessible. Configure credentials via a `.env` file.



## 📦 Environment Variables

Create a `.env` file like the following to match Docker defaults:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=postgres

MINIO_ENDPOINT=http://localhost:9100
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```



## 🧪 Main Scripts Overview

- `src/main.py`: Coordinates the overall pipeline execution.
- `tasks/scrape_pisos.py`: Scrapes apartments from pisos.com using Selenium.
- `tasks/scrape_solvia.py`: Scrapes listings from solvia.com using BeautifulSoup.
- `tasks/generate_embedding.py`: Transforms text data into vector embeddings using `SentenceTransformer`.
- `tasks/load_to_postgres.py`: Upserts scraped and enriched data into PostgreSQL.
- `tasks/generate_report.py`: Creates and uploads a summary report to MinIO.


## 🧠 Why Use Embeddings?

Embeddings convert apartment descriptions into **numerical vectors** that capture semantic meaning. This enables **search by similarity** (e.g., "Find apartments like this one") using metrics like **cosine similarity**.

You can query similar listings directly from the database using vector extensions such as [pgvector](https://github.com/pgvector/pgvector) or [PGEmbedding](https://python.langchain.com/docs/integrations/vectorstores/pgembedding/), or export them to a vector database like Qdrant, Pinecone, or FAISS.

This transforms your scraped data into a **semantic search engine** for real estate listings.



## 📄 License

MIT – free to use, modify and distribute.



