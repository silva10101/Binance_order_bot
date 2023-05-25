import random
import hashlib
import hmac
import json
import requests


API_KEY=''
API_SECRET=''

BASE_URL = 'https://testnet.binance.vision/api/v3'



class Bot:
    def __init__(self, base_url, symbol, data):
        '''Класс для выставления ордеров'''

        self.base_url = base_url
        
        self.volume = data['volume']
        self.number = data['number']
        self.amount_dif = data['amountDif']
        self.side = data['side']
        self.price_min = data['priceMin']
        self.price_max = data['priceMax']

        self.symbol = symbol
        self.base = ''
        self.quote = ''
        self.split_currency_pair()
        self.user_data()
        self.get_symbol_info()

        self.split_volume()
        priseSTEP = float(self.price_filter['tickSize'])
        quantitySTEP = float(self.quantity_filter['stepSize'])
        
        self.order_prices = [self.round_to_step(
            random.uniform(self.price_min, self.price_max), 
            priseSTEP, 
            self.prisePR) 
            for _ in range(self.number)]
        self.order_quantitys = [self.round_to_step(
            self.order_volumes[i]/self.order_prices[i], 
            quantitySTEP, 
            self.quantityPR)
            for i in range(self.number)]
        
        status = self.check_for_ussue()

        print(json.dumps(self.balances, indent=4))
        print(f'Prices:{self.order_prices}')
        print(f'Quant:{self.order_quantitys}')
        print(status[1])

        self.orders = []
        if status[0]:
            self.create_orders()
        
        self.all_orders()
        
    def get_full_params(self, params):
        '''Получение подписи для корректной работы запросов'''
        query_string = '&'.join([f"{key}={params[key]}" for key in params])
        signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params

    def get_server_time(self):
        '''Функция для получения времени серверов BINANCE'''
        endpoint = '/time'
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            server_time = response.json()['serverTime']
            return str(server_time)
        except requests.exceptions.RequestException as e:
            print(f"Failed to get server time: {e}")
            return None

    def user_data(self):
        '''Сохраняет баланс по нужной паре'''
        endpoint = '/account'
        params = {
            'recvWindow': '10000',
            'timestamp': self.get_server_time()
        }
        headers = {
            'X-MBX-APIKEY': API_KEY
        }
        params = self.get_full_params(params)

        try:
            response = requests.get(f"{self.base_url}{endpoint}", 
                                    params=params, 
                                    headers=headers)
            response.raise_for_status()
            user_info = response.json()

            self.balances = {}
            for balance in user_info['balances']:
                if (balance['asset'] == self.quote or 
                    balance['asset'] == self.base):
                    self.balances[balance['asset']] = {'free': balance['free'], 'locked': balance['locked']}

        except requests.exceptions.RequestException as e:
            print(f"Failed to get data: {e}")

    def get_symbol_info(self):
        '''получение информации о паре'''
        endpoint = "/exchangeInfo"
        params = {'symbol': self.symbol}
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()

            symbol_info = data["symbols"][0]

            if self.side == 'BUY':
                self.quantityPR = symbol_info["baseAssetPrecision"]
            elif self.side == 'SELL':
                self.quantityPR = symbol_info["quoteAssetPrecision"]

            self.prisePR=symbol_info["quotePrecision"]

            self.price_filter = symbol_info['filters'][0]
            self.quantity_filter = symbol_info['filters'][1] 

        except requests.exceptions.RequestException as e:
            print(f"Failed to get info about symbol: {e}")

    def split_volume(self):
        '''
        Разбиваем общий объем на указанное 
        количество ордеров с учетом разброса объема
        '''

        min_volume = self.volume / self.number - self.amount_dif / 2
        max_volume = self.volume / self.number + self.amount_dif / 2
        self.order_volumes = [random.uniform(min_volume, max_volume) for _ in range(self.number-1)]
        dif = self.volume - sum(self.order_volumes)
        self.order_volumes.append(dif)
        self.order_volumes.sort()
        if self.order_volumes[-1] > max_volume:
            self.order_volumes[0] += self.order_volumes[-1]-max_volume
            self.order_volumes[-1]=max_volume

    def round_to_step(self, value, step, pr):
        '''приводит число к нужному формату'''
        rounded_value = round(value / step) * step
        rounded_value = round(rounded_value, pr)
        return rounded_value

    def split_currency_pair(self):
        """
        Разделяет пару криптовалют на отдельные криптовалюты
        """
        currency_mappings = {
            'BTC': ['BTC'],
            'ETH': ['ETH'],
            'USDT': ['USDT'],
            'BNB': ['BNB'],
            'XRP': ['XRP'],
            'BUSD': ['BUSD'],
            'TRX': ['TRX'],
            # Добавьте другие криптовалюты и их символы
        }
        for currency, symbols in currency_mappings.items():
            for symbol in symbols:
                if symbol in self.symbol:
                    if not self.base:
                        self.base = currency
                    else:
                        self.quote = currency
                        break
    
    def check_for_ussue(self):
        '''Проверка данных'''
            # Проверяем на соответствие цены требованиям
        msg=(True, 'Allright',)
        if (min(self.order_prices)<float(self.price_filter['minPrice']) or 
            max(self.order_prices)>float(self.price_filter['maxPrice'])):
            msg = (False, 'Error in order prices',)
            # проверяем количество на соотетсятвие требованиям
        elif (min(self.order_quantitys)<float(self.quantity_filter['minQty']) or 
            max(self.order_quantitys)>float(self.quantity_filter['maxQty'])):
            msg = (False,'Error in order quantitys',) 
            # проверяем количество средств на счету
        elif self.side == 'BUY':
            if float(self.balances[self.quote]['free'])< sum(self.order_quantitys):
                msg = (False, 'Not enough balance',)
        elif self.side == 'SELL':
            if float(self.balances[self.base]['free'])< sum(self.order_quantitys):
                msg = (False, 'Not enough balance',)
        return msg

    def create_order(self, price, quantity):
        '''Создает один ордер'''
        endpoint = '/order'
        params = {
            'symbol': self.symbol,
            'side': self.side,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'price': str(price),
            'quantity': str(quantity),
            'timestamp': self.get_server_time()
        }
        headers = {
            'X-MBX-APIKEY': API_KEY
        }
        params = self.get_full_params(params)

        try:
            response = requests.post(f"{self.base_url}{endpoint}", 
                                     params=params, 
                                     headers=headers)
            response.raise_for_status()
            order_info = response.json()

            print(f"Order created successfully: {params['symbol']},{params['side']},{params['price']}$,{params['quantity']}")
            return order_info
        except requests.exceptions.RequestException as e:
            print(f"Failed to create order: {e}")

    def create_orders(self):
        '''Создает необходимое число ордеров'''
        for i in range(self.number):
            order = self.create_order(self.order_prices[i], self.order_quantitys[i])
            if order:
                self.orders.append(order)

    def all_orders(self):
        '''
        Выводит список всех ордеров за последнюю минуту
        '''
        time = self.get_server_time()
        endpoint = '/allOrders'
        params = {
            'symbol': self.symbol,
            'startTime': str(int(time)-60000),
            'endTime': time,
            'recvWindow': '10000',
            'timestamp': time
        }
        headers = {
            'X-MBX-APIKEY': API_KEY
        }
        params = self.get_full_params(params)

        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
            response.raise_for_status()
            orders_info = response.json()

            for order in orders_info:
                print(order['status'])
                print(f"symbol:{order['symbol']}, type:{order['type']}, side:{order['side']}"
                    f"\nprice:{order['price']}$ - quantity:{order['origQty']}")
                print('-'*10)
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to get orders: {e}")



