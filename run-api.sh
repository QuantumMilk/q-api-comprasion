#!/bin/bash

# Вспомогательные функции
show_usage() {
    echo "Usage: $0 [rest|graphql|grpc|all]"
    echo ""
    echo "Options:"
    echo "  rest    - Start only REST API"
    echo "  graphql - Start only GraphQL API"
    echo "  grpc    - Start only gRPC API"
    echo "  all     - Start all APIs"
    echo ""
    echo "Example: $0 rest"
}

# Проверка количества аргументов
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

# Запуск с выбранным профилем
case "$1" in
    rest)
        echo "Starting REST API..."
        docker-compose --profile rest up -d
        ;;
    graphql)
        echo "Starting GraphQL API..."
        docker-compose --profile graphql up -d
        ;;
    grpc)
        echo "Starting gRPC API..."
        docker-compose --profile grpc up -d
        ;;
    all)
        echo "Starting all APIs..."
        docker-compose --profile full up -d
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

echo "API services started successfully"