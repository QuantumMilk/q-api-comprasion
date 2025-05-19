import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

export let latency = new Trend('graphql_latency', true);
export let ttfb = new Trend('graphql_ttfb', true);
export let throughput = new Counter('graphql_throughput');
export let errorRate = new Rate('graphql_errors');
export let overfetchBytes = new Trend('graphql_overfetching_bytes');

const BASE_URL = 'http://127.0.0.1:8080/graphql';

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

function estimateOverfetch(response, expectedKeys) {
    try {
        const json = response.json();
        const fullLength = JSON.stringify(json).length;
        const data = json.data;
        const slimLength = JSON.stringify(data, (k, v) => (expectedKeys.includes(k) ? v : undefined)).length;
        return fullLength - slimLength;
    } catch (_) {
        return 0;
    }
}

function runGraphQL() {
    let userId = null;
    let orderId = null;

    group('GraphQL - createUser', () => {
        const query = `
            mutation {
                createUser(input: {name: "TestUser_${__VU}_${__ITER}", email: "user${Math.floor(Math.random() * 1000000)}@testgraphql.com"}) {
                    id
                    name
                    email
                }
            }
        `;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'createUser status 200': (r) => r.status === 200,
            'user ID exists': (r) => r.json().data?.createUser?.id !== undefined,
        });

        if (ok) userId = res.json().data.createUser.id;

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    group('GraphQL - users', () => {
        const query = `{ users { id name email } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, { 'users query status 200': (r) => r.status === 200 });

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    group('GraphQL - createOrder', () => {
        if (!userId) return;

        const query = `
            mutation {
                createOrder(input: {userId: ${userId}, productName: "TestProduct", price: 99.99}) {
                    id
                    productName
                    price
                    userId
                }
            }
        `;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'createOrder status 200': (r) => r.status === 200,
            'order ID exists': (r) => r.json().data?.createOrder?.id !== undefined,
        });

        if (ok) orderId = res.json().data.createOrder.id;

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'userId', 'productName', 'price']));
    });

    group('GraphQL - orders', () => {
        const query = `{ orders { id userId productName price } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, { 'orders query status 200': (r) => r.status === 200 });

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'userId', 'productName', 'price']));
    });

    group('GraphQL - ordersByUser', () => {
        if (!userId) return;

        const query = `{ ordersByUser(userId: ${userId}) { id productName price } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, { 'ordersByUser status 200': (r) => r.status === 200 });

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'productName', 'price']));
    });

    group('GraphQL - deleteOrder', () => {
        if (!orderId) return;

        const query = `mutation { deleteOrder(id: ${orderId}) }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, { 'deleteOrder status 200': (r) => r.status === 200 });

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
    });

    group('GraphQL - deleteUser', () => {
        if (!userId) return;

        const query = `mutation { deleteUser(id: ${userId}) }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, { 'deleteUser status 200': (r) => r.status === 200 });

        latency.add(res.timings.duration);
        ttfb.add(res.timings.waiting);
        throughput.add(1);
        errorRate.add(!ok);
    });
}

// 👇 Тестовые сценарии
export function latencyScenario() {
    runGraphQL();
    sleep(1);
}

export function throughputScenario() {
    runGraphQL();
    sleep(0.5);
}

export function loadScenario() {
    runGraphQL();
    sleep(1);
}
