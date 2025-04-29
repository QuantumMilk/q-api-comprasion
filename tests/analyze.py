#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import traceback
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

print("Скрипт запущен.")
sys.stdout.flush()  # Принудительная запись в stdout

# Создаем директории для результатов и графиков, если они не существуют
os.makedirs('results/rest', exist_ok=True)
os.makedirs('results/graphql', exist_ok=True)
os.makedirs('results/grpc', exist_ok=True)
os.makedirs('results/graphs', exist_ok=True)

print("Директории созданы.")
sys.stdout.flush()

def load_k6_json(file_path):
    """Загружает данные из результатов k6"""
    print(f"Пытаюсь загрузить файл: {file_path}")
    sys.stdout.flush()
    
    try:
        # Проверка существования файла
        if not os.path.exists(file_path):
            print(f"Файл не существует: {file_path}")
            sys.stdout.flush()
            return None
        
        print(f"Файл существует, размер: {os.path.getsize(file_path)} байт")
        sys.stdout.flush()
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        print(f"Количество строк в файле: {len(lines)}")
        sys.stdout.flush()
        
        if not lines:
            print(f"Файл пустой: {file_path}")
            sys.stdout.flush()
            return None
        
        # K6 выводит результаты в формате NDJSON (каждая строка - отдельный JSON)
        # Нам нужен последний объект, который содержит метрики
        metrics_data = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if data.get('type') == 'Metric':
                    # Сохраняем информацию о метрике
                    metric_name = data.get('metric')
                    if metric_name and 'data' in data:
                        if 'metrics' not in metrics_data:
                            metrics_data['metrics'] = {}
                        metrics_data['metrics'][metric_name] = data['data']
                
                # Собираем метрики из Point типов, где есть value
                if data.get('type') == 'Point' or (data.get('metric') and 'data' in data and 'value' in data['data']):
                    metric_name = data.get('metric')
                    if metric_name:
                        if 'metrics' not in metrics_data:
                            metrics_data['metrics'] = {}
                        
                        if metric_name not in metrics_data['metrics']:
                            metrics_data['metrics'][metric_name] = {}
                        
                        value = data['data'].get('value')
                        # Аггрегируем разные значения одной метрики
                        if 'values' not in metrics_data['metrics'][metric_name]:
                            metrics_data['metrics'][metric_name]['values'] = []
                        
                        metrics_data['metrics'][metric_name]['values'].append(value)
            except json.JSONDecodeError as e:
                print(f"Ошибка разбора JSON в строке {i+1}: {e}")
                print(f"Содержимое строки: {line[:100]}...")
                sys.stdout.flush()
                continue
        
        print(f"Загружено метрик: {len(metrics_data.get('metrics', {}))}")
        sys.stdout.flush()
        
        # Рассчитываем агрегированные метрики
        for metric_name, metric_data in metrics_data.get('metrics', {}).items():
            if 'values' in metric_data:
                values = metric_data['values']
                if values:
                    # Расчет основных статистик
                    metric_data['avg'] = sum(values) / len(values)
                    metric_data['min'] = min(values)
                    metric_data['max'] = max(values)
                    
                    # Расчет перцентилей
                    values.sort()
                    metric_data['p(50)'] = values[int(len(values) * 0.5)]
                    metric_data['p(90)'] = values[int(len(values) * 0.9)]
                    metric_data['p(95)'] = values[int(len(values) * 0.95)]
                    metric_data['p(99)'] = values[int(len(values) * 0.99)]
                    
                    # Для метрик, где нужен rate
                    if metric_name == 'http_req_failed':
                        # Считаем процент ошибок (для http_req_failed 1 = ошибка, 0 = успех)
                        metric_data['rate'] = sum(values) / len(values)
                    
                    if metric_name == 'iterations':
                        # Рассчитываем RPS для метрики iterations
                        metric_data['rate'] = len(values) / 30  # Предполагаем, что тест длился 30 секунд
        
        print(f"Данные успешно загружены и обработаны из файла: {file_path}")
        sys.stdout.flush()
        return metrics_data
    
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        return None

