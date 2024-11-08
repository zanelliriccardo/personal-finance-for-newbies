FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry==1.5.1

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8501

ENTRYPOINT ["poetry", "run", "streamlit", "run", "./src/0_🏠_Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
