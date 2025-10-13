# Usinagem ERP - Backend

Backend inicial com FastAPI.

## Rodando local
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --reload
