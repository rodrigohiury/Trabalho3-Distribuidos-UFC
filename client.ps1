cd src/cliente/app
.\.venv\Scripts\Activate.ps1
cd ..
uvicorn app.main:app --reload --port 8000