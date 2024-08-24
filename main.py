import requests
import json
import time
import random

# TODO if using API you can only get lowest buy order price (from skins to cash)
# see example https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=34306
# TODO use this instead https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=33811
# TODO see in network page (GET - requests) try to ask server to get items instead of using selenium



def convert_CNY_RUB():
    req_json = requests.get("https://api.exchangerate-api.com/v4/latest/CNY").json()
    CNY_TO_RUB = req_json["rates"]["RUB"]
    return CNY_TO_RUB

def save_items(items):
    with open("sample.json", "w") as outfile: 
        json.dump(items, outfile)


def get_items(number_of_items):
    CNY_RUB_price = convert_CNY_RUB() #without commision
    base_string = "https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id="
    item_id = 1
    dataset = {}
    with open("fixed_items.json") as jf:
        data = json.load(jf)
        quality_json_template = {
            "buff163_id": None,
            "price": None,
            "steam_price": None,
            "steam_trade_volume": None,
            "buff163_amount_of_sell_offers": None,
            "buff163_amount_of_buy_offers": None
        }
        for name in data:            
            time.sleep(random.random() + 0.5) # without this at a 100 or so ids will get To Many Requests
            id = data[name]
            s = base_string+f"{id}"
            req = requests.get(s)
            req_weapon = req.json()
            if len(req_weapon["data"]["goods_infos"]) > 0:
                name_quality = req_weapon["data"]["goods_infos"][f"{id}"]["market_hash_name"] # this should give eng name
                value = round(float(req_weapon["data"]["items"][0]["price"])*CNY_RUB_price, 2)
                skin_name = name_quality.split(' (')[0]
                quality = name_quality.split(' (')[1][:-1]
                steam_price = float(req_weapon["data"]["goods_infos"][f"{id}"]["steam_price_cny"])*CNY_RUB_price
            else:
                continue
            quality_json = {}
            quality_json["price"] = value
            quality_json["steam_price"] = round(steam_price, 2)
            quality_json["buff163_id"] = id
            #other field will be None till i find a way to fill them (or delete them)

            if skin_name in dataset:
                dataset[skin_name][quality] = quality_json
            else:

                json_item = {
                    "id" : item_id,
                    quality: quality_json
                }
                dataset[skin_name] = json_item
            
            item_id+=1
            if item_id > number_of_items:
                break
    save_items(dataset)

if __name__ == "__main__":
    full_st = time.time()
    get_items(300)
    full_et = time.time()
    full_time = full_et - full_st
    print("full exec time is = ", full_time)


