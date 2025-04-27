import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

// Пользовательские метрики
const minimalQueryDuration = new Trend('minimal_query_duration');
const fullQueryDuration = new Trend('full_query_duration');
const errorCounter = new Counter('errors');

export const options = {
  vus: 1, // Один виртуальный пользователь
  iterations: 50, // 50 итераций
};

// Минимальный запрос (только ID и имя)
const minimalQuery = `
query {
  users {
    id
    name
  }
}
`;

// Полный запрос (все поля)
const fullQuery = `
query {
  users {
    id
    name
    email
    created_at
  }
}
`;

export default function () {
  // Отправляем минимальный запрос
  const minimalResponse = http.post(`${__ENV.GRAPHQL_API_URL}`, 
    JSON.stringify({ query: minimalQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  check(minimalResponse, {
    'minimal query status was 200': (r) => r.status === 200,
    'minimal query response has no errors': (r) => !JSON.parse(r.body).errors,
  });
  
  minimalQueryDuration.add(minimalResponse.timings.duration);
  
  // Отправляем полный запрос
  const fullResponse = http.post(`${__ENV.GRAPHQL_API_URL}`, 
    JSON.stringify({ query: fullQuery }), 
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  check(fullResponse, {
    'full query status was 200': (r) => r.status === 200,
    'full query response has no errors': (r) => !JSON.parse(r.body).errors,
  });
  
  fullQueryDuration.add(fullResponse.timings.duration);
  
  // Сравниваем размеры ответов
  const minimalSize = JSON.stringify(JSON.parse(minimalResponse.body).data).length;
  const fullSize = JSON.stringify(JSON.parse(fullResponse.body).data).length;
  
  console.log(`Minimal query response size: ${minimalSize} bytes`);
  console.log(`Full query response size: ${fullSize} bytes`);
  console.log(`Difference: ${fullSize - minimalSize} bytes (${Math.round((fullSize - minimalSize) / fullSize * 100)}%)`);
  
  // Добавляем задержку в 1 секунду между итерациями
  sleep(1);
}