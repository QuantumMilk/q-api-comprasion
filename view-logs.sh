#!/bin/bash

# Скрипт для просмотра логов API сервисов

LOGS_DIR="./logs"

# Вспомогательные функции
show_usage() {
    echo "Usage: $0 [rest|graphql|grpc|all] [options]"
    echo ""
    echo "Options:"
    echo "  -f, --follow     Follow log output"
    echo "  -n, --lines N    Output the last N lines"
    echo "  -s, --service S  Show logs for specific service (api, business, requests)"
    echo ""
    echo "Examples:"
    echo "  $0 rest              - Show REST API logs"
    echo "  $0 graphql -f        - Follow GraphQL API logs"
    echo "  $0 grpc -n 100       - Show last 100 lines of gRPC API logs"
    echo "  $0 all               - Show all logs"
    echo "  $0 rest -s business  - Show REST API business events logs"
}

# Проверка количества аргументов
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

API_TYPE=$1
shift

# Параметры по умолчанию
FOLLOW=""
LINES="50"
SERVICE="api"

# Разбор опций
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--follow)
            FOLLOW="-f"
            shift
            ;;
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Функция для вывода логов
show_logs() {
    local api=$1
    local service=$2
    local log_file=""
    
    case "$service" in
        api)
            log_file="${LOGS_DIR}/${api}-api/${api}_api.log"
            ;;
        business)
            case "$api" in
                rest|graphql)
                    log_file="${LOGS_DIR}/${api}-api/user_service.log ${LOGS_DIR}/${api}-api/order_service.log"
                    ;;
                grpc)
                    log_file="${LOGS_DIR}/grpc-api/grpc_user_service.log ${LOGS_DIR}/grpc-api/grpc_order_service.log"
                    ;;
            esac
            ;;
        requests)
            case "$api" in
                rest)
                    log_file="${LOGS_DIR}/rest-api/rest_requests.log"
                    ;;
                graphql)
                    log_file="${LOGS_DIR}/graphql-api/graphql_requests.log"
                    ;;
                grpc)
                    log_file="${LOGS_DIR}/grpc-api/grpc_requests.log"
                    ;;
            esac
            ;;
        *)
            echo "Unknown service: $service"
            show_usage
            exit 1
            ;;
    esac
    
    if [ -f "$log_file" ]; then
        echo "Showing logs for ${api} API (${service}):"
        tail $FOLLOW -n $LINES $log_file
    else
        echo "Log file $log_file does not exist!"
    fi
}

# Вывод логов в зависимости от типа API
case "$API_TYPE" in
    rest)
        show_logs "rest" "$SERVICE"
        ;;
    graphql)
        show_logs "graphql" "$SERVICE"
        ;;
    grpc)
        show_logs "grpc" "$SERVICE"
        ;;
    all)
        echo "=== REST API logs ==="
        show_logs "rest" "$SERVICE"
        echo ""
        
        echo "=== GraphQL API logs ==="
        show_logs "graphql" "$SERVICE"
        echo ""
        
        echo "=== gRPC API logs ==="
        show_logs "grpc" "$SERVICE"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac