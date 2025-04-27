#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

# Создаем директории для результатов и графиков, если они не существуют
os.makedirs('results/rest', exist_ok=True)
os.makedirs('results/graphql', exist_ok=True)
os.makedirs('results/grpc', exist_ok=True)
os.makedirs('results/graphs', exist_ok=True)

def load_k6_json(file_path):
    """Загружает данные из результатов k6"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
        return None

def load_ghz_json(file_path):
    """Загружает данные из результатов ghz"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
        return None

def analyze_latency_results():
    """Анализирует результаты тестов задержки"""
    print("Анализ результатов тестов задержки (Latency)...")
    
    # Загружаем данные
    rest_data = load_k6_json('results/rest/latency_test.json')
    graphql_data = load_k6_json('results/graphql/latency_test.json')
    grpc_data = load_ghz_json('results/grpc/latency_test.json')
    
    if not all([rest_data, graphql_data, grpc_data]):
        print("Ошибка: не все данные были загружены.")
        return
    
    # Извлекаем метрики задержки
    latencies = {
        'REST': {
            'avg': rest_data['metrics']['http_req_duration']['avg'],
            'min': rest_data['metrics']['http_req_duration']['min'],
            'max': rest_data['metrics']['http_req_duration']['max'],
            'p50': rest_data['metrics']['http_req_duration']['p(50)'],
            'p90': rest_data['metrics']['http_req_duration']['p(90)'],
            'p95': rest_data['metrics']['http_req_duration']['p(95)'],
            'p99': rest_data['metrics']['http_req_duration']['p(99)']
        },
        'GraphQL': {
            'avg': graphql_data['metrics']['http_req_duration']['avg'],
            'min': graphql_data['metrics']['http_req_duration']['min'],
            'max': graphql_data['metrics']['http_req_duration']['max'],
            'p50': graphql_data['metrics']['http_req_duration']['p(50)'],
            'p90': graphql_data['metrics']['http_req_duration']['p(90)'],
            'p95': graphql_data['metrics']['http_req_duration']['p(95)'],
            'p99': graphql_data['metrics']['http_req_duration']['p(99)']
        },
        'gRPC': {
            'avg': grpc_data['average'] * 1000,  # ghz использует секунды, переводим в миллисекунды
            'min': grpc_data['fastest'] * 1000,
            'max': grpc_data['slowest'] * 1000,
            'p50': grpc_data['latencyDistribution'][2]['value'] * 1000,  # предполагаем, что 3-й элемент - P50
            'p90': grpc_data['latencyDistribution'][4]['value'] * 1000,  # предполагаем, что 5-й элемент - P90
            'p95': grpc_data['latencyDistribution'][5]['value'] * 1000,  # предполагаем, что 6-й элемент - P95
            'p99': grpc_data['latencyDistribution'][6]['value'] * 1000   # предполагаем, что 7-й элемент - P99
        }
    }
    
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
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Создаем визуализацию данных
    labels = list(latencies.keys())
    avg_values = [metrics['avg'] for metrics in latencies.values()]
    p95_values = [metrics['p95'] for metrics in latencies.values()]
    p99_values = [metrics['p99'] for metrics in latencies.values()]
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 8))
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
    plt.savefig('results/graphs/latency_comparison.png')
    plt.close()
    
    print("График сохранен в results/graphs/latency_comparison.png")
    
    return latencies

