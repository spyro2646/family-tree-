FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./services/api/app
COPY alembic ./services/api/alembic
COPY alembic.ini .
ENV PYTHONPATH=/srv/services/api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
