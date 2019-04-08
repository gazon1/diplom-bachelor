import logging
import requests
from darksky import forecast
import datetime
from datetime import datetime as dt
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
import os
import json


CURRENT_DIR = '.'#'tmp/diplom/'


def to_date_from_unix_time(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S')

def get_logger():
    logger = logging.getLogger(__name__)

    # Create handlers
    f_handler = logging.FileHandler(os.path.join(CURRENT_DIR, 'logs.log'), 'a')
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    return logger


def get_keys():
    keys = []
    keys_file = 'keys.txt'
    with open(keys_file, 'r') as f:
        for line in f.read().splitlines():
            keys.append(line)

    keys = {key: False for key in keys if isinstance(key, str)}
    
    return keys

def get_cities():
    cities = [
       ('Oxford',51.7517,-1.2553),
        ('Exeter',50.7184,-3.5339),
        ('Truro',50.2632,-5.051),
        ('Carmarthen',51.8576,-4.3121),
        ('Norwich',52.6309,1.2974),
        ('Brighton And Hove',50.8225,-0.1372),
        ('Bristol',51.44999778,-2.583315472),
        ('Durham',54.7753,-1.5849),
        ('Llanidloes',52.4135,-3.5883),
        ('Penrith',54.6641,-2.7527),
        ('Jedburgh',55.4777,-2.5549),
        ('Coventry',52.42040367,-1.499996583),
        ('Edinburgh',55.94832786,-3.219090618),
        ('Cambridge',52.2053,0.1218),
        ('Glasgow',55.87440472,-4.250707236),
        ('Kingston upon Hull',53.7457,-0.3367),
        ('Leeds',53.83000755,-1.580017539),
        ('London',51.49999473,-0.116721844),
        ('Manchester',53.50041526,-2.247987103),
        ('Nottingham',52.97034426,-1.170016725),
        ('Aberdeen',57.1497,-2.0943),
        ('Fort Augustus',57.1448,-4.6805),
        ('Lairg',58.197,-4.6173),
        ('Oxford',51.7517,-1.2553),
    #     ('Inverey',56.9855,-3.5055),
        ('Shrewsbury',52.7069,-2.7527),
        ('Colwyn Bay',53.2932,-3.7276),
        ('Newton Stewart',54.9186,-4.5918),    
        ('Portsmouth',50.80034751,-1.080022218)]
    return cities

#TODO писать в фалй название города, которого не удалось полностью закачать


columns = ["temperature", "windSpeed", "cloudCover", "humidity", "visibility", "icon",
               "apparentTemperature", "summary", "dewPoint"]

if __name__ == "__main__":

    keys = get_keys()
    logger = get_logger()
    cities = get_cities()

    cities = [city for city in cities if str(city[0]) + ".csv" not in os.listdir(os.path.join(CURRENT_DIR, "diplom_data/"))] 
    keys = {key: value for key, value in keys.items() if value == False}

    base = dt(2017, 1, 1, hour=0)
    date_list = [base + datetime.timedelta(days=x) for x in range(0, 730)]
    date_list = [t.isoformat() for t in date_list]

    for city, key in zip(cities[: len(keys)], keys.keys()): 
        df = pd.DataFrame()
        logger.info(f"Скачиваю данные с города {city[0]}")
        for date in tqdm(date_list):
            try:
                _city = forecast(key, city[1], city[2], time=date)
                error = False
            except requests.exceptions.HTTPError as e:
                error = True
                logger.error(str(e.request) + str(e.response) + str(e))
                break
            except Exception as e:
                error = True
                logger.error(str(e))
                break
            try:
                for i in range(len(_city.hourly)):
                    values = [to_date_from_unix_time(_city.hourly[i]['time'])]
                    for column in columns:
                        try:
                            values.append(_city.hourly[i][column])
                        except KeyError as e:
                            values.append(None)
                    t = pd.DataFrame(values).T

                    df = pd.concat((df ,t))
            except AttributeError as e:
                logger.error(str(e))
                error =True

        if df.shape[0] > 0:
            df.columns = ["time"] + columns
            df = df.set_index("time")
            df.to_csv(os.path.join(CURRENT_DIR, "diplom_data/" + str(city[0]) + ".csv"), index=True)

        keys[key] = True #key is used, dont use it again today


    with open(os.path.join(CURRENT_DIR, 'file.txt'), 'w') as file:
         file.write(json.dumps(keys))    