def analyze_throughput_results():
    """Анализирует результаты тестов пропускной способности"""
    print("Анализ результатов тестов пропускной способности (Throughput)...")
    
    # Загружаем данные
    rest_data = load_k6_json('results/rest/throughput_test.json')
    graphql_data = load_k6_json('results/graphql/throughput_test.json')
    grpc_data = load_ghz_json('results/grpc/throughput_test.json')
    
    if not all([rest_data, graphql_data, grpc_data]):
        print("Ошибка: не все данные были загружены.")
        return
    
    # Извлекаем метрики пропускной способности
    throughput = {
        'REST': {
            'rps': rest_data['metrics']['iterations']['rate'],
            'success_rate': 1 - rest_data['metrics']['http_req_failed']['rate'],
            'avg_duration': rest_data['metrics']['http_req_duration']['avg'],
            'p95_duration': rest_data['metrics']['http_req_duration']['p(95)']
        },
        'GraphQL': {
            'rps': graphql_data['metrics']['iterations']['rate'],
            'success_rate': 1 - graphql_data['metrics']['http_req_failed']['rate'],
            'avg_duration': graphql_data['metrics']['http_req_duration']['avg'],
            'p95_duration': graphql_data['metrics']['http_req_duration']['p(95)']
        },
        'gRPC': {
            'rps': grpc_data['rps'],
            'success_rate': 1 - (grpc_data['statusCodeDistribution']['1'] / grpc_data['count'] if '1' in grpc_data['statusCodeDistribution'] else 0),
            'avg_duration': grpc_data['average'] * 1000,  # переводим в миллисекунды
            'p95_duration': grpc_data['latencyDistribution'][5]['value'] * 1000  # P95
        }
    }
    
    # Создаем таблицу для вывода результатов
    table_data = []
    for api_type, metrics in throughput.items():
        table_data.append([
            api_type,
            f"{metrics['rps']:.2f}",
            f"{metrics['success_rate'] * 100:.2f}%",
            f"{metrics['avg_duration']:.2f}",
            f"{metrics['p95_duration']:.2f}"
        ])
    
    # Выводим таблицу результатов
    headers = ["API", "RPS", "Success Rate", "Avg Duration (ms)", "P95 Duration (ms)"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Создаем визуализацию данных
    labels = list(throughput.keys())
    rps_values = [metrics['rps'] for metrics in throughput.values()]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, rps_values, color=['skyblue', 'orange', 'green'])
    
    ax.set_title('Сравнение пропускной способности (Throughput Comparison)', fontsize=15)
    ax.set_xlabel('API', fontsize=12)
    ax.set_ylabel('Запросов в секунду (RPS)', fontsize=12)
    
    # Добавляем значения на бары
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('results/graphs/throughput_comparison.png')
    plt.close()
    
    print("График сохранен в results/graphs/throughput_comparison.png")
    
    return throughput

