import requests
import json
import time
import random
import json_manipulations
from os import environ
# TODO if using API you can only get lowest buy order price (from skins to cash)
# see example https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=34306
# TODO use this instead https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=33811
# TODO see in network page (GET - requests) try to ask server to get items instead of using selenium


def convert_to_RUB(currency_acronym_name):
    req_json = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency_acronym_name}").json()
    in_rub = req_json["rates"]["RUB"]
    return in_rub


def get_items_steam_API(API_key):
    req_json = requests.get(f"https://www.steamwebapi.com/steam/api/items?key={API_key}").json()
    json_manipulations.write_json(req_json, "steam_api.json")


def get_additional_data(item, wear):
    with open("steam_result.json", "r") as steam_json:
        data = json.load(steam_json)
        try:
            return data[item.lower()][wear]
        except:
            empty_data = {
                "skinname": None,
                "skin_wear": None,
                "pricelatest": None,
                "pricelatestsell": None,
                "priceupdatedat": None,
                "pricemin": None,
                "pricereal": None,
                "pricereal24h": None,
                "offervolume": None,
                "sold24h": None,
                "sold7d": None,
                "updatedat": None,
            }
            return empty_data


def get_wear_acronym(wear):
    line = ""
    if wear.lower() == "factory new":
        line = "fn"
    elif wear.lower() == "battle-scarred":
        line = "bs"
    elif wear.lower() == "minimal wear":
        line = "mw"
    elif wear.lower() == "field-tested":
        line = "ft"
    else:
        line = "ww"
    return line


def get_items():
    CNY_RUB_price = convert_to_RUB("CNY")  # without commision
    base_string = "https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id="
    item_id = 1
    dataset = {}
    with open("fixed_items.json") as jf:
        data = json.load(jf)  # 2690 items in there
        for name in data:
            time.sleep(random.random() + 0.5)  
            # without this at a 100 or so ids will get To Many Requests
            id = data[name]
            s = base_string + f"{id}"
            #extracting info from API on each and every weapon skin
            req = requests.get(s)
            req_weapon = req.json()
            if len(req_weapon["data"]["goods_infos"]) > 0:
                name_wear = req_weapon["data"]["goods_infos"][f"{id}"]["market_hash_name"]
                value = round(float(req_weapon["data"]["items"][0]["price"]) * CNY_RUB_price, 2)
                skin_name = name_wear.split(" (")[0] # wrong result on M4A4 | 龍王 (Dragon King) 
                wear = get_wear_acronym(name_wear.split(" (")[1][:-1])
                steam_price = float(req_weapon["data"]["goods_infos"][f"{id}"]["steam_price_cny"]) * CNY_RUB_price
            else:
                continue
            
            # "Helper" json
            wear_json = {}
            wear_json["price"] = value
            wear_json["steam_price"] = round(steam_price, 2)
            wear_json["buff163_id"] = id

            additional_data = get_additional_data(skin_name, wear)

            for item in additional_data:
                wear_json[item] = additional_data[item]

            if skin_name in dataset:
                dataset[skin_name][wear] = wear_json
            else:

                json_item = {"id": item_id, wear: wear_json}
                dataset[skin_name] = json_item
            item_id += 1
            print(item_id)
    return dataset


if __name__ == "__main__":
    # key = environ("steam_web_api_key")
    # get_items_steam_API(key)
    full_st = time.time()
    json_manipulations.write_json(get_items(), "result.json")
    full_et = time.time()
    full_time = full_et - full_st
    print("full exec time is = ", full_time)
