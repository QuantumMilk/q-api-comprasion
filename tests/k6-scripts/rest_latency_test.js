import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

// Пользовательские метрики
const userLatencies = new Trend('user_latencies');
const usersReqDuration = new Trend('users_req_duration');
const ordersReqDuration = new Trend('orders_req_duration');
const errorCounter = new Counter('errors');

export const options = {
  vus: 1, // Один виртуальный пользователь
  iterations: 100, // 100 итераций
  thresholds: {
    // Пороговые значения для успешного прохождения теста
    http_req_duration: ['p(95)<500'], // 95% запросов должны быть быстрее 500 мс
    errors: ['count<1'], // Ошибок быть не должно
  },
};

export default function () {
  // Запрос на получение списка пользователей
  const usersResponse = http.get(`${__ENV.REST_API_URL}/users/`);
  
  check(usersResponse, {
    'users status was 200': (r) => r.status === 200,
    'users response has users array': (r) => Array.isArray(JSON.parse(r.body)),
  });
  
  usersReqDuration.add(usersResponse.timings.duration);
  
  // Запрос на получение списка заказов
  const ordersResponse = http.get(`${__ENV.REST_API_URL}/orders/`);
  
  check(ordersResponse, {
    'orders status was 200': (r) => r.status === 200,
    'orders response has orders array': (r) => Array.isArray(JSON.parse(r.body)),
  });
  
  ordersReqDuration.add(ordersResponse.timings.duration);
  
  // Добавляем задержку в 1 секунду между итерациями
  sleep(1);
}