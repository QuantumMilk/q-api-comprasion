import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

export let latency = new Trend('graphql_latency');
export let throughput = new Counter('graphql_throughput');
export let errorRate = new Rate('graphql_errors');
export let overfetchBytes = new Trend('graphql_overfetching_bytes');

const BASE_URL = 'http://127.0.0.1:8080/graphql';

export let options = {
    vus: 20,
    duration: '30s',
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

export default function () {
    let userId = null;
    let orderId = null;

    // ➤ Create user
    group('GraphQL - createUser', () => {
        const query = `
            mutation {
                createUser(input: {name: "TestUser_${__VU}_${__ITER}", email: "user${Math.floor(Math.random() * 10000)}@test.com"}) {
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
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    // ➤ Get users
    group('GraphQL - users', () => {
        const query = `{ users { id name email } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'users query status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'name', 'email']));
    });

    // ➤ Create order
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
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'userId', 'productName', 'price']));
    });

    // ➤ Get all orders
    group('GraphQL - orders', () => {
        const query = `{ orders { id userId productName price } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'orders query status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'userId', 'productName', 'price']));
    });

    // ➤ Get orders by user
    group('GraphQL - ordersByUser', () => {
        if (!userId) return;

        const query = `{ ordersByUser(userId: ${userId}) { id productName price } }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'ordersByUser status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
        overfetchBytes.add(estimateOverfetch(res, ['id', 'productName', 'price']));
    });

    // ➤ Delete order
    group('GraphQL - deleteOrder', () => {
        if (!orderId) return;

        const query = `mutation { deleteOrder(id: ${orderId}) }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'deleteOrder status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
    });

    // ➤ Delete user
    group('GraphQL - deleteUser', () => {
        if (!userId) return;

        const query = `mutation { deleteUser(id: ${userId}) }`;
        const res = http.post(BASE_URL, JSON.stringify({ query }), { headers: { 'Content-Type': 'application/json' } });

        const ok = check(res, {
            'deleteUser status 200': (r) => r.status === 200,
        });

        latency.add(res.timings.duration);
        throughput.add(1);
        errorRate.add(!ok);
    });

    sleep(1);
}