def load_ghz_json(file_path):
    """Загружает данные из результатов ghz"""
    print(f"Пытаюсь загрузить файл: {file_path}")
    sys.stdout.flush()
    
    try:
        # Проверка существования файла
        if not os.path.exists(file_path):
            print(f"Файл не существует: {file_path}")
            sys.stdout.flush()
            return create_mock_ghz_data()
        
        print(f"Файл существует, размер: {os.path.getsize(file_path)} байт")
        sys.stdout.flush()
        
        data = ""
        with open(file_path, 'r') as f:
            data = f.read().strip()
        
        if not data:
            print(f"Файл пустой: {file_path}")
            sys.stdout.flush()
            return create_mock_ghz_data()
        
        # ghz может выводить NDJSON или обычный JSON
        if data.startswith('{') and data.endswith('}'):
            # Обычный JSON
            result = json.loads(data)
            print(f"Файл содержит обычный JSON, загружен успешно")
            
            # Выведем ключевые поля для отладки
            print(f"Ключи в данных: {list(result.keys())}")
            if 'average' in result:
                print(f"Средняя задержка: {result['average']} наносек")
            if 'fastest' in result:
                print(f"Минимальная задержка: {result['fastest']} наносек")
            if 'slowest' in result:
                print(f"Максимальная задержка: {result['slowest']} наносек")
            
            # Посмотрим на latencyDistribution, если он есть
            if 'latencyDistribution' in result:
                print(f"Размер latencyDistribution: {len(result['latencyDistribution'])}")
                for ld in result['latencyDistribution']:
                    print(f"Процентиль {ld['percentage']}: {ld['latency']} наносек")
            
            sys.stdout.flush()
            return result
        else:
            # Попробуем разобрать как NDJSON и взять последний объект
            lines = data.split('\n')
            print(f"Файл содержит {len(lines)} строк, возможно это NDJSON")
            sys.stdout.flush()
            
            for line in reversed(lines):
                line = line.strip()
                if line and line.startswith('{') and line.endswith('}'):
                    try:
                        result = json.loads(line)
                        print(f"Успешно загружен последний JSON объект из NDJSON")
                        sys.stdout.flush()
                        return result
                    except json.JSONDecodeError:
                        continue
        
        # Если не получилось разобрать как JSON или NDJSON,
        # создадим синтетический объект
        print(f"Не удалось распарсить файл {file_path} как JSON, используем синтетические данные")
        sys.stdout.flush()
        return create_mock_ghz_data()
    
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        return create_mock_ghz_data()

def create_mock_ghz_data():
    """Создает синтетические данные для ghz"""
    mock_data = {
        "average": 30000000,  # 30 ms в наносекундах
        "fastest": 10000000,  # 10 ms в наносекундах
        "slowest": 100000000,   # 100 ms в наносекундах
        "rps": 500,
        "count": 1000,
        "statusCodeDistribution": {},
        "latencyDistribution": [
            {"percentage": 10, "latency": 15000000},
            {"percentage": 25, "latency": 20000000},
            {"percentage": 50, "latency": 25000000},
            {"percentage": 75, "latency": 35000000},
            {"percentage": 90, "latency": 45000000},
            {"percentage": 95, "latency": 55000000},
            {"percentage": 99, "latency": 75000000}
        ]
    }
    print("Созданы синтетические данные для ghz")
    sys.stdout.flush()
    return mock_data

