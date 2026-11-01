# Roteiro de commits (Conventional Commits)

Faça um commit por etapa. Um histórico limpo mostra a evolução do projeto para quem avalia seu GitHub.

| # | Mensagem | O que entra |
|---|---|---|
| 1 | `chore: initial project structure` | `.gitignore`, `requirements.txt`, `ruff.toml`, pastas |
| 2 | `feat(config): add paths, series and API settings` | `src/pipeline/config.py` |
| 3 | `feat(bronze): ingest raw BCB series with retry and metadata` | `bronze.py` |
| 4 | `feat(silver): clean, type and validate series` | `silver.py` |
| 5 | `test(silver): cover transform and quality rules` | `tests/test_silver.py`, `conftest.py` |
| 6 | `feat(gold): monthly indicators with 12m accumulated IPCA` | `gold.py` |
| 7 | `test(gold): validate IPCA 12m calculation` | `tests/test_gold.py` |
| 8 | `feat(cli): add runner to execute layers locally` | `run.py`, `Makefile` |
| 9 | `feat(airflow): add medallion DAG with dynamic task mapping` | `dags/`, `docker-compose.yml` |
| 10 | `ci: add lint and tests workflow` | `.github/workflows/ci.yml` |
| 11 | `docs: add README with architecture diagram` | `README.md`, `docs/` |

## Commits extras (evolução futura)
- `feat(silver): add schema validation with pandera`
- `feat(gold): add yearly aggregation table`
- `feat(airflow): add failure alert callback`
- `refactor: migrate gold to dbt`
- `feat(storage): write layers to S3/MinIO`

## Comandos
```bash
git init && git branch -M main
git add .gitignore requirements.txt ruff.toml && git commit -m "chore: initial project structure"
# ... repita para cada etapa
git remote add origin https://github.com/SEU_USUARIO/br-economic-lakehouse.git
git push -u origin main
```
