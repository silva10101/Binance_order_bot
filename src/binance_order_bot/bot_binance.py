import random
import json

from enum import Enum

from binance_order_bot.api_binance import ApiBinance
from binance_order_bot.config_reader import ConfigReader




class BotBinance:
    '''
    Класс для создания 
    нескольких ордеров различных
    по цене и объему
    '''
    def __init__(self, symbol, data):
        '''Класс для выставления ордеров'''

        cfg = ConfigReader().get_cfg()
        self.api = ApiBinance(*cfg)
        
        self.volume = data['volume']
        self.number = data['number']
        self.amount_dif = data['amountDif']
        self.side = data['side']
        self.price_min = data['priceMin']
        self.price_max = data['priceMax']

        self.symbol = symbol
        self.base = ''
        self.quote = ''

        self.status=[]


    class OrderSide(Enum):
        BUY = 'BUY'
        SELL = 'SELL'
    
    def prepare_for_orders(self):
        '''Подготавливает к созданию ордеров'''
        
        self.split_currency_pair()
        self.show_balance()
        self.show_symbol_info()
        self.create_price_quantitys()

        self.check_for_ussue()

        print(self.status)
        print(json.dumps(self.balances, indent=4))
        print(f'Prices:{self.order_prices}')
        print(f'Quant:{self.order_quantitys}')
        print(self.status[1])

        return self.status
    
    def show_balance(self):
        '''Сохраняет баланс по нужной паре'''
        
        user_info = self.api.get_user_data()
        if user_info:
            print('Получена информация о пользователе')
            self.balances = {}
            for balance in user_info['balances']:
                if (balance['asset'] == self.quote or 
                    balance['asset'] == self.base):
                    self.balances[balance['asset']] = {'free': balance['free'], 'locked': balance['locked']}
        else:
            self.status=(False, 'Нет информации о пользователе',)
            print('Нет информации о пользователе')

    def show_symbol_info(self):
        '''получение информации о паре'''
    
        data = self.api.get_symbol_info(symbol=self.symbol)
        if data:
            print('Получена о паре')
            symbol_info = data["symbols"][0]

            if self.side == self.OrderSide.BUY.value:
                self.quantityPR = symbol_info["baseAssetPrecision"]
            elif self.side == self.OrderSide.SELL.value:
                self.quantityPR = symbol_info["quoteAssetPrecision"]

            self.pricePR=symbol_info["quotePrecision"]

            self.price_filter = symbol_info['filters'][0]
            self.quantity_filter = symbol_info['filters'][1] 
        else:
            self.status=(False, 'Нет информации о паре',)
            print('Нет информации о паре')

    def create_order(self, price, quantity):
        '''Создает один ордер'''
        order_info = self.api.create_order(self.symbol,
                                           self.side,
                                           price,
                                           quantity)
        
        if order_info:
            print(f"Order created successfully: {self.symbol},{self.side},{price}$,{quantity}")
        return order_info

    def create_orders(self):
        '''Создает необходимое число ордеров'''

        self.orders=[]
        if self.status[0]:
            for i in range(self.number):
                order = self.create_order(self.order_prices[i], self.order_quantitys[i])
                if order:
                    self.orders.append(order)
        
        self.show_all_orders()
    
    def show_all_orders(self):
        '''
        Выводит список всех ордеров
        '''
    
        orders_info = self.api.get_all_orders(self.symbol)

        for order in orders_info:
            print(order['status'])
            print(f"symbol:{order['symbol']}, type:{order['type']}, side:{order['side']}"
                f"\nprice:{order['price']}$ - quantity:{order['origQty']}")
            print('-'*10)
    
    def split_volume(self):
        '''
        Разбиваем общий объем на указанное 
        количество ордеров с учетом разброса объема
        '''

        min_volume = self.volume / self.number - self.amount_dif / 2
        if min_volume < 0:
            min_volume = 0
        max_volume = self.volume / self.number + self.amount_dif / 2
        self.order_volumes = [random.uniform(min_volume, max_volume) for _ in range(self.number-1)]
        dif = self.volume - sum(self.order_volumes)
        self.order_volumes.append(dif)
        
        while min_volume>min(self.order_volumes) or max_volume < max(self.order_volumes):
            self.order_volumes.sort()
            if self.order_volumes[-1] > max_volume:
                self.order_volumes[0] += self.order_volumes[-1]-max_volume
                self.order_volumes[-1]=max_volume
            if self.order_volumes[0] < min_volume:
                self.order_volumes[-1] -= min_volume-self.order_volumes[0]
                self.order_volumes[0]=min_volume
        
        return self.order_volumes
    
    def create_price_quantitys(self):

        self.split_volume()
        priceSTEP = float(self.price_filter['tickSize'])
        quantitySTEP = float(self.quantity_filter['stepSize'])
        
        self.order_prices = [self.round_to_step(
            random.uniform(self.price_min, self.price_max), 
            priceSTEP, 
            self.pricePR) 
            for _ in range(self.number)]
        
        self.order_quantitys = [self.round_to_step(
            self.order_volumes[i]/self.order_prices[i], 
            quantitySTEP, 
            self.quantityPR)
            for i in range(self.number)]
        
        return self.order_prices, self.order_prices, self.order_quantitys
        
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
        
        return self.base, self.quote
    
    def check_for_ussue(self):
        '''Проверка данных'''
        msg = (True, 'Alright',)

            # Проверяем на соответствие цены требованиям
        if (min(self.order_prices)<float(self.price_filter['minPrice']) or 
            max(self.order_prices)>float(self.price_filter['maxPrice'])):
            msg = (False, 'Error in order prices',)

            # проверяем количество на соответствие требованиям
        elif (min(self.order_quantitys)<float(self.quantity_filter['minQty']) or 
            max(self.order_quantitys)>float(self.quantity_filter['maxQty'])):
            msg = (False,'Error in order quantitys',) 

            # проверяем количество средств на счету
        elif self.side == self.OrderSide.BUY.value:
            if float(self.balances[self.quote]['free'])< sum(self.order_quantitys):
                msg = (False, 'Not enough balance',)
        elif self.side == self.OrderSide.SELL.value:
            if float(self.balances[self.base]['free'])< sum(self.order_quantitys):
                msg = (False, 'Not enough balance',)
        elif self.status:
            return self.status
        
        self.status = msg
        
        return self.status
