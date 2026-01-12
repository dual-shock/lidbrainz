

FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY interface/ /app/interface/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.main"]