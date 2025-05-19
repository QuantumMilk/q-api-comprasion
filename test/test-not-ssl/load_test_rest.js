import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Метрики
export let latency = new Trend('latency', true); // enable percentiles
export let throughput = new Counter('throughput');
export let errorRate = new Rate('errors');
export let overfetchBytes = new Trend('overfetching_bytes');
export let ttfb = new Trend('ttfb', true); // enable percentiles


const BASE_URL = 'http://127.0.0.1:8000';

export let options = {
    scenarios: {
        latency_test: {
            executor: 'per-vu-iterations',
            vus: 1,
            iterations: 100,
            exec: 'latencyScenario',
        },
        throughput_test: {
            executor: 'constant-arrival-rate',
            rate: 100,
            timeUnit: '1s',
            duration: '30s',
            preAllocatedVUs: 20,
            maxVUs: 50,
            exec: 'throughputScenario',
        },
        load_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '30s', target: 10 },
                { duration: '30s', target: 25 },
                { duration: '30s', target: 50 },
            ],
            exec: 'loadScenario',
        },
    },
};

// Overfetching helper
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

// Shared logic
function runCRUD() {
    let userId = null;
    let orderId = null;

    group('POST /users', () => {
        const payload = JSON.stringify({
            name: `TestUser_${__VU}_${__ITER}`,
            email: `user${Math.floor(Math.random() * 1000000)}@testrestapi.com`,
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
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    group('GET /users', () => {
        const res = http.get(`${BASE_URL}/users/`);
        const ok = check(res, { 'GET /users status 200': (r) => r.status === 200 });
        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

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
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'user_id', 'product_name', 'price']));
    });

    group('GET /orders/user/{user_id}', () => {
        if (userId === null) return;

        const res = http.get(`${BASE_URL}/orders/user/${userId}`);
        const ok = check(res, { 'GET /orders/user/{id} status 200': (r) => r.status === 200 });
        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
    });

    group('DELETE /orders/{order_id}', () => {
        if (orderId === null) return;

        const res = http.del(`${BASE_URL}/orders/${orderId}`);
        const ok = check(res, { 'DELETE /orders status 200': (r) => r.status === 200 });
        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
    });

    group('DELETE /users/{user_id}', () => {
        if (userId === null) return;

        const res = http.del(`${BASE_URL}/users/${userId}`);
        const ok = check(res, { 'DELETE /users status 200': (r) => r.status === 200 });
        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
    });
}

// Сценарии
export function latencyScenario() {
    runCRUD();
    sleep(1);
}

export function throughputScenario() {
    runCRUD();
    sleep(0.5);
}

export function loadScenario() {
    runCRUD();
    sleep(1);
}
