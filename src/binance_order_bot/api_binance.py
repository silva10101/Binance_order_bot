import hashlib
import hmac
import requests
from enum import Enum



class ApiBinance():
    '''Класс для работы с API Binance'''
    def __init__(self, url, key, secret):
        self.url = url
        self.key = key
        self.secret = secret
        
    class RequestType(Enum):
        GET = 'GET'
        POST = 'POST'
        DELETE = 'DELETE'

    def get_full_params(self, params):
        '''Получение подписи для корректной работы запросов'''
        query_string = '&'.join([f"{key}={params[key]}" for key in params])
        signature = hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params        

    def obtain_response(self, type, endpoint, params=None, headers=None):
        '''Функция для get запроса'''

        try:
            if type == self.RequestType.GET.value:
                response = requests.get(f"{self.url}{endpoint}",  
                                    params=params, 
                                    headers=headers)
            elif type == self.RequestType.POST.value:
                response = requests.post(f"{self.url}{endpoint}", 
                                     params=params, 
                                     headers=headers)
            elif type == self.RequestType.DELETE.value:
                response = requests.delete(f"{self.url}{endpoint}", 
                                     params=params, 
                                     headers=headers)

            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to {type} {endpoint}: {e}")
            return None
        
    def get_server_time(self):
        '''Функция для получения времени серверов BINANCE'''
        endpoint = '/time'

        server_time = self.obtain_response('GET', endpoint=endpoint)

        return server_time['serverTime']
            
    def get_user_data(self):
        '''Запрашивает данные о пользователе'''
        endpoint = '/account'
        params = {
            'recvWindow': '10000',
            'timestamp': self.get_server_time()
        }
        headers = {
            'X-MBX-APIKEY': self.key
        }
        params = self.get_full_params(params)

        user_info = self.obtain_response('GET', endpoint=endpoint,
                                            params=params,
                                            headers=headers)

        return user_info

    def get_symbol_info(self, symbol):
        '''получение информации о паре'''
        endpoint = "/exchangeInfo"
        params = {
            'symbol': symbol
            }
        headers = {
            'X-MBX-APIKEY': self.key
        }

        data  = self.obtain_response('GET', endpoint=endpoint,
                                            params=params,
                                            headers=headers)
        return data
    
    def get_all_orders(self, symbol):
        '''
        Выводит список всех ордеров за последнюю минуту
        '''
        time = self.get_server_time()
        endpoint = '/allOrders'
        params = {
            'symbol': symbol,
            'startTime': str(int(time)-60000),
            'endTime': time,
            'recvWindow': '10000',
            'timestamp': time
        }
        headers = {
            'X-MBX-APIKEY': self.key
        }
        params = self.get_full_params(params)

        orders_info  = self.obtain_response('GET', endpoint=endpoint,
                                            params=params,
                                            headers=headers)
        return orders_info

    def create_order(self, symbol, side, price, quantity):
        '''Создает один ордер и отправляет данные о нём'''
        endpoint = '/order'
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'price': price,
            'quantity': quantity,
            'timestamp': self.get_server_time()
        }
        headers = {
            'X-MBX-APIKEY': self.key
        }
        params = self.get_full_params(params)

        order_info = self.obtain_response('POST', endpoint=endpoint,
                                            params=params,
                                            headers=headers)
        return order_info
    
    def delete_orders(self, symbol):
        '''Удаляет все ордеры определенной пары'''
        endpoint = '/openOrders'
        params = {
            'symbol': symbol,
            'recvWindow': '60000',
            'timestamp': self.get_server_time()
        }
        headers = {
            'X-MBX-APIKEY': self.key
        }
        params = self.get_full_params(params)
        
        order_info = self.obtain_response('DELETE', endpoint=endpoint,
                                            params=params,
                                            headers=headers)
        return order_info