FROM python:3.10-slim

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr-por \
    libtesseract-dev \
    && apt-get clean

# Configuração do diretório de trabalho
WORKDIR /app

# Configuração do TESSDATA_PREFIX para apontar para os dados de treinamento do Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Copie o arquivo de requisitos e instale as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o contêiner
COPY main.py .

# Comando padrão para executar a aplicação FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
