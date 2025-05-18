# Сравнение API

docker compose -f 

# Внутри контейнера
cd /tests
chmod +x run-tests.sh
./run-tests.sh

# Или запускать отдельные тесты
k6 run k6-scripts/rest_latency_test.js --out json=results/rest/latency_test.json