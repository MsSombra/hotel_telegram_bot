FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install

ENTRYPOINT ["python", "main.py"]