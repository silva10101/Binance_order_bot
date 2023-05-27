import json
from pathlib import Path

class ConfigReader():

    def __init__(self):
        try:
            p = Path(__file__).with_name('config.json')
            with open(p) as config_file:
                config = json.load(config_file)

            self.url = config['API']['url']
            self.key = config['API']['api_key']
            self.secret = config['API']['api_secret']
            print('Ключи получены')

        except Exception as e:
            print(f'Не удалось открыть файл конфига: {e}')
    
    def get_cfg(self):
        return (self.url, self.key, self.secret,)
        
