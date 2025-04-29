#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import datetime
import pandas as pd
from jinja2 import Template

def generate_html_report():
    """Генерирует HTML-отчет на основе результатов тестирования"""
    
    print("Генерация HTML-отчета...")
    
    # Создаем директорию для отчета
    report_dir = 'report'
    os.makedirs(report_dir, exist_ok=True)
    
    # Копируем графики в директорию отчета
    if os.path.exists('results/graphs'):
        if not os.path.exists(f'{report_dir}/graphs'):
            os.makedirs(f'{report_dir}/graphs', exist_ok=True)
        
        # Копируем все файлы из директории graphs
        for graph_file in os.listdir('results/graphs'):
            if graph_file.endswith('.png'):
                os.system(f'cp results/graphs/{graph_file} {report_dir}/graphs/')
    
    # Читаем summary.txt если он существует
    summary_text = "Сводная информация не найдена"
    if os.path.exists('results/summary.txt'):
        with open('results/summary.txt', 'r') as f:
            summary_text = f.read()
    
    # Создаем HTML шаблон
    template_str = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сравнение API технологий - Отчет</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 0;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }
        h1, h2, h3 { color: #2c3e50; }
        header h1 { 
            color: white; 
            margin: 0;
        }
        .timestamp {
            color: #7f8c8d;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .section {
            margin-bottom: 40px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        .results { margin-top: 20px; }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        img { 
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        pre { 
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #ddd;
            font-family: monospace;
            font-size: 0.9em;
        }
        table { 
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td { 
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th { 
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) { background-color: #f9f9f9; }
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .api-comparison {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 20px 0;
        }
        .api-card {
            flex: 0 0 30%;
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .api-card h3 {
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        @media (max-width: 768px) {
            .api-card {
                flex: 0 0 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Сравнение API технологий</h1>
        <div class="timestamp">Отчет сгенерирован: {{ date }}</div>
    </header>
    
    <div class="container">
        <div class="section">
            <h2>Обзор результатов тестирования</h2>
            <p>
                Этот отчет содержит результаты сравнительного анализа трех типов API:
                REST, GraphQL и gRPC. Сравнение было проведено по трем ключевым метрикам:
                задержка (latency), пропускная способность (throughput) и поведение под нагрузкой (load).
            </p>
            
            <div class="api-comparison">
                <div class="api-card">
                    <h3>REST API</h3>
                    <p>Традиционный подход к разработке API с использованием HTTP методов.</p>
                    <p><strong>Преимущества:</strong> Широкая поддержка, простота, кеширование.</p>
                    <p><strong>Недостатки:</strong> Проблемы с недостаточной и избыточной выборкой данных.</p>
                </div>
                
                <div class="api-card">
                    <h3>GraphQL API</h3>
                    <p>Язык запросов и среда выполнения для API, разработанный Facebook.</p>
                    <p><strong>Преимущества:</strong> Гибкость запросов, единая точка входа.</p>
                    <p><strong>Недостатки:</strong> Сложность кеширования, проблемы с оптимизацией.</p>
                </div>
                
                <div class="api-card">
                    <h3>gRPC API</h3>
                    <p>Высокопроизводительная система удаленного вызова процедур, разработанная Google.</p>
                    <p><strong>Преимущества:</strong> Высокая производительность, строгие контракты.</p>
                    <p><strong>Недостатки:</strong> Менее поддерживается браузерами, сложная настройка.</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Сводная информация</h2>
            <pre>{{ summary }}</pre>
        </div>
        
        <div class="section">
            <h2>Сравнение задержки (Latency)</h2>
            <p>
                Задержка – это время, которое требуется системе для обработки одного запроса.
                Меньшее значение означает более быстрый отклик API.
            </p>
            <div class="chart-container">
                <img src="graphs/latency_comparison.png" alt="Сравнение задержки" />
            </div>
        </div>
        
        <div class="section">
            <h2>Сравнение пропускной способности (Throughput)</h2>
            <p>
                Пропускная способность – это количество запросов, которое система может обработать в единицу времени.
                Более высокое значение RPS (запросов в секунду) означает лучшую производительность.
            </p>
            <div class="chart-container">
                <img src="graphs/throughput_comparison.png" alt="Сравнение пропускной способности" />
                <img src="graphs/success_rate_comparison.png" alt="Сравнение успешности запросов" 
                     onerror="this.style.display='none'" />
            </div>
        </div>
        
        <div class="section">
            <h2>Сравнение поведения под нагрузкой (Load)</h2>
            <p>
                Это сравнение показывает, как API справляется с увеличением нагрузки.
                Мы измеряли время отклика при 1, 10 и 50 одновременных пользователях.
            </p>
            <div class="chart-container">
                <img src="graphs/load_comparison.png" alt="Сравнение под нагрузкой" />
            </div>
            
            <h3>Рост задержки при увеличении нагрузки</h3>
            <div class="chart-container">
                <img src="graphs/load_growth_comparison.png" alt="Рост задержки при увеличении нагрузки" 
                     onerror="this.style.display='none'" />
                <img src="graphs/load_normalized_growth_comparison.png" alt="Относительный рост задержки" 
                     onerror="this.style.display='none'" />
            </div>
        </div>
        
        <div class="section">
            <h2>Общее сравнение всех метрик</h2>
            <div class="chart-container">
                <img src="graphs/summary_comparison.png" alt="Сводное сравнение" 
                     onerror="this.style.display='none'" />
            </div>
        </div>
        
        <div class="section">
            <h2>Выводы и рекомендации</h2>
            <p>
                На основе проведенных тестов можно сделать следующие выводы:
            </p>
            <ul>
                <li><strong>REST API</strong> показывает хорошие результаты для простых операций чтения и имеет широкую поддержку.</li>
                <li><strong>GraphQL API</strong> предоставляет большую гибкость при запросах данных, но может иметь более высокую задержку.</li>
                <li><strong>gRPC API</strong> обычно демонстрирует наилучшую производительность, особенно под высокой нагрузкой, но имеет более высокий порог входа.</li>
            </ul>
            
            <p>
                <strong>Рекомендации по выбору:</strong>
            </p>
            <ul>
                <li>Для публичных API с разнородными клиентами: <strong>REST</strong> или <strong>GraphQL</strong></li>
                <li>Для микросервисной архитектуры с высокой нагрузкой: <strong>gRPC</strong></li>
                <li>Для клиентских приложений с переменными требованиями к данным: <strong>GraphQL</strong></li>
            </ul>
        </div>
        
        <footer>
            <p>Отчет сгенерирован автоматически системой CI/CD</p>
            <p>© {{ year }} API Comparison Project</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Формируем данные для шаблона
    now = datetime.datetime.now()
    template_data = {
        'date': now.strftime('%d.%m.%Y %H:%M:%S'),
        'year': now.year,
        'summary': summary_text
    }
    
    # Рендерим шаблон
    template = Template(template_str)
    html = template.render(**template_data)
    
    # Записываем HTML отчет
    with open(f'{report_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML-отчет успешно сгенерирован в директории {report_dir}")
    return True

if __name__ == "__main__":
    try:
        generate_html_report()
    except Exception as e:
        print(f"Ошибка при генерации отчета: {e}")
        sys.exit(1)