symbols = ('ETHUSDT', 'TRXUSDT',)
datasets =[
    ({
    "volume": 20000,"number": 5,"amountDif": 5000,
    "side": "BUY","priceMin": 1700,"priceMax": 1800
    },
    {
    "volume": 20000,"number": 5,"amountDif": 5000,
    "side": "SELL","priceMin": 1500,"priceMax": 1700
    },
    {
    "volume": 1000,"number": 2,"amountDif": 200,
    "side": "BUY","priceMin": 1700,"priceMax": 1800
    },
    {
    "volume": 1000,"number": 2,"amountDif": 200,
    "side": "SELL","priceMin": 1500,"priceMax": 1700
    },),
    ({
    "volume": 20000,"number": 20,"amountDif": 1000,
    "side": "BUY","priceMin": 0.06,"priceMax": 0.0768
    },
    {
    "volume": 20000,"number": 20,"amountDif": 1000,
    "side": "SELL","priceMin": 0.0768,"priceMax": 0.08
    },
    {
    "volume": 10,"number": 5,"amountDif": 200,
    "side": "BUY","priceMin": 0.06,"priceMax": 0.0768
    },
    {
    "volume": 10,"number": 5,"amountDif": 200,
    "side": "SELL","priceMin": 0.0768,"priceMax": 0.08
    },)]

if __name__ =='__main__':
    for i in range(len(symbols)):
        for data in datasets[i]:
            Bot(BASE_URL, symbols[i], data)
