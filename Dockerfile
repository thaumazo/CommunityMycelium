FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /mycelium

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./mycelium/ .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
