FROM python:3.11-slim

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    tar \
    build-essential \
    golang \
    git

# Установка k6
RUN wget https://github.com/grafana/k6/releases/download/v0.42.0/k6-v0.42.0-linux-amd64.tar.gz && \
    tar -xzf k6-v0.42.0-linux-amd64.tar.gz && \
    mv k6-v0.42.0-linux-amd64/k6 /usr/local/bin/ && \
    rm -rf k6-v0.42.0-linux-amd64 k6-v0.42.0-linux-amd64.tar.gz

# Установка ghz (для тестирования gRPC)
RUN wget https://github.com/bojand/ghz/releases/download/v0.120.0/ghz-linux-x86_64.tar.gz && \
    tar -xzf ghz-linux-x86_64.tar.gz && \
    mv ghz /usr/local/bin/ && \
    rm ghz-linux-x86_64.tar.gz

# Установка grpcurl
RUN wget https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz && \
    tar -xzf grpcurl_1.8.7_linux_x86_64.tar.gz && \
    chmod +x grpcurl && \
    mv grpcurl /usr/local/bin/ && \
    rm grpcurl_1.8.7_linux_x86_64.tar.gz

# Установка Python-зависимостей для анализа
RUN pip install matplotlib numpy pandas tabulate jinja2

WORKDIR /app

# Точка входа
CMD ["bash"]