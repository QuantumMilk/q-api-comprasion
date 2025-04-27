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

// Запрос на получение всех пользователей
const usersQuery = `
query {
  users {
    id
    name
    email
    created_at
  }
}
`;

// Запрос на получение всех заказов
const ordersQuery = `
query {
  orders {
    id
    user_id
    product_name
    price
    created_at
  }
}
`;

export default function () {
  // Отправляем запрос на получение списка пользователей
  const usersResponse = http.post('http://localhost:8080/graphql', 
    JSON.stringify({ query: usersQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  check(usersResponse, {
    'users status was 200': (r) => r.status === 200,
    'users response has no errors': (r) => !JSON.parse(r.body).errors,
    'users response has data': (r) => JSON.parse(r.body).data,
  });
  
  usersReqDuration.add(usersResponse.timings.duration);
  
  // Отправляем запрос на получение списка заказов
  const ordersResponse = http.post('http://localhost:8080/graphql', 
    JSON.stringify({ query: ordersQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  check(ordersResponse, {
    'orders status was 200': (r) => r.status === 200,
    'orders response has no errors': (r) => !JSON.parse(r.body).errors,
    'orders response has data': (r) => JSON.parse(r.body).data,
  });
  
  ordersReqDuration.add(ordersResponse.timings.duration);
  
  // Добавляем задержку в 1 секунду между итерациями
  sleep(1);
}