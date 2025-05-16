
import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

const client = new grpc.Client();
client.load(['/home/molokanovii/Документы/Science/Диплом/q-api-comprasion/grpc-api/app/protos'], 'service.proto');

// Метрики
const latency = new Trend('latency');
const throughput = new Counter('throughput');
const errorRate = new Rate('errors');

export const options = {
    vus: 20,
    duration: '30s',
};

export default () => {
    client.connect('127.0.0.1:50051', { plaintext: true });

    const user = {
        name: `TestUser_${__VU}_${__ITER}`,
        email: `user${Math.floor(Math.random() * 100000)}@test_grpc.com`,
    };

    const startCU = Date.now();
    const resCU = client.invoke('usersorders.UserService/CreateUser', user);
    const durCU = Date.now() - startCU;
    check(resCU, {
        'CreateUser status is OK': (r) => r && r.status === grpc.StatusOK,
        'user ID exists': (r) => r && r.message && r.message.id !== undefined,
    });
    latency.add(durCU);
    throughput.add(1);
    errorRate.add(!(resCU && resCU.status === grpc.StatusOK));
    const userId = resCU.message?.id;

    const resGU = client.invoke('usersorders.UserService/GetUsers', {});
    check(resGU, { 'GetUsers status is OK': (r) => r && r.status === grpc.StatusOK });
    latency.add(Date.now() - startCU);
    throughput.add(1);
    errorRate.add(!(resGU && resGU.status === grpc.StatusOK));

    if (userId) {
        const order = {
            user_id: userId,
            product_name: 'TestProduct',
            price: 99.99,
        };
        const startCO = Date.now();
        const resCO = client.invoke('usersorders.OrderService/CreateOrder', order);
        const durCO = Date.now() - startCO;
        check(resCO, {
            'CreateOrder status is OK': (r) => r && r.status === grpc.StatusOK,
            'order ID exists': (r) => r && r.message && r.message.id !== undefined,
        });
        latency.add(durCO);
        throughput.add(1);
        errorRate.add(!(resCO && resCO.status === grpc.StatusOK));
        const orderId = resCO.message?.id;

        const resGO = client.invoke('usersorders.OrderService/GetOrders', {});
        check(resGO, { 'GetOrders status is OK': (r) => r && r.status === grpc.StatusOK });
        latency.add(Date.now() - startCO);
        throughput.add(1);
        errorRate.add(!(resGO && resGO.status === grpc.StatusOK));

        const resGOBU = client.invoke('usersorders.OrderService/GetOrdersByUser', { id: userId });
        check(resGOBU, { 'GetOrdersByUser status is OK': (r) => r && r.status === grpc.StatusOK });
        latency.add(Date.now() - startCO);
        throughput.add(1);
        errorRate.add(!(resGOBU && resGOBU.status === grpc.StatusOK));

        if (orderId) {
            const resDO = client.invoke('usersorders.OrderService/DeleteOrder', { id: orderId });
            check(resDO, { 'DeleteOrder status is OK': (r) => r && r.status === grpc.StatusOK });
            latency.add(Date.now() - startCO);
            throughput.add(1);
            errorRate.add(!(resDO && resDO.status === grpc.StatusOK));
        }

        const resDU = client.invoke('usersorders.UserService/DeleteUser', { id: userId });
        check(resDU, { 'DeleteUser status is OK': (r) => r && r.status === grpc.StatusOK });
        latency.add(Date.now() - startCO);
        throughput.add(1);
        errorRate.add(!(resDU && resDU.status === grpc.StatusOK));
    }

    client.close();
    sleep(1);
};
