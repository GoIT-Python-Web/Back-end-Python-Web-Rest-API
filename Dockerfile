FROM python:3.11

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "echo \"[alembic]\nscript_location = alembic\nsqlalchemy.url = $DATABASE_URL\n\n[logging]\nlevel = INFO\nformatters = keys\nhandlers = keys\nloggers = keys\" > alembic.ini && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
