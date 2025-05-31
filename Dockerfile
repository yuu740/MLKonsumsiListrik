FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]

