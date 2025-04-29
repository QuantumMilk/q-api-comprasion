import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// Пользовательские метрики
const successRate = new Rate('success_rate');
const errorCounter = new Counter('errors');

// Убираем многоэтапную конфигурацию, вместо этого используем параметры запуска
export const options = {
  thresholds: {
    http_req_failed: ['rate<0.01'], // Менее 1% ошибок
    http_req_duration: ['p(95)<1000'], // 95% запросов должны быть быстрее 1000 мс
    success_rate: ['rate>0.95'], // Успешных запросов должно быть более 95%
  },
};

export default function () {
  // Запрос на получение списка пользователей
  const usersResponse = http.get(`${__ENV.REST_API_URL}/users/`);
  
  // Проверяем успешность запроса
  const usersSuccess = check(usersResponse, {
    'users status was 200': (r) => r.status === 200,
  });
  
  // Увеличиваем счетчик успешных запросов
  successRate.add(usersSuccess);
  
  // Если запрос не успешен, увеличиваем счетчик ошибок
  if (!usersSuccess) {
    errorCounter.add(1);
  }
  
  // Запрос на получение списка заказов
  const ordersResponse = http.get(`${__ENV.REST_API_URL}/orders/`);
  
  // Проверяем успешность запроса
  const ordersSuccess = check(ordersResponse, {
    'orders status was 200': (r) => r.status === 200,
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