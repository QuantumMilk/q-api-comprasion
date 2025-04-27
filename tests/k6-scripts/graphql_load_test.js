import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Пользовательские метрики
const successRate = new Rate('success_rate');
const errorCounter = new Counter('errors');

// Запрос на получение всех пользователей
const usersQuery = `
query {
  users {
    id
    name
    email
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
  }
}
`;

export const options = {
  stages: [
    { duration: '30s', target: 1 }, // 1 пользователь в течение 30 секунд
    { duration: '30s', target: 10 }, // 10 пользователей в течение 30 секунд
    { duration: '30s', target: 50 }, // 50 пользователей в течение 30 секунд
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // Менее 1% ошибок
    http_req_duration: ['p(95)<1000'], // 95% запросов должны быть быстрее 1000 мс
    success_rate: ['rate>0.95'], // Успешных запросов должно быть более 95%
  },
};

export default function () {
  // Отправляем запрос на получение списка пользователей
  const usersResponse = http.post(`${__ENV.GRAPHQL_API_URL}`, 
    JSON.stringify({ query: usersQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  // Проверяем успешность запроса
  const usersSuccess = check(usersResponse, {
    'users status was 200': (r) => r.status === 200,
    'users response has no errors': (r) => !JSON.parse(r.body).errors,
  });
  
  // Увеличиваем счетчик успешных запросов
  successRate.add(usersSuccess);
  
  // Если запрос не успешен, увеличиваем счетчик ошибок
  if (!usersSuccess) {
    errorCounter.add(1);
  }
  
  // Отправляем запрос на получение списка заказов
  const ordersResponse = http.post(`${__ENV.GRAPHQL_API_URL}`, 
    JSON.stringify({ query: ordersQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  // Проверяем успешность запроса
  const ordersSuccess = check(ordersResponse, {
    'orders status was 200': (r) => r.status === 200,
    'orders response has no errors': (r) => !JSON.parse(r.body).errors,
  });
  
  // Увеличиваем счетчик успешных запросов
  successRate.add(ordersSuccess);
  
  // Если запрос не успешен, увеличиваем счетчик ошибок
  if (!ordersSuccess) {
    errorCounter.add(1);
  }
  
  // Добавляем небольшую задержку между запросами
  sleep(1);
}