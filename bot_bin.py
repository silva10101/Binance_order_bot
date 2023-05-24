import random
import hashlib
import hmac
import json
import requests


API_KEY='lrCRmE1LHeNWXLVcqcwajX3j00zlxnzWDHmbmpBg27LWVyQYOPCNUjuGcIPRIXpw'
API_SECRET='YSlFV6fqP6ZDYrVuwgyTAUMRwHdD9NZISIHhKUTN0aPke5EJsQu41k3PAqmo6bKb'

BASE_URL = 'https://testnet.binance.vision/api/v3'

def get_full_params(params):
    """Получение подписи для корректной работы запросов"""
    query_string = '&'.join([f"{key}={params[key]}" for key in params])
    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    return params

def get_server_time():
    '''Функция для получения времени серверов BINANCE'''
    endpoint = '/time'
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        server_time = response.json()['serverTime']
    except requests.exceptions.RequestException as e:
        print(f"Failed to get server time: {e}")
        return None

    return str(server_time)

def split_volume(volume, number, amount_dif):
    '''
    Разбиваем общий объем на указанное 
    количество ордеров с учетом разброса объема
    '''

    min_volume = volume / number - amount_dif / 2
    max_volume = volume / number + amount_dif / 2
    order_volumes = [random.uniform(min_volume, max_volume) for _ in range(number-1)]
    dif = volume - sum(order_volumes)
    order_volumes.append(dif)
    order_volumes.sort()
    if order_volumes[-1] > max_volume:
        order_volumes[0] += order_volumes[-1]-max_volume
        order_volumes[-1]=max_volume
    return order_volumes

def get_symbol_info(symbol):
    '''получение информации о паре'''
    endpoint = "/exchangeInfo"
    params = {'symbol': symbol}

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        symbol = data["symbols"][0]
        price_filter = symbol['filters'][0]
        quantity_filter = symbol['filters'][1]
        output = (symbol["baseAssetPrecision"], 
                  symbol["quoteAssetPrecision"], 
                  symbol["quotePrecision"],
                  price_filter,
                  quantity_filter)
        return output
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to get info about symbol: {e}")

