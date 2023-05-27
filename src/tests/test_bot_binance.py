import pytest

from binance_order_bot.bot_binance import BotBinance

class TestBotBinance:
    @pytest.mark.parametrize("symbol, data, expected", [
    ('ETHUSDT', {"volume": 20000,"number": 5,"amountDif": 3000,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 20000),      
    ('ETHUSDT', {"volume": 40000,"number": 20,"amountDif": 2000,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 40000),      
    ('ETHUSDT', {"volume": 200,"number": 2,"amountDif": 50,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 200),
    ('ETHUSDT', {"volume": 80000,"number": 1000,"amountDif": 35,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 80000),     
    ('ETHUSDT', {"volume": 150,"number": 15,"amountDif": 15,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 150),     
    ('ETHUSDT', {"volume": 2000000,"number": 40,"amountDif": 50000,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 2000000),     
    ('ETHUSDT', {"volume": 4500,"number": 2,"amountDif": 1500,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 4500),     
    ('ETHUSDT', {"volume": 100,"number": 8,"amountDif": 50,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 100),     
    ('ETHUSDT', {"volume": 2000,"number": 3,"amountDif": 750,"side": "BUY","priceMin": 1700,"priceMax": 1800}, 2000),     

])
    def test_split_volume_sum(self, symbol, data, expected):
        bot=BotBinance(symbol=symbol, data=data)
        result = bot.split_volume()
        assert round(sum(result),8) == expected

    @pytest.mark.parametrize("symbol, data", [
    ('ETHUSDT', {"volume": 20000,"number": 5,"amountDif": 3000,"side": "BUY","priceMin": 1700,"priceMax": 1800},),      
    ('ETHUSDT', {"volume": 40000,"number": 20,"amountDif": 1000,"side": "BUY","priceMin": 1700,"priceMax": 1800},),      
    ('ETHUSDT', {"volume": 200,"number": 2,"amountDif": 50,"side": "BUY","priceMin": 1700,"priceMax": 1800},),  
    ('ETHUSDT', {"volume": 80000,"number": 1000,"amountDif": 35,"side": "BUY","priceMin": 1700,"priceMax": 1800}, ),     
    ('ETHUSDT', {"volume": 150,"number": 15,"amountDif": 15,"side": "BUY","priceMin": 1700,"priceMax": 1800}, ),     
    ('ETHUSDT', {"volume": 2000000,"number": 40,"amountDif": 50000,"side": "BUY","priceMin": 1700,"priceMax": 1800}, ),     
    ('ETHUSDT', {"volume": 4500,"number": 2,"amountDif": 1500,"side": "BUY","priceMin": 1700,"priceMax": 1800},),     
    ('ETHUSDT', {"volume": 100,"number": 8,"amountDif": 50,"side": "BUY","priceMin": 1700,"priceMax": 1800}, ),     
    ('ETHUSDT', {"volume": 2000,"number": 3,"amountDif": 750,"side": "BUY","priceMin": 1700,"priceMax": 1800}, ),    
])  
    def test_split_volume_maxmin(self, symbol, data):
        bot=BotBinance(symbol=symbol, data=data)
        result = bot.split_volume()
        min=float(data['volume'])/float(data["number"])-float(data["amountDif"])/2
        max=float(data['volume'])/float(data["number"])+float(data["amountDif"])/2
        for i in result:
            assert min<=i<=max

    



    





#         symbols = ('ETHUSDT', 'TRXUSDT',)
# datasets =[
#     ({"volume": 20000,"number": 5,"amountDif": 5000,"side": "BUY","priceMin": 1700,"priceMax": 1800},
#     {
#     "volume": 20000,"number": 5,"amountDif": 5000,
#     "side": "SELL","priceMin": 1500,"priceMax": 1700
#     },
#     {
#     "volume": 1000,"number": 2,"amountDif": 200,
#     "side": "BUY","priceMin": 1700,"priceMax": 1800
#     },
#     {
#     "volume": 1000,"number": 2,"amountDif": 200,
#     "side": "SELL","priceMin": 1500,"priceMax": 1700
#     },),
#     ({
#     "volume": 20000,"number": 20,"amountDif": 1000,
#     "side": "BUY","priceMin": 0.06,"priceMax": 0.0768
#     },
#     {
#     "volume": 20000,"number": 20,"amountDif": 1000,
#     "side": "SELL","priceMin": 0.0768,"priceMax": 0.08
#     },
#     {
#     "volume": 10,"number": 5,"amountDif": 200,
#     "side": "BUY","priceMin": 0.06,"priceMax": 0.0768
#     },
#     {
#     "volume": 10,"number": 5,"amountDif": 200,
#     "side": "SELL","priceMin": 0.0768,"priceMax": 0.08
#     },)]
