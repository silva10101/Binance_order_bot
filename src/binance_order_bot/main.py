from bot_binance import BotBinance

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
            bot=BotBinance(symbols[i], data)
            bot.prepare_for_orders()
            bot.create_orders()
