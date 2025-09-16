FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG PIP_CACHE_DIR=/cache
ARG POETRY_CACHE_DIR=/cache
ARG TMPDIR=/cache
ENV PIP_CACHE_DIR=${PIP_CACHE_DIR} POETRY_CACHE_DIR=${POETRY_CACHE_DIR} TMPDIR=${TMPDIR}

WORKDIR /mycelium

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -v -r requirements.txt

COPY ./mycelium/ .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
