import requests
import hashlib
import hmac, time

API_KEY='YzTSY98VZK92Fi2IgsbqMJ8Oq2hMVpeTVgeUebbBFUNrBsBLVh1NdUmHNbV6V0sn'
API_SECRET='d0g9yy4XZnjOcSBWfWcHFywmqIWNwXJqdpXjhoeLGwetAUo3LSPtMhcX5TSynf7c'


def cancel_all_orders():
    url = 'https://testnet.binance.vision/api/v3/openOrders'
    symbol = 'ETHUSDT'  # Торговая пара для отмены ордеров

    params = {
        'symbol': symbol,
        'recvWindow': '60000',
        'timestamp': int(time.time() * 1000)
    }
    params['signature'] = generate_signature(params, API_SECRET)
    headers = {
        'X-MBX-APIKEY': API_KEY 
    }

    try:
        response = requests.delete(url, params=params, headers=headers)
        response.raise_for_status()
        print("All orders have been successfully canceled.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to cancel orders: {e}")

def generate_signature(params, secret_key):
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    return hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

cancel_all_orders()
