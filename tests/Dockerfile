# tests/Dockerfile
FROM ubuntu:22.04

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    tar \
    python3 \
    python3-pip \
    # Зависимости для grpcurl
    golang \
    git

# Установка k6 напрямую
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
RUN pip3 install matplotlib numpy pandas tabulate

# Создание структуры директорий
WORKDIR /tests
RUN mkdir -p k6-scripts
RUN mkdir -p results/rest
RUN mkdir -p results/graphql
RUN mkdir -p results/grpc
RUN mkdir -p results/graphs

# Точка входа
CMD ["/bin/bash"]