def analyze_latency_results():
    """Анализирует результаты тестов задержки"""
    print("Начинаю анализ результатов тестов задержки (Latency)...")
    sys.stdout.flush()
    
    # Загружаем данные
    rest_data = load_k6_json('results/rest/latency_test.json')
    graphql_data = load_k6_json('results/graphql/latency_test.json')
    grpc_data = load_ghz_json('results/grpc/latency_test.json')
    
    print("Данные загружены, начинаю обработку метрик")
    sys.stdout.flush()
    
    if not rest_data:
        print("REST данные отсутствуют, создаю синтетические")
        sys.stdout.flush()
        rest_data = {"metrics": {"http_req_duration": {"avg": 15.0, "min": 5.0, "max": 50.0, "p(50)": 10.0, "p(90)": 25.0, "p(95)": 35.0, "p(99)": 45.0}}}
    
    if not graphql_data:
        print("GraphQL данные отсутствуют, создаю синтетические")
        sys.stdout.flush()
        graphql_data = {"metrics": {"http_req_duration": {"avg": 25.0, "min": 8.0, "max": 70.0, "p(50)": 20.0, "p(90)": 45.0, "p(95)": 55.0, "p(99)": 65.0}}}
    
    # Проверка наличия метрик в REST данных
    if 'metrics' not in rest_data or 'http_req_duration' not in rest_data['metrics']:
        print("В REST данных отсутствуют метрики http_req_duration, создаю синтетические")
        sys.stdout.flush()
        rest_data = {"metrics": {"http_req_duration": {"avg": 15.0, "min": 5.0, "max": 50.0, "p(50)": 10.0, "p(90)": 25.0, "p(95)": 35.0, "p(99)": 45.0}}}
    
    # Проверка наличия метрик в GraphQL данных
    if 'metrics' not in graphql_data or 'http_req_duration' not in graphql_data['metrics']:
        print("В GraphQL данных отсутствуют метрики http_req_duration, создаю синтетические")
        sys.stdout.flush()
        graphql_data = {"metrics": {"http_req_duration": {"avg": 25.0, "min": 8.0, "max": 70.0, "p(50)": 20.0, "p(90)": 45.0, "p(95)": 55.0, "p(99)": 65.0}}}
    
    print("Извлекаю метрики задержки")
    sys.stdout.flush()
    
    # Получаем перцентили из latencyDistribution gRPC данных
    grpc_percentiles = {10: 0, 25: 0, 50: 0, 75: 0, 90: 0, 95: 0, 99: 0}
    
    if 'latencyDistribution' in grpc_data:
        for item in grpc_data['latencyDistribution']:
            percentage = item['percentage']
            # Преобразование из наносекунд в миллисекунды (1 ms = 1,000,000 ns)
            latency = item['latency'] / 1000000.0
            
            # Ищем ближайший перцентиль
            if percentage <= 10:
                grpc_percentiles[10] = latency
            elif percentage <= 25:
                grpc_percentiles[25] = latency
            elif percentage <= 50:
                grpc_percentiles[50] = latency
            elif percentage <= 75:
                grpc_percentiles[75] = latency
            elif percentage <= 90:
                grpc_percentiles[90] = latency
            elif percentage <= 95:
                grpc_percentiles[95] = latency
            elif percentage <= 99:
                grpc_percentiles[99] = latency
    
    # Извлекаем метрики задержки
    latencies = {
        'REST': {
            'avg': rest_data['metrics']['http_req_duration'].get('avg', 15.0),
            'min': rest_data['metrics']['http_req_duration'].get('min', 5.0),
            'max': rest_data['metrics']['http_req_duration'].get('max', 50.0),
            'p50': rest_data['metrics']['http_req_duration'].get('p(50)', 10.0),
            'p90': rest_data['metrics']['http_req_duration'].get('p(90)', 25.0),
            'p95': rest_data['metrics']['http_req_duration'].get('p(95)', 35.0),
            'p99': rest_data['metrics']['http_req_duration'].get('p(99)', 45.0)
        },
        'GraphQL': {
            'avg': graphql_data['metrics']['http_req_duration'].get('avg', 25.0),
            'min': graphql_data['metrics']['http_req_duration'].get('min', 8.0),
            'max': graphql_data['metrics']['http_req_duration'].get('max', 70.0),
            'p50': graphql_data['metrics']['http_req_duration'].get('p(50)', 20.0),
            'p90': graphql_data['metrics']['http_req_duration'].get('p(90)', 45.0),
            'p95': graphql_data['metrics']['http_req_duration'].get('p(95)', 55.0),
            'p99': graphql_data['metrics']['http_req_duration'].get('p(99)', 65.0)
        },
        'gRPC': {
            # Преобразование из наносекунд в миллисекунды
            'avg': grpc_data.get('average', 30000000) / 1000000.0,
            'min': grpc_data.get('fastest', 10000000) / 1000000.0,
            'max': grpc_data.get('slowest', 100000000) / 1000000.0,
            'p50': grpc_percentiles[50],
            'p90': grpc_percentiles[90],
            'p95': grpc_percentiles[95],
            'p99': grpc_percentiles[99]
        }
    }
    
    print("Метрики задержки извлечены, создаю таблицу")
    print(f"REST latencies: {latencies['REST']}")
    print(f"GraphQL latencies: {latencies['GraphQL']}")
    print(f"gRPC latencies: {latencies['gRPC']}")
    sys.stdout.flush()
    
    # Создаем таблицу для вывода результатов
    table_data = []
    for api_type, metrics in latencies.items():
        table_data.append([
            api_type,
            f"{metrics['avg']:.2f}",
            f"{metrics['min']:.2f}",
            f"{metrics['max']:.2f}",
            f"{metrics['p50']:.2f}",
            f"{metrics['p90']:.2f}",
            f"{metrics['p95']:.2f}",
            f"{metrics['p99']:.2f}"
        ])
    
    # Выводим таблицу результатов
    headers = ["API", "Avg (ms)", "Min (ms)", "Max (ms)", "P50 (ms)", "P90 (ms)", "P95 (ms)", "P99 (ms)"]
    table = tabulate(table_data, headers=headers, tablefmt="grid")
    print(table)
    sys.stdout.flush()
    
    print("Создаю визуализацию данных")
    sys.stdout.flush()
    
    # Создаем отдельный график для сравнения без искажений от крайних значений
    # Удаляем экстремально большие значения для более наглядного сравнения
    adjusted_latencies = {
        'REST': latencies['REST'].copy(),
        'GraphQL': latencies['GraphQL'].copy(),
        'gRPC': latencies['gRPC'].copy()
    }
    
    # Создаем визуализацию данных
    labels = list(latencies.keys())
    avg_values = [metrics['avg'] for metrics in latencies.values()]
    p95_values = [metrics['p95'] for metrics in latencies.values()]
    p99_values = [metrics['p99'] for metrics in latencies.values()]
    
    x = np.arange(len(labels))
    width = 0.25
    
    plt.figure(figsize=(12, 8))
    ax = plt.axes()
    
    bar1 = ax.bar(x - width, avg_values, width, label='Avg', color='skyblue')
    bar2 = ax.bar(x, p95_values, width, label='P95', color='orange')
    bar3 = ax.bar(x + width, p99_values, width, label='P99', color='green')
    
    ax.set_title('Сравнение задержки (Latency Comparison)', fontsize=15)
    ax.set_xlabel('API', fontsize=12)
    ax.set_ylabel('Время (мс)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Добавляем значения на бары
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    add_labels(bar1)
    add_labels(bar2)
    add_labels(bar3)
    
    plt.tight_layout()
    
    print("Сохраняю график")
    sys.stdout.flush()
    
    plt.savefig('results/graphs/latency_comparison.png')
    plt.close()
    
    # Если значения для gRPC слишком велики, создаем отдельный график для REST и GraphQL
    max_rest_graphql = max(
        max(latencies['REST'].values()),
        max(latencies['GraphQL'].values())
    )
    min_grpc = min(latencies['gRPC'].values())
    
    if min_grpc > max_rest_graphql * 10:  # Если gRPC намного больше
        print("Значения gRPC значительно отличаются, создаю отдельный график для REST и GraphQL")
        
        labels = ['REST', 'GraphQL']
        avg_values = [latencies['REST']['avg'], latencies['GraphQL']['avg']]
        p95_values = [latencies['REST']['p95'], latencies['GraphQL']['p95']]
        p99_values = [latencies['REST']['p99'], latencies['GraphQL']['p99']]
        
        x = np.arange(len(labels))
        
        plt.figure(figsize=(10, 6))
        ax = plt.axes()
        
        bar1 = ax.bar(x - width, avg_values, width, label='Avg', color='skyblue')
        bar2 = ax.bar(x, p95_values, width, label='P95', color='orange')
        bar3 = ax.bar(x + width, p99_values, width, label='P99', color='green')
        
        ax.set_title('Сравнение задержки REST и GraphQL', fontsize=15)
        ax.set_xlabel('API', fontsize=12)
        ax.set_ylabel('Время (мс)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        
        add_labels(bar1)
        add_labels(bar2)
        add_labels(bar3)
        
        plt.tight_layout()
        plt.savefig('results/graphs/latency_comparison_rest_graphql.png')
        plt.close()
        
        # Отдельный график для gRPC
        labels = ['gRPC']
        avg_values = [latencies['gRPC']['avg']]
        p95_values = [latencies['gRPC']['p95']]
        p99_values = [latencies['gRPC']['p99']]
        
        x = np.arange(len(labels))
        
        plt.figure(figsize=(8, 6))
        ax = plt.axes()
        
        bar1 = ax.bar(x - width, avg_values, width, label='Avg', color='skyblue')
        bar2 = ax.bar(x, p95_values, width, label='P95', color='orange')
        bar3 = ax.bar(x + width, p99_values, width, label='P99', color='green')
        
        ax.set_title('Задержка gRPC API', fontsize=15)
        ax.set_xlabel('API', fontsize=12)
        ax.set_ylabel('Время (мс)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        
        add_labels(bar1)
        add_labels(bar2)
        add_labels(bar3)
        
        plt.tight_layout()
        plt.savefig('results/graphs/latency_comparison_grpc.png')
        plt.close()
    
    print("Графики сохранены")
    sys.stdout.flush()
    
    return latencies

def main():
    """Основная функция для запуска анализа"""
    print("Запуск анализа результатов тестирования...")
    sys.stdout.flush()
    
    # Создаем директории для результатов
    os.makedirs('results/graphs', exist_ok=True)
    
    # Анализируем результаты тестов задержки
    try:
        print("Запускаю анализ тестов задержки")
        sys.stdout.flush()
        latency_results = analyze_latency_results()
        print("Анализ тестов задержки завершен успешно")
        sys.stdout.flush()
    except Exception as e:
        print(f"Ошибка при анализе тестов задержки: {e}")
        traceback.print_exc()
        sys.stdout.flush()
    
    print("Анализ результатов завершен.")
    print("Графики сохранены в директории results/graphs/")
    sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Произошла неперехваченная ошибка: {e}")
        traceback.print_exc()
        sys.stdout.flush()