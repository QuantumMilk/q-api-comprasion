import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

const client = new grpc.Client();
client.load(
    ['/home/molokanovii/Документы/Science/Диплом/q-api-comprasion/grpc-api/app/protos'],
    'service.proto'
);

// Метрики
const latency = new Trend('grpc_latency', true);
const throughput = new Counter('grpc_throughput');
const errorRate = new Rate('grpc_errors');

export const options = {
    insecureSkipTLSVerify: true,
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

function runGRPC() {
    client.connect('127.0.0.1:50052');

    const user = {
        name: `TestUser_${__VU}_${__ITER}`,
        email: `user${Math.floor(Math.random() * 1000000)}@testgrpcssl.com`,
    };

    const t0 = Date.now();
    const resCU = client.invoke('usersorders.UserService/CreateUser', user);
    const t1 = Date.now();
    check(resCU, {
        'CreateUser OK': (r) => r && r.status === grpc.StatusOK,
        'user ID exists': (r) => r?.message?.id !== undefined,
    });
    latency.add(t1 - t0);
    throughput.add(1);
    errorRate.add(!(resCU && resCU.status === grpc.StatusOK));
    const userId = resCU.message?.id;

    const resGU = client.invoke('usersorders.UserService/GetUsers', {});
    latency.add(Date.now() - t1);
    throughput.add(1);
    errorRate.add(!(resGU && resGU.status === grpc.StatusOK));

    let orderId = null;
    if (userId) {
        const order = {
            user_id: userId,
            product_name: 'TestProduct',
            price: 99.99,
        };

        const t2 = Date.now();
        const resCO = client.invoke('usersorders.OrderService/CreateOrder', order);
        const t3 = Date.now();
        check(resCO, {
            'CreateOrder OK': (r) => r && r.status === grpc.StatusOK,
            'order ID exists': (r) => r?.message?.id !== undefined,
        });
        latency.add(t3 - t2);
        throughput.add(1);
        errorRate.add(!(resCO && resCO.status === grpc.StatusOK));
        orderId = resCO.message?.id;

        const resGO = client.invoke('usersorders.OrderService/GetOrders', {});
        latency.add(Date.now() - t3);
        throughput.add(1);
        errorRate.add(!(resGO && resGO.status === grpc.StatusOK));

        const resGOBU = client.invoke('usersorders.OrderService/GetOrdersByUser', { id: userId });
        latency.add(Date.now() - t3);
        throughput.add(1);
        errorRate.add(!(resGOBU && resGOBU.status === grpc.StatusOK));

        if (orderId) {
            const t4 = Date.now();
            const resDO = client.invoke('usersorders.OrderService/DeleteOrder', { id: orderId });
            latency.add(Date.now() - t4);
            throughput.add(1);
            errorRate.add(!(resDO && resDO.status === grpc.StatusOK));
        }

        const t5 = Date.now();
        const resDU = client.invoke('usersorders.UserService/DeleteUser', { id: userId });
        latency.add(Date.now() - t5);
        throughput.add(1);
        errorRate.add(!(resDU && resDU.status === grpc.StatusOK));
    }

    client.close();
}

// 👇 Сценарии как в REST и GraphQL
export function latencyScenario() {
    runGRPC();
    sleep(1);
}

export function throughputScenario() {
    runGRPC();
    sleep(0.5);
}

export function loadScenario() {
    runGRPC();
    sleep(1);
}
