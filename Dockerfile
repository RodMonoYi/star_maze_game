FROM python:3.11-slim

# Instalações de dependências de sistema (incluindo suporte ao tkinter + GUI)
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    tk \
    x11-apps \
    libx11-6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos
COPY . .

# Comando para rodar o app
CMD ["python", "game.py"]
