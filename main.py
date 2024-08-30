import json
import time
import random
import mysql.connector
import datetime
import os
from requests import get


def convert_to_RUB(currency_acronym_name):
    req_json = get(
        f"https://api.exchangerate-api.com/v4/latest/{currency_acronym_name}"
    ).json()
    in_rub = req_json["rates"]["RUB"]
    return in_rub


def make_requests(link):
    req_json = None
    base_time = random.random() + 0.7
    while req_json is None:
        time.sleep(base_time)
        req = get(link)
        req_json = req.json()
        if req_json is None:
            print(f"Empty link {link}")
    return req_json


def sql_query(db, cursor, vals):
    # vals will be all columns in table exept id
    find_query = f"SELECT ID FROM items WHERE skin_name = '{vals[0]}' AND skin_wear = '{vals[1]}'"
    cursor.execute(find_query)
    res = cursor.fetchall()
    if len(res) == 0:
        query = "INSERT INTO items (skin_name, skin_wear, buff163_price, steam_real_price, date_time) VALUES (%s, %s, %s, %s, %s)"
        val = (vals[0], vals[1], vals[2], vals[3], vals[4])
        # print(f"id not found: {vals[0]} {vals[1]} {vals[2]} {vals[3]} {vals[4]}")
    else:
        # res[0] has value of (1,)
        query = "REPLACE INTO items (id, skin_name, skin_wear, buff163_price, steam_real_price, date_time) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (res[0][0], vals[0], vals[1], vals[2], vals[3], vals[4])
        # print(f"id found: {myresult[0][0]} {vals[0]} {vals[1]} {vals[2]} {vals[3]} {vals[4]}")
    cursor.execute(query, val)
    db.commit()


def get_items():
    db = mysql.connector.connect(
        host = os.environ.get("HOST"),
        database = os.environ.get("MYSQL_DATABASE"),
        user = os.environ.get("MYSQL_USER"),
        password = os.environ.get("MYSQL_PASSWORD"),
        port = os.environ.get("MYSQL_PORT"),
    )
    mycursor = db.cursor()

    steam_price_fees_mult = 0.86956521739
    CNY_price = convert_to_RUB("CNY") * 1.02 # with commision

    base_link = "https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id="
    item_id = 1
    with open("finally_fixed_items.json") as jf:
        data = json.load(jf)
        for name in data:
            id = data[name]
            s = base_link + f"{id}"
            # extracting info from API on each and every weapon skin
            req = make_requests(s)
            if len(req["data"]["goods_infos"]) > 0:
                name_wear = req["data"]["goods_infos"][f"{id}"]["market_hash_name"]
                value = round(float(req["data"]["items"][0]["price"]) * CNY_price, 2)
                # find index of last opening ( so skins with multiple ( in it will parse correctly
                # FE this skin M4A4 | 龍王 (Dragon King) (Well-Worn)
                index_of_last_parentesis = name_wear.rfind("(")
                skin_name = name_wear[:index_of_last_parentesis]
                wear = name_wear[index_of_last_parentesis + 1 : -1]
                steam_price = (
                    float(req["data"]["goods_infos"][f"{id}"]["steam_price_cny"])
                    * CNY_price
                )

            if round(steam_price * steam_price_fees_mult, 2) <= value or "'" in name:
                # If somehow buy - sell will be non-profit
                # "'" exluded to not break sql query
                continue

            t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_query(db, mycursor, [skin_name, wear, value, steam_price, t])
            print(mycursor.rowcount, "rows affected. unique_item = ", item_id)
            item_id += 1
        print("end")


if __name__ == "__main__":
    # make it loop
    get_items()