def analyze_load_results():
    """Анализирует результаты тестов поведения под нагрузкой"""
    print("Анализ результатов тестов поведения под нагрузкой (Load)...")
    
    # Загружаем данные для REST API
    rest_1vu = load_k6_json('results/rest/load_test_stage1.json')
    rest_10vu = load_k6_json('results/rest/load_test_stage2.json')
    rest_50vu = load_k6_json('results/rest/load_test_stage3.json')
    
    # Загружаем данные для GraphQL API
    graphql_1vu = load_k6_json('results/graphql/load_test_stage1.json')
    graphql_10vu = load_k6_json('results/graphql/load_test_stage2.json')
    graphql_50vu = load_k6_json('results/graphql/load_test_stage3.json')
    
    # Загружаем данные для gRPC API
    grpc_1vu = load_ghz_json('results/grpc/load_test_1vu.json')
    grpc_10vu = load_ghz_json('results/grpc/load_test_10vu.json')
    grpc_50vu = load_ghz_json('results/grpc/load_test_50vu.json')
    
    # Проверяем, загружены ли все данные
    rest_data = [rest_1vu, rest_10vu, rest_50vu]
    graphql_data = [graphql_1vu, graphql_10vu, graphql_50vu]
    grpc_data = [grpc_1vu, grpc_10vu, grpc_50vu]
    
    if not all(rest_data) or not all(graphql_data) or not all(grpc_data):
        print("Ошибка: не все данные были загружены.")
        return
    
    # Извлекаем метрики поведения под нагрузкой
    # Для этого мы будем сравнивать P95 задержки при разной нагрузке
    
    load_comparison = {
        'REST': {
            '1 VU': rest_1vu['metrics']['http_req_duration']['p(95)'],
            '10 VU': rest_10vu['metrics']['http_req_duration']['p(95)'],
            '50 VU': rest_50vu['metrics']['http_req_duration']['p(95)']
        },
        'GraphQL': {
            '1 VU': graphql_1vu['metrics']['http_req_duration']['p(95)'],
            '10 VU': graphql_10vu['metrics']['http_req_duration']['p(95)'],
            '50 VU': graphql_50vu['metrics']['http_req_duration']['p(95)']
        },
        'gRPC': {
            '1 VU': grpc_1vu['latencyDistribution'][5]['value'] * 1000,  # переводим в миллисекунды
            '10 VU': grpc_10vu['latencyDistribution'][5]['value'] * 1000,
            '50 VU': grpc_50vu['latencyDistribution'][5]['value'] * 1000
        }
    }
    
    # Создаем таблицу для вывода результатов
    table_data = []
    for api_type, metrics in load_comparison.items():
        table_data.append([
            api_type,
            f"{metrics['1 VU']:.2f}",
            f"{metrics['10 VU']:.2f}",
            f"{metrics['50 VU']:.2f}"
        ])
    
    # Выводим таблицу результатов
    headers = ["API", "1 VU (P95, ms)", "10 VU (P95, ms)", "50 VU (P95, ms)"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Создаем визуализацию данных
    labels = ['1 VU', '10 VU', '50 VU']
    rest_values = [load_comparison['REST'][label] for label in labels]
    graphql_values = [load_comparison['GraphQL'][label] for label in labels]
    grpc_values = [load_comparison['gRPC'][label] for label in labels]
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bar1 = ax.bar(x - width, rest_values, width, label='REST', color='skyblue')
    bar2 = ax.bar(x, graphql_values, width, label='GraphQL', color='orange')
    bar3 = ax.bar(x + width, grpc_values, width, label='gRPC', color='green')
    
    ax.set_title('Сравнение поведения под нагрузкой (Load Comparison)', fontsize=15)
    ax.set_xlabel('Количество виртуальных пользователей', fontsize=12)
    ax.set_ylabel('Задержка P95 (мс)', fontsize=12)
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
    plt.savefig('results/graphs/load_comparison.png')
    plt.close()
    
    print("График сохранен в results/graphs/load_comparison.png")
    
    return load_comparison

def analyze_graphql_overfetching():
    """Анализирует результаты тестов GraphQL на overfetching/underfetching"""
    print("Анализ результатов тестов GraphQL на overfetching/underfetching...")
    
    # Загружаем данные
    graphql_overfetching = load_k6_json('results/graphql/overfetching_test.json')
    
    if not graphql_overfetching:
        print("Ошибка: данные не были загружены.")
        return
    
    # Извлекаем метрики
    minimal_duration = graphql_overfetching['metrics']['minimal_query_duration']['avg']
    full_duration = graphql_overfetching['metrics']['full_query_duration']['avg']
    
    # Создаем таблицу для вывода результатов
    table_data = [
        ["Минимальный запрос (только ID и имя)", f"{minimal_duration:.2f}"],
        ["Полный запрос (все поля)", f"{full_duration:.2f}"],
        ["Разница", f"{full_duration - minimal_duration:.2f}"],
        ["Процентная разница", f"{((full_duration - minimal_duration) / minimal_duration * 100):.2f}%"]
    ]
    
    # Выводим таблицу результатов
    headers = ["Тип запроса", "Среднее время выполнения (мс)"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Создаем визуализацию данных
    labels = ['Минимальный запрос', 'Полный запрос']
    values = [minimal_duration, full_duration]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['lightblue', 'orange'])
    
    ax.set_title('Анализ GraphQL Overfetching', fontsize=15)
    ax.set_xlabel('Тип запроса', fontsize=12)
    ax.set_ylabel('Среднее время выполнения (мс)', fontsize=12)
    
    # Добавляем значения на бары
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('results/graphs/graphql_overfetching.png')
    plt.close()
    
    print("График сохранен в results/graphs/graphql_overfetching.png")
    
    return {
        'minimal_duration': minimal_duration,
        'full_duration': full_duration,
        'difference': full_duration - minimal_duration,
        'percentage_difference': (full_duration - minimal_duration) / minimal_duration * 100
    }

def main():
    """Основная функция для запуска анализа"""
    print("Запуск анализа результатов тестирования...")
    
    # Создаем директории для результатов
    os.makedirs('results/graphs', exist_ok=True)
    
    # Анализируем результаты тестов задержки
    latency_results = analyze_latency_results()
    print()
    
    # Анализируем результаты тестов пропускной способности
    throughput_results = analyze_throughput_results()
    print()
    
    # Анализируем результаты тестов поведения под нагрузкой
    load_results = analyze_load_results()
    print()
    
    # Анализируем результаты тестов GraphQL на overfetching/underfetching
    overfetching_results = analyze_graphql_overfetching()
    print()
    
    print("Анализ результатов завершен.")
    print("Графики сохранены в директории results/graphs/")

if __name__ == "__main__":
    main()