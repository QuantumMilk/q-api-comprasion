import http from 'k6/http';
import { check } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Пользовательские метрики
const successRate = new Rate('success_rate');
const errorCounter = new Counter('errors');
const reqRate = new Rate('req_rate');

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

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 100, // 100 запросов в секунду
      timeUnit: '1s',
      duration: '30s', // Продолжительность теста - 30 секунд
      preAllocatedVUs: 20, // Начальное количество VU
      maxVUs: 100, // Максимальное количество VU
    },
  },
  thresholds: {
    success_rate: ['rate>0.95'], // Успешных запросов должно быть более 95%
    http_req_duration: ['p(95)<1000'], // 95% запросов должны быть быстрее 1000 мс
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
  
  // Увеличиваем счетчик запросов
  reqRate.add(1);
  
  // Если запрос не успешен, увеличиваем счетчик ошибок
  if (!usersSuccess) {
    errorCounter.add(1);
  }
}