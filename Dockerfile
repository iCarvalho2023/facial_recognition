FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Install required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    cmake \
    g++ \
    make \
 && rm -rf /var/lib/apt/lists/*

# Instalar as dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "main.py"]