def create_order(symbol, side, price, quantity):
    '''
    Создает 1 ордер 
    '''

    endpoint = '/order'
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'price': str(price),
        'quantity': str(quantity),
        'timestamp': get_server_time()
    }
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    params = get_full_params(params)

    try:
        response = requests.post(f"{BASE_URL}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        order_info = response.json()
        print(f"Order created successfully: {params['symbol']},{params['side']},{params['price']}$,{params['quantity']}")
        return json.dumps(order_info, indent=4)
    except requests.exceptions.RequestException as e:
        print(f"Failed to create order: {e}")

def create_orders(balance, symbol, data):
    '''
    Создает ордера по заданным параметрам 
    объема, числа, паре, цене
    '''

    volume = data['volume']
    number = data['number']
    amount_dif = data['amountDif']
    side = data['side']
    price_min = data['priceMin']
    price_max = data['priceMax']
    order_quantitys = []

    # Получаем данные о паре
    precition = get_symbol_info(symbol)
    prisePR=precition[2]
    if side == 'BUY':
        quantityPR = precition[0]
    elif side == 'SELL':
        quantityPR = precition[1]
    prise_filter=precition[3]
    quantity_filter=precition[4]

    priseSTEP = float(prise_filter['tickSize'])
    quantitySTEP = float(quantity_filter['stepSize'])

    # Рассчитываем объем каждого ордера
    order_volumes = split_volume(volume, number, amount_dif)
    order_prices =  [round_to_step(random.uniform(price_min, price_max), priseSTEP, prisePR) for _ in range(number)]

    # Проверяем на соответствие цены требованиям
    if (min(order_prices)<float(prise_filter['minPrice']) or 
        max(order_prices)>float(prise_filter['maxPrice'])):
        return 'Error in order prices'
    # рассчитываем количество монет
    for i in range(number):
        order_quantitys.append(round_to_step(order_volumes[i]/order_prices[i], quantitySTEP, quantityPR))
    # проверяем количество на соотетсятвие требованиям
    if (min(order_quantitys)<float(quantity_filter['minQty']) or 
        max(order_quantitys)>float(quantity_filter['maxQty'])):
        return 'Error in order quantitys'   

    base, quote=split_currency_pair(symbol)
    needed_amount=0
    for i in range(number):
        needed_amount+=order_quantitys[i]/order_prices[i]
    
    if side == 'BUY':
        for i in balance:
            if i['asset'] == quote:
                if float(i['free']) < needed_amount:
                    return 'Not enough balance'
    elif side == 'SELL':
        for i in balance:
            if i['asset'] == base:
                if float(i['free']) < sum(order_quantitys):
                    return 'Not enough balance'

    # Создаем ордеры
    orders = []
    for i in range(number):
        order = create_order(symbol, side, order_prices[i], order_quantitys[i])
        if order:
            orders.append(order)
    return orders

def user_data():
    '''
    Выводит балансы по всем монетам
    '''

    endpoint = '/account'
    params = {
        'recvWindow': '10000',
        'timestamp': get_server_time()
    }

    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    params = get_full_params(params)

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print('===Баланс===')
        print('coin     free      locked')
        for balance in user_info['balances']:
            print(f'{balance["asset"]}\t{balance["free"]}\t{balance["locked"]}')
        print('='*20)
    except requests.exceptions.RequestException as e:
        print(f"Failed to get data: {e}")
    return user_info['balances']

def all_orders(symbol, number):
    '''
    Выводит список всех ордеров
    '''

    endpoint = '/allOrders'
    params = {
        'symbol': symbol,
        'startTime': str(int(get_server_time())-100000),
        'endTime': get_server_time(),
        'recvWindow': '10000',
        'timestamp': get_server_time()
    }
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    params = get_full_params(params)

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        orders_info = response.json()

        for order in orders_info:
            print(order['status'])
            print(f"symbol:{order['symbol']}, type:{order['type']}, side:{order['side']}"
                f"\nprice:{order['price']}$ - quantity:{order['origQty']}")
            print('-'*10)
            
    except requests.exceptions.RequestException as e:
        print(f"Failed to get orders: {e}")

def round_to_step(value, step, pr):
    '''приводит число к нудному формату'''
    rounded_value = round(value / step) * step
    rounded_value = round(rounded_value, pr)
    return rounded_value

def split_currency_pair(currency_pair):
    """
    Разделяет пару криптовалют на отдельные криптовалюты
    """
    currency_mappings = {
        'BTC': ['BTC'],
        'ETH': ['ETH'],
        'USDT': ['USDT'],
        'BNB': ['BNB'],
        'XRP': ['XRP'],
        # Добавьте другие криптовалюты и их символы
    }
    
    base_currency = ''
    quote_currency = ''
    
    for currency, symbols in currency_mappings.items():
        for symbol in symbols:
            if symbol in currency_pair:
                if not base_currency:
                    base_currency = currency
                else:
                    quote_currency = currency
                    break
    
    return base_currency, quote_currency

if __name__ == '__main__':
    # Пример использования функции create_orders
    symbol = 'ETHUSDT'
    data = {
        "volume": 26000,
        "number": 5,
        "amountDif": 5000,
        "side": "BUY",
        "priceMin": 1900,
        "priceMax": 1800
    }

    balance =user_data()
    result = create_orders(balance, symbol, data)
    if type(result)==str:
        print (result)
    elif type(result)==list:
        print(f"Created {len(result)} orders")
    all_orders(symbol, number=data['number'])


    symbol = 'ETHUSDT'
    data = {
        "volume": 20000,
        "number": 5,
        "amountDif": 5000,
        "side": "SELL",
        "priceMin": 1700,
        "priceMax": 1600
    }

    balance =user_data()
    result = create_orders(balance, symbol, data)
    if type(result)==str:
        print (result)
    elif type(result)==list:
        print(f"Created {len(result)} orders")
    all_orders(symbol, number=data['number'])



