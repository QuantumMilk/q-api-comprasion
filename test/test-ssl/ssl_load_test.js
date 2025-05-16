import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Метрики
export let latency = new Trend('latency');
export let throughput = new Counter('throughput');
export let errorRate = new Rate('errors');
export let overfetchBytes = new Trend('overfetching_bytes');

const BASE_URL = 'https://127.0.0.1:8443';

export let options = {
    vus: 20,
    duration: '30s',
    insecureSkipTLSVerify: true,
};

// Вспомогательная функция для оценки overfetching
function estimateOverfetch(response, expectedKeys) {
    try {
        const json = response.json();
        const fullLength = JSON.stringify(json).length;
        const slimLength = JSON.stringify(
            Array.isArray(json)
                ? json.map(item => Object.fromEntries(expectedKeys.map(k => [k, item[k]])))
                : Object.fromEntries(expectedKeys.map(k => [k, json[k]]))
        ).length;
        return fullLength - slimLength;
    } catch (_) {
        return 0;
    }
}

// Глобальные переменные
let userId = null;
let orderId = null;

export default function () {
    // ➤ POST /users
    group('POST /users', () => {
        const payload = JSON.stringify({
            name: `TestUser_${__VU}_${__ITER}`,
            email: `user${Math.floor(Math.random() * 10000)}@test-restapi.com`,
        });

        const res = http.post(`${BASE_URL}/users/`, payload, {
            headers: { 'Content-Type': 'application/json' },
        });

        const ok = check(res, {
            'POST /users status 200': (r) => r.status === 200,
            'user ID exists': (r) => r.json().id !== undefined,
        });

        if (ok) userId = res.json().id;

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    // ➤ GET /users
    group('GET /users', () => {
        const res = http.get(`${BASE_URL}/users/`);

        const ok = check(res, {
            'GET /users status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    // ➤ POST /orders
    group('POST /orders', () => {
        if (userId === null) return;

        const payload = JSON.stringify({
            user_id: userId,
            product_name: 'TestProduct',
            price: 99.99,
        });

        const res = http.post(`${BASE_URL}/orders/`, payload, {
            headers: { 'Content-Type': 'application/json' },
        });

        const ok = check(res, {
            'POST /orders status 200': (r) => r.status === 200,
            'order ID exists': (r) => r.json().id !== undefined,
        });

        if (ok) orderId = res.json().id;

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'user_id', 'product_name', 'price']));
    });

    // ➤ GET /orders
    group('GET /orders', () => {
        const res = http.get(`${BASE_URL}/orders/`);

        const ok = check(res, {
            'GET /orders status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'user_id', 'product_name', 'price']));
    });

    // ➤ GET /orders/user/{user_id}
    group('GET /orders/user/{user_id}', () => {
        if (userId === null) return;

        const res = http.get(`${BASE_URL}/orders/user/${userId}`);

        const ok = check(res, {
            'GET /orders/user/{id} status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'user_id', 'product_name', 'price']));
    });

    // ➤ DELETE /orders/{order_id}
    group('DELETE /orders/{order_id}', () => {
        if (orderId === null) return;

        const res = http.del(`${BASE_URL}/orders/${orderId}`);

        const ok = check(res, {
            'DELETE /orders/{id} status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
    });

    // ➤ DELETE /users/{user_id}
    group('DELETE /users/{user_id}', () => {
        if (userId === null) return;

        const res = http.del(`${BASE_URL}/users/${userId}`);

        const ok = check(res, {
            'DELETE /users/{id} status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
    });

    sleep(1);
}
